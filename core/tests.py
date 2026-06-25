from django.test import TestCase
from .models import ClaimFileBatch, NormalizedClaim
from datetime import date

class ModelIntegrityTest(TestCase):
    def test_deduplication(self):
        batch = ClaimFileBatch.objects.create(filename="test.csv")
        # Create first record
        NormalizedClaim.objects.create(
            batch=batch,
            row_integrity_hash="unique_hash_1",
            patient_name="John Doe",
            amount=100.0
        )
        # Attempt to create duplicate hash
        with self.assertRaises(Exception):
            NormalizedClaim.objects.create(
                batch=batch,
                row_integrity_hash="unique_hash_1",
                patient_name="Duplicate Entry"
            )

    def test_batch_relationship(self):
        batch = ClaimFileBatch.objects.create(filename="batch_1.csv")
        NormalizedClaim.objects.create(
            batch=batch,
            row_integrity_hash="h1",
            patient_name="Alice"
        )
        self.assertEqual(batch.claims.count(), 1)
