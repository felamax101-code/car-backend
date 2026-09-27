from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrGateOperator
from parking.models import Gate, ParkingLot
from parking.services import assign_slot, calculate_fee, occupy_slot, open_gate
from payments.services import create_pending_payment

from .models import ParkingSession, Vehicle
from .serializers import ParkingSessionSerializer


class EntryView(APIView):
    """
    POST /api/sessions/entry/
    { "plate_number": "KDA123X", "lot_id": 1, "gate_id": 3 }

    Task One 3.2 — handleEntry(). Gate clerks and admins only; drivers
    don't call this directly (a real gate/camera or the clerk's UI does).
    """

    permission_classes = [IsAdminOrGateOperator]

    @transaction.atomic
    def post(self, request):
        plate_number = request.data.get("plate_number", "").strip().upper()
        lot_id = request.data.get("lot_id")
        gate_id = request.data.get("gate_id")

        if not plate_number or not lot_id or not gate_id:
            return Response(
                {"detail": "plate_number, lot_id and gate_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lot = get_object_or_404(ParkingLot, pk=lot_id)
        gate = get_object_or_404(Gate, pk=gate_id, lot=lot, gate_type=Gate.GateType.ENTRY)

        slot = assign_slot(lot)
        if slot is None:
            return Response({"detail": "Lot full — no available slots."}, status=status.HTTP_409_CONFLICT)

        vehicle, _ = Vehicle.objects.get_or_create(plate_number=plate_number)

        session = ParkingSession.objects.create(
            vehicle=vehicle,
            slot=slot,
            entry_gate=gate,
            entry_time=timezone.now(),
            status=ParkingSession.Status.ACTIVE,
        )

        occupy_slot(slot)
        open_gate(gate)

        return Response(ParkingSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class ExitView(APIView):
    """
    POST /api/sessions/exit/
    { "plate_number": "KDA123X" }

    Task One 3.3 (steps 1-6) + 3.4 — finds the active session by plate,
    computes duration and fee, and creates a PENDING payment. The
    barrier does NOT open here; that happens in payments.PayView once
    the fee is actually paid.
    """

    permission_classes = [IsAdminOrGateOperator]

    def post(self, request):
        plate_number = request.data.get("plate_number", "").strip().upper()
        if not plate_number:
            return Response({"detail": "plate_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        session = (
            ParkingSession.objects.filter(
                vehicle__plate_number=plate_number, status=ParkingSession.Status.ACTIVE
            )
            .order_by("-entry_time")
            .first()
        )
        if session is None:
            return Response(
                {"detail": "No active session found for this plate."},
                status=status.HTTP_404_NOT_FOUND,
            )

        duration_minutes = int((timezone.now() - session.entry_time).total_seconds() // 60)
        fee = calculate_fee(duration_minutes, session.slot.lot)

        session.amount_due = fee
        session.status = ParkingSession.Status.PENDING_PAYMENT
        session.save(update_fields=["amount_due", "status"])

        payment = create_pending_payment(session, fee)

        return Response(
            {
                "session": ParkingSessionSerializer(session).data,
                "duration_minutes": duration_minutes,
                "amount_due": fee,
                "payment_id": payment.id,
            },
            status=status.HTTP_200_OK,
        )


class ActiveSessionListView(APIView):
    """GET /api/sessions/active/ — for the gate operator / admin dashboard."""

    permission_classes = [IsAdminOrGateOperator]

    def get(self, request):
        sessions = ParkingSession.objects.filter(status=ParkingSession.Status.ACTIVE)
        return Response(ParkingSessionSerializer(sessions, many=True).data)