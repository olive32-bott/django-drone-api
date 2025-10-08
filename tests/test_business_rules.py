from django.urls import reverse
from rest_framework.test import APITestCase
from fleet.models import Drone, Medication

class BusinessRuleTests(APITestCase):
    def setUp(self):
        self.drone = Drone.objects.create(
            serial_number='SN-001',
            model=Drone.ModelChoices.LIGHTWEIGHT,
            weight_limit=300,
            battery_capacity=20,  # below threshold
            state=Drone.StateChoices.LOADING,
        )
        self.med = Medication.objects.create(
            name='PARA_500',
            weight=100,
            code='PARA_500',
            image='medications/dummy.jpg',
        )

    def test_drone_with_low_battery_cannot_load(self):
        url = reverse('fleet:drone-load', args=[self.drone.pk])
        res = self.client.post(url, {'items': [{'medication_id': str(self.med.pk), 'quantity': 1}]}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('battery', str(res.data).lower())

    def test_weight_limit_enforced(self):
        self.drone.battery_capacity = 50
        self.drone.save()

        url = reverse('fleet:drone-load', args=[self.drone.pk])
        # quantity 4 * 100g = 400g > 300g limit
        res = self.client.post(url, {'items': [{'medication_id': str(self.med.pk), 'quantity': 4}]}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('weight', str(res.data).lower())

    def test_state_must_be_loading(self):
        self.drone.battery_capacity = 50
        self.drone.state = Drone.StateChoices.IDLE
        self.drone.save()

        url = reverse('fleet:drone-load', args=[self.drone.pk])
        res = self.client.post(url, {'items': [{'medication_id': str(self.med.pk), 'quantity': 1}]}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('loading', str(res.data).lower())
