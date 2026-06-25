from django.db import models

class ClaimFileBatch(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='pending') # pending, processed, error

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at})"

class NormalizedClaim(models.Model):
    batch = models.ForeignKey(ClaimFileBatch, on_delete=models.CASCADE, related_name='claims')
    voucher_id = models.CharField(max_length=100, blank=True, null=True)
    patient_id = models.CharField(max_length=100, blank=True, null=True)
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    doctor_id = models.CharField(max_length=100, blank=True, null=True)
    doctor_name = models.CharField(max_length=255, blank=True, null=True)
    visit_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    insurance_copay = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    patient_copay = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    medicine_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    facility = models.CharField(max_length=255, blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)

    # Absolute deduplication shield
    row_integrity_hash = models.CharField(max_length=64, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Claim {self.voucher_id} - {self.patient_name}"
