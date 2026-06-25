from django import forms
from django.core.validators import FileExtensionValidator

class VoucherUploadForm(forms.Form):
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls', 'ods'])],
        label="Upload Pharmacy Voucher (CSV, XLSX, ODS)"
    )
    rapid_days = forms.IntegerField(initial=7, min_value=1, max_value=30, label="Rapid Revisit Window (Days)")
