from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from books.models import Book
from .models import Borrowing
import datetime
from rest_framework.test import APIClient
from rest_framework import status


class BorrowingModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            email='testuser@test.com',
            password='testpass',
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HR",
            inventory=5,
            daily_fee=1.99,
        )

    def test_model_fields(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=3)
        )
        self.assertIsInstance(borrowing.borrow_date, datetime.date)
        self.assertEqual(borrowing.expected_return_date, timezone.now().date() + timezone.timedelta(days=3))
        self.assertIsNone(borrowing.actual_return_date)

    def test_object_creation_and_string_representation(self):
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=3)
        )
        self.assertIsInstance(borrowing, Borrowing)
        expected_string = f"{self.book.title} was borrow {borrowing.borrow_date.strftime('%Y-%m-%d')} " \
                          f"expected return {borrowing.expected_return_date.strftime('%Y-%m-%d')}"
        self.assertEqual(str(borrowing), expected_string)

    def test_object_querying(self):
        borrowing_1 = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=3)
        )
        borrowing_2 = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now() - timezone.timedelta(days=7),
            expected_return_date=timezone.now().date() - timezone.timedelta(days=2),
            actual_return_date=timezone.now().date()
        )
        self.assertQuerysetEqual(
            Borrowing.objects.filter(actual_return_date__isnull=False),
            [repr(borrowing_2)],
            transform=repr
        )


class BorrowingListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpass')
        self.admin = User.objects.create_superuser(email='adminuser@gmail.com', password='adminpass')
        self.client = APIClient()
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HR",
            inventory=5,
            daily_fee=1.99,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=3)
        )
        self.access_token = str(AccessToken.for_user(self.admin))

    def test_get_borrowings_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/borrowings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_borrowings_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/borrowings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_borrowings_filter_by_user_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/borrowings/', {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_borrowing(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        data = {'book': self.book.id, 'user': self.user.id,
                'expected_return_date': str(timezone.now().date() + timezone.timedelta(days=3))}
        response = self.client.post('/api/borrowings/create/', data)
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 2)

    def test_create_borrowing_with_invalid_book(self):
        self.client.force_authenticate(user=self.user)
        data = {'book': 123}
        response = self.client.post('/api/borrowings/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Borrowing.objects.count(), 1)


class BorrowingDetailViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email='adminuser@mail.com', password='adminpass')
        self.client = APIClient()
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HR",
            inventory=5,
            daily_fee=1.99,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.admin,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=3)
        )

    def test_return_book(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/borrowings/{self.borrowing.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_book_as_user(self):
        self.client.force_authenticate(user=User.objects.create_user(email='testuser@mail.com', password='testpass'))
        response = self.client.delete(f'/api/borrowings/{self.borrowing.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_borrowing_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/borrowings/{self.borrowing.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
