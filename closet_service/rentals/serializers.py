from rest_framework import serializers
from .models import Item, BorrowedItem


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "tier"]


class BorrowedItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = BorrowedItem
        fields = ["id", "item", "borrowed_at"]