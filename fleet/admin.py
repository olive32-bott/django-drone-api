from django.contrib import admin
from .models import Drone, Medication, CargoItem

@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'model', 'weight_limit', 'battery_capacity', 'state', 'current_load_weight')
    search_fields = ('serial_number',)
    list_filter = ('model', 'state')

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'weight')
    search_fields = ('name', 'code')

@admin.register(CargoItem)
class CargoItemAdmin(admin.ModelAdmin):
    list_display = ('drone', 'medication', 'quantity')
    list_select_related = ('drone', 'medication')
