from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrGateOperator
from parking.models import Gate

from .models import Payment
from .serializers import PaymentSerializer
from .services import settle_payment


class PayView(APIView):
    """
    POST /api/payments/<payment_id>/pay/
    { "gate_id": 5, "method": "MPESA" }   # method optional, defaults to MOCK

    Task One 3.5 + back half of 3.3. On success: session -> COMPLETED,
    slot freed, exit barrier opened. On failure: nothing changes, caller
    can retry.
    """

    permission_classes = [IsAdminOrGateOperator]

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, pk=payment_id)

        if payment.status == Payment.Status.PAID:
            return Response(
                {"detail": "This payment has already been settled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        gate_id = request.data.get("gate_id")
        exit_gate = get_object_or_404(Gate, pk=gate_id, gate_type=Gate.GateType.EXIT) if gate_id else None
        if exit_gate is None:
            return Response({"detail": "gate_id (an EXIT gate) is required."}, status=status.HTTP_400_BAD_REQUEST)

        method = request.data.get("method", "MOCK")
        payment, success = settle_payment(payment, exit_gate, method=method)

        if not success:
            return Response(
                {"detail": "Payment failed.", "payment": PaymentSerializer(payment).data},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        return Response(
            {"detail": "Payment successful. Barrier open.", "payment": PaymentSerializer(payment).data},
            status=status.HTTP_200_OK,
        )