"""
Implementations of the Task One algorithms (Slot Availability, Fee
Calculation, Barrier Control) as plain functions, kept separate from the
views so they're easy to unit test and reuse.
"""

from django.utils import timezone

from .models import Gate, ParkingSlot, Tariff


def get_availability(lot):
    """Task One 3.1 — getAvailableSlots()."""
    total = lot.slots.count()
    available = lot.slots.filter(status=ParkingSlot.Status.AVAILABLE).count()
    return {"total": total, "available": available}


def assign_slot(lot):
    """
    Task One 3.2 (slot-finding step).

    Simple, correct baseline: first free slot by slot_number. A
    nearest-slot / priority-queue optimisation (Task One 4, 'priority
    queue' row) can replace just this function later without touching
    the entry view that calls it.
    """
    slot = (
        lot.slots.filter(status=ParkingSlot.Status.AVAILABLE)
        .order_by("slot_number")
        .select_for_update()
        .first()
    )
    return slot


def release_slot(slot):
    slot.status = ParkingSlot.Status.AVAILABLE
    slot.save(update_fields=["status"])


def occupy_slot(slot):
    slot.status = ParkingSlot.Status.OCCUPIED
    slot.save(update_fields=["status"])


def calculate_fee(duration_minutes, lot):
    """
    Task One 3.4 — calculateFee(). Reads dynamic Tariff rows for the lot,
    sorted ascending by min_minutes, instead of hardcoding bands.
    """
    bands = Tariff.objects.filter(lot=lot).order_by("min_minutes")

    for band in bands:
        lower_ok = duration_minutes >= band.min_minutes
        upper_ok = band.max_minutes is None or duration_minutes <= band.max_minutes
        if lower_ok and upper_ok:
            return band.amount

    # No band matched (e.g. tariffs not configured yet) — fail safe to 0
    # rather than silently charging an undefined amount.
    return 0


def open_gate(gate):
    """Task One 3.6 — simplified barrier state machine (no hardware here)."""
    gate.status = Gate.Status.OPEN
    gate.save(update_fields=["status"])


def close_gate(gate):
    gate.status = Gate.Status.CLOSED
    gate.save(update_fields=["status"])


def now():
    return timezone.now()