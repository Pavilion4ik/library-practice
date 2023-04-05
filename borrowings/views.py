from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from books.permissions import IsAdminOrReadOnly
from django_filters import rest_framework as filters


class BorrowingFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user")


class BorrowingListView(generics.ListAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = BorrowingFilter

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if user.is_staff:
            return queryset
        return queryset.filter(user__email=user.email)


class BorrowingDetailView(generics.RetrieveDestroyAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def delete(self, request, *args, **kwargs):
        for borrowing in self.queryset.all():
            with transaction.atomic():
                borrowing.book.inventory += 1

                borrowing.book.save()

                return self.destroy(request, *args, **kwargs)


class BorrowingCreateView(generics.CreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer
    permission_classes = (IsAuthenticated,)
