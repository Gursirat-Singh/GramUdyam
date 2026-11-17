from django.urls import path
from business_advisor import views

app_name = "business_advisor"

urlpatterns = [
    path("", views.advisory_list_view, name="list"),
    path("new/", views.advisory_create_view, name="create"),
    path("<int:pk>/", views.advisory_detail_view, name="detail"),
    path("<int:pk>/select/<int:rec_id>/", views.advisory_select_recommendation_view, name="select_recommendation"),
    path("<int:pk>/delete/", views.advisory_delete_view, name="delete"),
]
