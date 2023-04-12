from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from payment.models import Payment
from payment.serializers import PaymentSerializer
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User


class PaymentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Payment.objects.create(status=Payment.Status.PENDING, type=Payment.Type.PAYMENT)

    def test_status_label(self):
        payment = Payment.objects.get(id=1)
        field_label = payment._meta.get_field("status").verbose_name
        self.assertEqual(field_label, "status")

    def test_type_label(self):
        payment = Payment.objects.get(id=1)
        field_label = payment._meta.get_field("type").verbose_name
        self.assertEqual(field_label, "type")

    def test_status_max_length(self):
        payment = Payment.objects.get(id=1)
        max_length = payment._meta.get_field("status").max_length
        self.assertEqual(max_length, 2)

    def test_type_max_length(self):
        payment = Payment.objects.get(id=1)
        max_length = payment._meta.get_field("type").max_length
        self.assertEqual(max_length, 2)

    def test_status_choices(self):
        payment = Payment.objects.get(id=1)
        choices = payment._meta.get_field("status").choices
        self.assertEqual(choices, [("PN", "Pending"), ("PD", "Paid")])

    def test_type_choices(self):
        payment = Payment.objects.get(id=1)
        choices = payment._meta.get_field("type").choices
        self.assertEqual(choices, [("PN", "Payment"), ("FN", "Fine")])


class PaymentSerializerTest(TestCase):
    def setUp(self):
        self.payment_data = {"status": Payment.Status.PAID, "type": Payment.Type.FINE}
        self.serializer = PaymentSerializer(data=self.payment_data)

    def test_contains_expected_fields(self):
        data = self.serializer.initial_data
        self.assertCountEqual(data.keys(), ["status", "type"])

    def test_status_field_content(self):
        data = self.serializer.initial_data
        self.assertEqual(data["status"], self.payment_data["status"])

    def test_type_field_content(self):
        data = self.serializer.initial_data
        self.assertEqual(data["type"], self.payment_data["type"])

    def test_valid_data(self):
        self.assertTrue(self.serializer.is_valid())

    def test_invalid_status_field(self):
        self.payment_data["status"] = "Invalid"
        serializer = PaymentSerializer(data=self.payment_data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ["status"])

    def test_invalid_type_field(self):
        self.payment_data["type"] = 'Invalid'
        serializer = PaymentSerializer(data=self.payment_data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ["type"])


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payment_data = {"status": Payment.Status.PENDING, "type": Payment.Type.PAYMENT}
        self.payment = Payment.objects.create(**self.payment_data)
        self.admin = User.objects.create_superuser(email='testadmin@mail.com', password='testadmin')
        self.access_token = str(AccessToken.for_user(self.admin))

    def test_create_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.post("/api/payments/", self.payment_data)
        print(response.content)
        pending_payments = Payment.objects.filter(status=Payment.Status.PENDING)
        self.assertEqual(pending_payments.count(), 2)
        self.assertEqual(pending_payments.first().type, Payment.Type.PAYMENT)

    def test_get_payment_list(self):
        payment_data2 = {"status": Payment.Status.PAID, "type": Payment.Type.FINE}
        payment2 = Payment.objects.create(**payment_data2)
        response = self.client.get("/api/payments/")
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_payment_detail(self):
        response = self.client.get(f"/api/payments/{self.payment.id}/")
        serializer = PaymentSerializer(self.payment)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        updated_payment_data = {"status": Payment.Status.PAID, "type": Payment.Type.FINE}
        response = self.client.put(f"/api/payments/{self.payment.id}/", updated_payment_data, format="json")
        self.payment.refresh_from_db()
        serializer = PaymentSerializer(self.payment)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_payment(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.delete(f"/api/payments/{self.payment.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Payment.objects.count(), 0)
