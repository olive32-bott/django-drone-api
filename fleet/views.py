from django.db import transaction
from django.db.models import Sum, F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Drone, Medication, CargoItem
from .serializers import DroneSerializer, MedicationSerializer, CargoItemSerializer, LoadRequestSerializer, BatterySerializer

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by('name')
    serializer_class = MedicationSerializer
    permission_classes = [AllowAny]

class DroneViewSet(viewsets.ModelViewSet):
    queryset = Drone.objects.all().order_by('serial_number')
    serializer_class = DroneSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def load(self, request, pk=None):
        drone = self.get_object()
        ser = LoadRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if drone.state != Drone.StateChoices.LOADING:
            return Response({'detail': 'Drone must be in LOADING state to load medications.'}, status=400)

        if drone.battery_capacity < 25:
            return Response({'detail': 'Drone battery must be at least 25% to load medications.'}, status=400)

        items = ser.validated_data['items']

        with transaction.atomic():
            # lock cargo items to prevent race conditions
            Drone.objects.select_for_update().filter(pk=drone.pk).first()

            # calculate added weight
            add_weight = 0
            for item in items:
                med = item['medication_id']
                qty = item['quantity']
                add_weight += med.weight * qty

            if add_weight <= 0:
                return Response({'detail': 'Nothing to load.'}, status=400)

            if drone.current_load_weight + add_weight > drone.weight_limit:
                return Response({'detail': 'Loading would exceed the drone weight limit.'}, status=400)

            # upsert cargo items
            created_items = []
            for item in items:
                med = item['medication_id']
                qty = item['quantity']
                cargo, created = CargoItem.objects.get_or_create(drone=drone, medication=med, defaults={'quantity': qty})
                if not created:
                    cargo.quantity = cargo.quantity + qty
                    cargo.save(update_fields=['quantity'])
                created_items.append(cargo)

            # once loaded, move to LOADED
            drone.state = Drone.StateChoices.LOADED
            drone.save(update_fields=['state'])

        out = CargoItemSerializer(Drone.objects.get(pk=drone.pk).cargo_items.select_related('medication'), many=True)
        return Response({'drone': DroneSerializer(drone).data, 'cargo': out.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def medications(self, request, pk=None):
        drone = self.get_object()
        items = drone.cargo_items.select_related('medication')
        data = CargoItemSerializer(items, many=True).data
        return Response({'drone': DroneSerializer(drone).data, 'cargo': data})

    @action(detail=False, methods=['get'], url_path='available-for-loading')
    def available_for_loading(self, request):
        qs = self.get_queryset().annotate(
            current=Sum(F('cargo_items__quantity') * F('cargo_items__medication__weight'))
        ).filter(
            battery_capacity__gte=25,
            state__in=[Drone.StateChoices.IDLE, Drone.StateChoices.LOADING]
        )
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

    @action(detail=True, methods=['get'])
    def battery(self, request, pk=None):
        drone = self.get_object()
        return Response({'battery_capacity': drone.battery_capacity})

    @action(detail=True, methods=['post'], url_path='state')
    def change_state(self, request, pk=None):
        drone = self.get_object()
        next_state = request.data.get('state')
        allowed = {
            Drone.StateChoices.IDLE: [Drone.StateChoices.LOADING],
            Drone.StateChoices.LOADING: [Drone.StateChoices.LOADED],
            Drone.StateChoices.LOADED: [Drone.StateChoices.DELIVERING],
            Drone.StateChoices.DELIVERING: [Drone.StateChoices.DELIVERED, Drone.StateChoices.RETURNING],
            Drone.StateChoices.DELIVERED: [Drone.StateChoices.RETURNING, Drone.StateChoices.IDLE],
            Drone.StateChoices.RETURNING: [Drone.StateChoices.IDLE],
        }
        if next_state not in dict(Drone.StateChoices.choices):
            return Response({'detail': 'Invalid state.'}, status=400)
        if next_state not in allowed.get(drone.state, []):
            return Response({'detail': f'Invalid transition from {drone.state} to {next_state}.'}, status=400)
        drone.state = next_state
        drone.save(update_fields=['state'])
        return Response(DroneSerializer(drone).data, status=200)
