import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_medication_name, validate_medication_code

class Drone(models.Model):
    class ModelChoices(models.TextChoices):
        LIGHTWEIGHT = 'LIGHTWEIGHT', 'Lightweight'
        MIDDLEWEIGHT = 'MIDDLEWEIGHT', 'Middleweight'
        CRUISERWEIGHT = 'CRUISERWEIGHT', 'Cruiserweight'
        HEAVYWEIGHT = 'HEAVYWEIGHT', 'Heavyweight'

    class StateChoices(models.TextChoices):
        IDLE = 'IDLE', 'Idle'
        LOADING = 'LOADING', 'Loading'
        LOADED = 'LOADED', 'Loaded'
        DELIVERING = 'DELIVERING', 'Delivering'
        DELIVERED = 'DELIVERED', 'Delivered'
        RETURNING = 'RETURNING', 'Returning'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=20, choices=ModelChoices.choices)
    weight_limit = models.PositiveIntegerField(validators=[MaxValueValidator(500)], help_text="grams, max 500")
    battery_capacity = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="percentage 0-100")
    state = models.CharField(max_length=20, choices=StateChoices.choices, default=StateChoices.IDLE)

    def __str__(self):
        return f"{self.serial_number} ({self.model})"

    @property
    def current_load_weight(self):
        agg = self.cargo_items.aggregate(total=models.Sum(models.F('quantity') * models.F('medication__weight')))
        return agg['total'] or 0

    @property
    def remaining_capacity(self):
        return max(0, self.weight_limit - self.current_load_weight)

class Medication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, validators=[validate_medication_name])
    weight = models.PositiveIntegerField(help_text="grams")
    code = models.CharField(max_length=100, unique=True, validators=[validate_medication_code])
    image = models.ImageField(upload_to='medications/')

    def __str__(self):
        return f"{self.name} ({self.code})"

class CargoItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drone = models.ForeignKey(Drone, related_name='cargo_items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, related_name='cargo_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['drone', 'medication'], name='unique_drone_medication')
        ]

    @property
    def total_weight(self):
        return self.medication.weight * self.quantity
