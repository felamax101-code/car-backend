from rest_framework import serializers

from .models import Gate, ParkingLot, ParkingSlot, Tariff


class ParkingLotSerializer(serializers.ModelSerializer):
    total_slots = serializers.ReadOnlyField()
    available_slots = serializers.ReadOnlyField()

    class Meta:
        model = ParkingLot
        fields = ["id", "name", "location", "total_slots", "available_slots"]


class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = ["id", "lot", "slot_number", "status", "slot_type"]
        read_only_fields = ["status"]  # status changes only via entry/exit logic, not direct edits


class GateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gate
        fields = ["id", "lot", "gate_number", "gate_type", "status"]
        read_only_fields = ["status"]  # status changes only via barrier control logic


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ["id", "lot", "min_minutes", "max_minutes", "amount", "effective_from"]
        read_only_fields = ["effective_from"]