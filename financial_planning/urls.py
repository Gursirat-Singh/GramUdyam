from django.urls import path
from financial_planning import views

app_name = "financial_planning"

urlpatterns = [
    path("", views.financial_plan_list_view, name="list"),
    path("new/", views.financial_plan_create_view, name="create"),
    path("<int:pk>/", views.financial_plan_detail_view, name="detail"),
    path("<int:pk>/edit/", views.financial_plan_edit_view, name="edit"),
    path("<int:pk>/delete/", views.financial_plan_delete_view, name="delete"),
    path("<int:pk>/expenses/add/", views.financial_expense_add_view, name="add_expense"),
    path("<int:pk>/expenses/<int:expense_id>/delete/", views.financial_expense_delete_view, name="delete_expense"),
]
