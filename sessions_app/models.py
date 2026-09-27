from django.conf import settings
from django.db import models

from parking.models import Gate, ParkingSlot


class Vehicle(models.Model):
    """A returning plate reuses this record — history accumulates per plate."""

    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=30, default="CAR")
    first_seen = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.plate_number


class ParkingSession(models.Model):
    """
    One row per visit. Task One 5.2 — the central transactional table.
    Never deleted, only moved through the status states below, so it
    doubles as the history used for reporting.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"                       # parked, not yet at exit
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"  # at exit, fee shown, awaiting payment
        COMPLETED = "COMPLETED", "Completed"               # paid, barrier opened, slot freed

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="sessions")
    slot = models.ForeignKey(ParkingSlot, on_delete=models.PROTECT, related_name="sessions")
    entry_gate = models.ForeignKey(Gate, on_delete=models.SET_NULL, null=True, related_name="entries")
    exit_gate = models.ForeignKey(
        Gate, on_delete=models.SET_NULL, null=True, blank=True, related_name="exits"
    )

    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    amount_due = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Indexed: this is the field the exit flow looks up by (Task One 4.1's
    # 'hash map keyed by plate number' — the DB index gives the same O(1)-ish
    # lookup behaviour in practice).
    class Meta:
        indexes = [
            models.Index(fields=["status"]),
        ]
        ordering = ["-entry_time"]

    def __str__(self):
        return f"{self.vehicle.plate_number} @ slot {self.slot.slot_number} ({self.status})"