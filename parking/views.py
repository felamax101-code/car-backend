from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from .models import Gate, ParkingLot, ParkingSlot, Tariff
from .serializers import GateSerializer, ParkingLotSerializer, ParkingSlotSerializer, TariffSerializer
from .services import get_availability


class SlotAvailabilityView(APIView):
    """
    GET /api/parking/lots/<lot_id>/availability/

    Task One 3.1 — any logged-in role can check this (it's what drivers
    see before entry, and what the display board polls).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, lot_id):
        lot = get_object_or_404(ParkingLot, pk=lot_id)
        return Response(get_availability(lot))


class SlotGridView(APIView):
    """
    GET /api/parking/lots/<lot_id>/slots/

    Full slot-by-slot status, for rendering the visual display grid.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, lot_id):
        lot = get_object_or_404(ParkingLot, pk=lot_id)
        slots = lot.slots.all()
        return Response(ParkingSlotSerializer(slots, many=True).data)


# ---------------------------------------------------------------------
# Admin CRUD — lots, slots, gates, tariffs.
# Each pair (List/Create + Detail) follows the same shape deliberately,
# so it's easy to see they all follow one pattern.
# ---------------------------------------------------------------------


class ParkingLotListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        lots = ParkingLot.objects.all()
        return Response(ParkingLotSerializer(lots, many=True).data)

    def post(self, request):
        serializer = ParkingLotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParkingSlotListCreateView(APIView):
    """
    Adding a row here is how the client 'adds a slot' — no code change,
    matching the Task One 5.3 definition of 'dynamic'.
    """

    permission_classes = [IsAdmin]

    def get(self, request):
        slots = ParkingSlot.objects.all()
        return Response(ParkingSlotSerializer(slots, many=True).data)

    def post(self, request):
        serializer = ParkingSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParkingSlotDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        slot = get_object_or_404(ParkingSlot, pk=pk)
        serializer = ParkingSlotSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        slot = get_object_or_404(ParkingSlot, pk=pk)
        slot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GateListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        gates = Gate.objects.all()
        return Response(GateSerializer(gates, many=True).data)

    def post(self, request):
        serializer = GateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TariffListCreateView(APIView):
    """
    Editing prices here is how the client changes fees — Task One 3.4's
    fee calculation reads these rows, nothing is hardcoded.
    """

    permission_classes = [IsAdmin]

    def get(self, request):
        tariffs = Tariff.objects.all()
        return Response(TariffSerializer(tariffs, many=True).data)

    def post(self, request):
        serializer = TariffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TariffDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        tariff = get_object_or_404(Tariff, pk=pk)
        serializer = TariffSerializer(tariff, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        tariff = get_object_or_404(Tariff, pk=pk)
        tariff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)