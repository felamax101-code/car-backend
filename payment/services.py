from django.utils import timezone

from parking.services import open_gate, release_slot
from sessions_app.models import ParkingSession

from .gateway import charge
from .models import Payment


def create_pending_payment(session, amount):
    """Called at the start of exit (Task One 3.3, step 5-6): fee is shown,
    payment is not yet made."""
    return Payment.objects.create(session=session, amount=amount, status=Payment.Status.PENDING)


def settle_payment(payment, exit_gate, method="MOCK"):
    """
    Task One 3.5 combined with the back half of 3.3: charge the mock
    gateway, and on success complete the session, free the slot, and
    open the exit barrier. On failure, nothing changes — the barrier
    stays closed and the driver can retry.
    """
    success, reference = charge(payment, method=method)

    if not success:
        payment.status = Payment.Status.FAILED
        payment.method = method
        payment.save(update_fields=["status", "method"])
        return payment, False

    payment.status = Payment.Status.PAID
    payment.method = method
    payment.reference = reference
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "method", "reference", "paid_at"])

    session = payment.session
    session.status = ParkingSession.Status.COMPLETED
    session.exit_time = timezone.now()
    session.exit_gate = exit_gate
    session.amount_paid = payment.amount
    session.save(update_fields=["status", "exit_time", "exit_gate", "amount_paid"])

    release_slot(session.slot)
    open_gate(exit_gate)

    return payment, True