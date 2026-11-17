from django.urls import path
from market_insights import views

app_name = "market_insights"

urlpatterns = [
    path("", views.market_overview_view, name="overview"),
    path("observations/new/", views.observation_create_view, name="add_observation"),
    path("observations/<int:pk>/delete/", views.observation_delete_view, name="delete_observation"),
    path("schemes/", views.funding_schemes_list_view, name="schemes_list"),
    path("schemes/<int:pk>/", views.funding_scheme_detail_view, name="scheme_detail"),
]
