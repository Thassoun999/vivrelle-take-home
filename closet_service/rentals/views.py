from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import User, Item, BorrowedItem
from .serializers import BorrowedItemSerializer
from .services import get_user_closet, borrow_item, return_item, get_eligible_upgrades, get_eligible_downgrades, change_user_plan

Plan = User.Plan

# Create your views here.
@api_view(["GET"])
def get_closet(request, user_id):

    try:
        user = User.objects.get(id=user_id)
    except user.DoesNotExist:
        return Response(
            {"error": "user not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    closet = get_user_closet(user)

    serializer = BorrowedItemSerializer(closet, many=True)

    return Response(serializer.data)

# {
#   "user_id": 1,
#   "item_id": 5 
# }

@api_view(["POST"])
def borrow(request):

    user_id = request.data.get("user_id")
    item_id = request.data.get("item_id")

    try:
        user = User.objects.get(id=user_id)
        item = Item.objects.get(id=item_id)
    except (user.DoesNotExist, Item.DoesNotExist):
        return Response(
            {"error": "Invalid user or item"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        borrow = borrow_item(user, item)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = BorrowedItemSerializer(borrow)

    return Response(serializer.data)

# {
#   "borrow_id": 2
# }

@api_view(["POST"])
def return_borrowed_item(request):

    borrow_id = request.data.get("borrow_id")

    try:
        borrow = BorrowedItem.objects.get(id=borrow_id)
    except BorrowedItem.DoesNotExist:
        return Response(
            {"error": "Borrow record not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    return_item(borrow)

    return Response({"message": "Item returned successfully"})

@api_view(["GET"])
def eligible_upgrades(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    plans = get_eligible_upgrades(user)
    return Response({"eligible_upgrades": plans})


@api_view(["GET"])
def eligible_downgrades(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    plans = get_eligible_downgrades(user)
    return Response({"eligible_downgrades": plans})


# { "new_plan": "couture_plus" } 
@api_view(["POST"])
def change_plan(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    new_plan = request.data.get("new_plan")
    if new_plan not in [p.value for p in Plan]:
        return Response({"error": "Invalid plan"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        updated_user = change_user_plan(user, new_plan)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": f"User plan changed to {updated_user.plan}"})