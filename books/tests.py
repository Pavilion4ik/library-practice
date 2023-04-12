from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken
from books.models import Book
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from books.serializers import BookSerializer
from users.models import User


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HR",
            inventory=5,
            daily_fee=1.99,
        )

    def test_book_title(self):
        self.assertEqual(str(self.book), "Test Author: Test Book")

    def test_book_daily_fee(self):
        self.assertEqual(self.book.daily_fee, 1.99)

    def test_book_cover_choices(self):
        self.assertIn(self.book.cover, [choice[0] for choice in Book.Cover.choices])


class BookAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.book1 = Book.objects.create(
            title="Test Book 1",
            author="Test Author",
            cover="HR",
            inventory=1,
            daily_fee=1.99,
        )
        self.book2 = Book.objects.create(
            title="Test Book 2",
            author="Test Author",
            cover="HR",
            inventory=2,
            daily_fee=2.99,
        )
        self.user = User.objects.create_superuser(
            email="test_user@mail.com", password="test_password"
        )
        self.access_token = str(AccessToken.for_user(self.user))

    def test_get_all_books(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.get("/api/books/")
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_book(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.get(f"/api/books/{self.book1.pk}/")
        book = Book.objects.get(pk=self.book1.pk)
        serializer = BookSerializer(book)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        new_book = {
            "title": "Test Book 3",
            "author": "Test Author",
            "cover": "HR",
            "inventory": 3,
            "daily_fee": 3.99,
        }
        response = self.client.post("/api/books/", new_book)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_book(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        updated_book = {
            "title": "Test Book 1 Updated",
            "author": "Test Author Updated",
            "cover": "ST",
            "inventory": 10,
            "daily_fee": 5.99,
        }
        response = self.client.put(f"/api/books/{self.book1.pk}/", updated_book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.delete(f"/api/books/{self.book2.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book2.pk).exists())
