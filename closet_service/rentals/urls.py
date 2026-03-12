from django.urls import path
from . import views

urlpatterns = [
    path("users/<str:user_id>/closet/", views.get_closet),
    path("users/<str:user_id>/eligible-upgrades/", views.eligible_upgrades),
    path("users/<str:user_id>/eligible-downgrades/", views.eligible_downgrades),
    path("users/<str:user_id>/change-plan/", views.change_plan),
    path("borrow/", views.borrow),
    path("return/", views.return_borrowed_item),
]