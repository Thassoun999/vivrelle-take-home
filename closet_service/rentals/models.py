from django.db import models

# Create your models here.
class Item(models.Model):

    class Tier(models.TextChoices):
        PREMIER = "premier"
        CLASSIQUE = "classique"
        COUTURE = "couture"

    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=255)
    tier = models.CharField(
        max_length=20,
        choices=Tier.choices
    )
    is_borrowed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.tier}) - {'Borrowed' if self.is_borrowed else 'Available'}"

class User(models.Model):
    class Plan(models.TextChoices):
        PREMIER = "premier"
        CLASSIQUE = "classique"
        COUTURE = "couture"
        COUTURE_PLUS = "couture_plus"

    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    plan = models.CharField(
        max_length=20,
        choices=Plan.choices
    )

    def __str__(self):
        return f"{self.name} ({self.plan})"
    
class BorrowedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.returned_at is None
    
    def __str__(self):
        return f"{self.user.name} -> {self.item.name}"
    

#BorrowedItem.objects.filter(
#   user=user,
#    returned_at__isnull=True
#)