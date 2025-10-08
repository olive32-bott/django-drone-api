from rest_framework import serializers
from .models import Drone, Medication, CargoItem

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'weight', 'code', 'image']

class CargoItemSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer(read_only=True)
    medication_id = serializers.PrimaryKeyRelatedField(queryset=Medication.objects.all(), source='medication', write_only=True)

    class Meta:
        model = CargoItem
        fields = ['id', 'medication', 'medication_id', 'quantity', 'total_weight']
        read_only_fields = ['id', 'total_weight', 'medication']

class DroneSerializer(serializers.ModelSerializer):
    current_load_weight = serializers.IntegerField(read_only=True)
    remaining_capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Drone
        fields = ['id', 'serial_number', 'model', 'weight_limit', 'battery_capacity', 'state', 'current_load_weight', 'remaining_capacity']

    def validate_serial_number(self, v):
        if len(v) > 100:
            raise serializers.ValidationError("Serial number must be at most 100 characters.")
        return v

    def validate_weight_limit(self, v):
        if v > 500:
            raise serializers.ValidationError("Weight limit cannot exceed 500 grams.")
        if v <= 0:
            raise serializers.ValidationError("Weight limit must be positive.")
        return v

    def validate_battery_capacity(self, v):
        if not (0 <= v <= 100):
            raise serializers.ValidationError("Battery capacity must be 0-100.")
        return v

class LoadItem(serializers.Serializer):
    medication_id = serializers.PrimaryKeyRelatedField(queryset=Medication.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)

class LoadRequestSerializer(serializers.Serializer):
    items = LoadItem(many=True)

class BatterySerializer(serializers.Serializer):
    battery_capacity = serializers.IntegerField(read_only=True)
