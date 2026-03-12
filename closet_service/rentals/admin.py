from django.contrib import admin
from .models import Item, User, BorrowedItem

# Register your models here.

admin.site.register(Item)
admin.site.register(User)

class BorrowedItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'borrowed_at', 'returned_at')
    readonly_fields = ('borrowed_at',)

admin.site.register(BorrowedItem, BorrowedItemAdmin)

# admin
# thassoun000@gmail.com
# Roflcopter$999