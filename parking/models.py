from django.db import models


class ParkingLot(models.Model):
    """A physical site. Supports multiple lots later without schema changes."""

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    @property
    def total_slots(self):
        return self.slots.count()

    @property
    def available_slots(self):
        return self.slots.filter(status=ParkingSlot.Status.AVAILABLE).count()


class ParkingSlot(models.Model):
    """
    One physical bay. Admins add/remove/retire slots by editing rows here —
    nothing in the entry/exit logic hardcodes a slot count.
    """

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"
        RESERVED = "RESERVED", "Reserved"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="slots")
    slot_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    slot_type = models.CharField(max_length=30, default="STANDARD")  # e.g. STANDARD, DISABLED, EV

    class Meta:
        unique_together = ("lot", "slot_number")
        ordering = ["slot_number"]

    def __str__(self):
        return f"{self.lot.name} - Slot {self.slot_number} ({self.status})"


class Gate(models.Model):
    class GateType(models.TextChoices):
        ENTRY = "ENTRY", "Entry"
        EXIT = "EXIT", "Exit"

    class Status(models.TextChoices):
        CLOSED = "CLOSED", "Closed"
        OPENING = "OPENING", "Opening"
        OPEN = "OPEN", "Open"
        CLOSING = "CLOSING", "Closing"

    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="gates")
    gate_number = models.PositiveIntegerField()
    gate_type = models.CharField(max_length=10, choices=GateType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CLOSED)

    class Meta:
        unique_together = ("lot", "gate_number", "gate_type")

    def __str__(self):
        return f"{self.lot.name} - Gate {self.gate_number} ({self.gate_type})"


class Tariff(models.Model):
    """
    Dynamic, admin-editable pricing bands (Task One, section 3.4/5.3).
    Fee lookup reads these rows — pricing changes need no code change.
    """

    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="tariffs")
    min_minutes = models.PositiveIntegerField()
    max_minutes = models.PositiveIntegerField(null=True, blank=True)  # null = open-ended top band
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    effective_from = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["min_minutes"]

    def __str__(self):
        top = self.max_minutes if self.max_minutes is not None else "∞"
        return f"{self.lot.name}: {self.min_minutes}-{top} min -> Kshs. {self.amount}"