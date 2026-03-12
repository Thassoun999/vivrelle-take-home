from .models import BorrowedItem, User, Item
from django.utils import timezone


Plan = User.Plan  # Plan enum from User model
Tier = Item.Tier  # Tier enum from Item model

PLAN_RULES = {
    "premier": {
        "max_items": 1,
        "allowed_tiers": ["premier"],
    },
    "classique": {
        "max_items": 1,
        "allowed_tiers": ["premier", "classique"],
    },
    "couture": {
        "max_items": 1,
        "allowed_tiers": ["premier", "classique", "couture"],
    },
    "couture_plus": {
        "max_items": 2,
        "allowed_tiers": ["premier", "classique", "couture"],
    },
}

def get_user_closet(user: User):
    return BorrowedItem.objects.filter(
        user=user,
        returned_at__isnull=True
    ).select_related("item")

def validate_borrow(user: User, item: Item):
    rules = PLAN_RULES[user.plan]

    if item.tier not in rules["allowed_tiers"]:
        raise Exception(
            f"{user.plan} users cannot borrow {item.tier} items. Please make a new selection."
        )
    
    if item.is_borrowed:
        raise Exception("This item is currently unavailable.")
    
    active_borrows = BorrowedItem.objects.filter(
        user=user,
        returned_at__isnull=True
    )

    if active_borrows.count() >= rules["max_items"]:
        raise Exception(
            "You have reached the maximum number of borrowed items for your plan."
        )
    
    # Couture Plus Case
    if user.plan == "COUTURE_PLUS":
        couture_count = active_borrows.filter(item__tier="COUTURE").count()

        if item.tier == "COUTURE" and couture_count >= 1:
            raise Exception("Couture Plus users may only borrow one Couture item at a time")
        
def borrow_item(user: User, item: Item):
    validate_borrow(user, item)

    item.is_borrowed = True
    item.save()

    return BorrowedItem.objects.create(
        user=user,
        item=item
    )

def return_item(borrow_record):
    borrow_record.returned_at = timezone.now()
    borrow_record.save()

    item = borrow_record.item
    item.is_borrowed = False
    item.save()

    return borrow_record

def can_fit_plan(user: User, plan_value):
    borrowed = BorrowedItem.objects.filter(user=user, returned_at__isnull=True)
    plan_rules = PLAN_RULES[plan_value]

    # Check max items
    if borrowed.count() > plan_rules['max_items']:
        return False

    # Check allowed tiers
    allowed_tiers = plan_rules['allowed_tiers']
    for b in borrowed:
        if b.item.tier not in allowed_tiers:
            return False

    # Special rule for couture_plus plan
    if plan_value == Plan.COUTURE_PLUS.value:
        couture_count = sum(1 for b in borrowed if b.item.tier == Tier.COUTURE.value)
        if couture_count > 1:
            return False

    return True

def get_eligible_upgrades(user: User):
    current_plan = user.plan
    plan_list = list(Plan)
    current_index = plan_list.index(Plan(current_plan))

    eligible = []
    for plan in plan_list:
        if plan == Plan(current_plan):
            continue  # skip current plan
        if plan_list.index(plan) <= current_index:
            continue  # only upgrades with higher index
        if can_fit_plan(user, plan.value):
            eligible.append(plan.value)
    return eligible

def get_eligible_downgrades(user: User):
    current_plan = user.plan
    plan_list = list(Plan)
    current_index = plan_list.index(Plan(current_plan))

    eligible = []
    for plan in plan_list:
        if plan == Plan(current_plan):
            continue  # skip current plan
        if plan_list.index(plan) >= current_index:
            continue  # only downgrades with lower index
        if can_fit_plan(user, plan.value):
            eligible.append(plan.value)
    return eligible

def change_user_plan(user, new_plan_value):
    if not can_fit_plan(user, new_plan_value):
        raise Exception(f"Cannot change plan to {new_plan_value}, current closet invalid")
    user.plan = new_plan_value
    user.save()
    return user