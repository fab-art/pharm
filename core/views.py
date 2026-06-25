import base64
import io
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import VoucherUploadForm
from .utils import load_and_process, hbar_chart_buf, time_series_chart_buf, rapid_histogram_buf, ACCENT, ACCENT2

def buffer_to_base64(buf):
    if not buf:
        return None
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def upload_view(request):
    if request.method == 'POST':
        form = VoucherUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name
            rapid_days = form.cleaned_data['rapid_days']

            # Pre-process once to get initial stats and mapping
            _, renamed, s, _, _, _ = load_and_process(file_bytes, filename, rapid_days)

            # Filter stats to be JSON serializable
            serializable_stats = {}
            for k, v in s.items():
                if isinstance(v, pd.DataFrame):
                    serializable_stats[k] = v.to_dict(orient='records')
                else:
                    serializable_stats[k] = v

            request.session['raw_data'] = base64.b64encode(file_bytes).decode('utf-8')
            request.session['filename'] = filename
            request.session['rapid_days'] = rapid_days
            request.session['initial_renamed'] = renamed
            request.session['initial_stats'] = serializable_stats

            return redirect('core:mapping')
    else:
        form = VoucherUploadForm()
    return render(request, 'core/upload.html', {'form': form})

def mapping_view(request):
    filename = request.session.get('filename')
    if not filename:
        return redirect('core:upload')

    renamed = request.session.get('initial_renamed', {})

    if request.method == 'POST':
        new_mapping = {}
        for original_col in renamed.keys():
            # Sanitize original_col for key lookup (it was lowercase/stripped in load_and_process)
            import re
            key = re.sub(r"[^a-z0-9]", "_", original_col.lower().strip())
            key = re.sub(r"_+", "_", key).strip("_")

            new_target = request.POST.get(f"map_{original_col}")
            if new_target:
                new_mapping[original_col] = new_target

        request.session['custom_mapping'] = new_mapping
        return redirect('core:dashboard')

    return render(request, 'core/mapping.html', {
        'filename': filename,
        'renamed': renamed,
    })

def dashboard_view(request):
    raw_data_b64 = request.session.get('raw_data')
    if not raw_data_b64:
        return redirect('core:upload')

    file_bytes = base64.b64decode(raw_data_b64)
    filename = request.session.get('filename')
    rapid_days = request.session.get('rapid_days', 7)
    custom_mapping = request.session.get('custom_mapping')

    df, _, s, _, _, rapid = load_and_process(file_bytes, filename, rapid_days)

    # Generate charts using processing results
    charts = {}
    if 'top_patients' in s:
        tp = s['top_patients']
        charts['patients'] = buffer_to_base64(hbar_chart_buf(
            tp['id'].tolist(), tp['visits'].tolist(), ACCENT, "Top Patients", "Visits"
        ))

    if 'top_doctors' in s:
        td = s['top_doctors']
        charts['doctors'] = buffer_to_base64(hbar_chart_buf(
            td['doctor'].tolist(), td['visits'].tolist(), ACCENT2, "Top Prescribers", "Visits"
        ))

    charts['timeseries'] = buffer_to_base64(time_series_chart_buf(df))
    charts['rapid_hist'] = buffer_to_base64(rapid_histogram_buf(rapid))

    context = {
        'stats': s,
        'charts': charts,
        'rapid': rapid[:50],
        'filename': filename,
        'total_rows': len(df),
    }
    return render(request, 'core/dashboard.html', context)

def export_csv_view(request):
    raw_data_b64 = request.session.get('raw_data')
    if not raw_data_b64:
        return HttpResponse("No data to export", status=400)

    file_bytes = base64.b64decode(raw_data_b64)
    filename = request.session.get('filename')
    rapid_days = request.session.get('rapid_days', 7)

    df, _, _, _, _, _ = load_and_process(file_bytes, filename, rapid_days)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pharmascan_export.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def clear_session_view(request):
    request.session.flush()
    return redirect('core:upload')

from .utils import build_network_data, run_match, generate_excel_audit_report

def network_view(request):
    raw_data_b64 = request.session.get('raw_data')
    if not raw_data_b64: return redirect('core:upload')

    file_bytes = base64.b64decode(raw_data_b64)
    filename = request.session.get('filename')
    df, _, _, _, _, _ = load_and_process(file_bytes, filename, 7)

    net_data = build_network_data(df)
    return render(request, 'core/network.html', {'network_data': net_data})

def fraud_view(request):
    raw_data_b64 = request.session.get('raw_data')
    if not raw_data_b64: return redirect('core:upload')

    file_bytes = base64.b64decode(raw_data_b64)
    filename = request.session.get('filename')
    df, _, _, _, _, _ = load_and_process(file_bytes, filename, 7)

    ph_work = df.copy()
    # Ensure columns exist for run_match
    ph_work["_rama"] = ph_work.get("patient_id", "")
    ph_work["_name"] = ph_work.get("patient_name", "")
    ph_work["_date"] = ph_work.get("visit_date", pd.NaT)
    ph_work["_vou"] = ph_work.get("voucher_id", "")
    ph_work["_ins"] = ph_work.get("insurance_copay", 0)
    ph_work["_tot"] = ph_work.get("amount", 0)

    fraud_results = []
    stats = {}

    if request.method == 'POST' and request.FILES.getlist('facility_files'):
        new_frames = []
        for uf in request.FILES.getlist('facility_files'):
            # Simplified parsing for the demo/implementation
            f_df = pd.read_excel(uf) if uf.name.endswith(('.xlsx', '.xls')) else pd.read_csv(uf)
            # Normalize to internal format
            parsed = pd.DataFrame()
            # Try to find columns similar to _parse_facility
            # Here we'll just assume simple structure for now or map common ones
            parsed["_rama"] = f_df.iloc[:, 0].astype(str) # placeholder
            parsed["_name"] = f_df.iloc[:, 1].astype(str)
            parsed["_date"] = pd.to_datetime(f_df.iloc[:, 2], errors='coerce')
            parsed["_source"] = uf.name
            new_frames.append(parsed)

        if new_frames:
            fac_df = pd.concat(new_frames, ignore_index=True)
            res_df = run_match(ph_work, fac_df)
            request.session['fraud_results_json'] = res_df.to_json(orient='records', date_format='iso')
            fraud_results = res_df[res_df['status'] != 'MATCHED'].to_dict('records')

            stats = {
                'no_record_count': len(res_df[res_df['status'] == 'NO_RECORD']),
                'unlinked_count': len(res_df[res_df['status'] == 'UNLINKED']),
                'coverage_pct': round(100 * len(res_df[res_df['status'] == 'MATCHED']) / len(res_df)) if len(res_df) > 0 else 0
            }

    return render(request, 'core/fraud.html', {
        'fraud_results': fraud_results,
        'stats': stats
    })

def export_audit_view(request):
    fraud_json = request.session.get('fraud_results_json')
    if not fraud_json: return HttpResponse("No audit data", status=400)

    res_df = pd.read_json(io.StringIO(fraud_json))
    buf = generate_excel_audit_report(res_df)

    response = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="PharmaScan_Fraud_Audit.xlsx"'
    return response
