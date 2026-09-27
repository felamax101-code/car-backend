from rest_framework import serializers

from .models import ParkingSession, Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "plate_number", "vehicle_type", "first_seen"]


class ParkingSessionSerializer(serializers.ModelSerializer):
    plate_number = serializers.CharField(source="vehicle.plate_number", read_only=True)
    slot_number = serializers.IntegerField(source="slot.slot_number", read_only=True)

    class Meta:
        model = ParkingSession
        fields = [
            "id",
            "plate_number",
            "slot_number",
            "entry_time",
            "exit_time",
            "status",
            "amount_due",
            "amount_paid",
        ]
        read_only_fields = fields