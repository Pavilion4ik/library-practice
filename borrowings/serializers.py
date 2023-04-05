from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"


class BorrowingCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if not attrs["book"].inventory:
            raise ValidationError("Book is not available")
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]

            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(**validated_data)

        return borrowing

    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "actual_return_date", "book", "user")
        read_only_fields = ("borrow_date",)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"
