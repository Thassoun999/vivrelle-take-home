from django.core.management.base import BaseCommand
import json
import os
from rentals.models import User, Item, BorrowedItem
from django.utils import timezone


class Command(BaseCommand):
    help = "Load initial seed data from seed.json"

    def handle(self, *args, **options):

        # Adjust path to your seed.json
        seed_path = os.path.join(os.path.dirname(__file__), "../../../seed.json")
        with open(seed_path, "r") as f:
            data = json.load(f)

        # 1Load items
        items = data.get("items", [])
        for i in items:
            Item.objects.update_or_create(
                id=i["id"],
                defaults={"name": i["name"], "tier": i["tier"], "is_borrowed": False},
            )

        # Load users
        users = data.get("users", [])
        for u in users:
            user_obj, _ = User.objects.update_or_create(
                id=u["id"],
                defaults={"name": u["name"], "email": u["email"], "plan": u["plan"]},
            )

            # Load borrowed items (closet)
            for item_id in u.get("closet", []):
                try:
                    item_obj = Item.objects.get(id=item_id)
                    BorrowedItem.objects.update_or_create(
                        user=user_obj,
                        item=item_obj,
                        returned_at=None,
                        defaults={"borrowed_at": timezone.now()},
                    )
                    # Mark item as borrowed
                    item_obj.is_borrowed = True
                    item_obj.save()
                except Item.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Item {item_id} not found"))

        self.stdout.write(self.style.SUCCESS("Seed data loaded successfully!"))