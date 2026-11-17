from django.urls import path
from reports import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list_view, name="list"),
    path("new/", views.report_create_view, name="create"),
    path("compare/", views.scenario_comparison_view, name="compare"),
    path("<int:pk>/", views.report_detail_view, name="detail"),
    path("<int:pk>/pdf/", views.report_pdf_export_view, name="export_pdf"),
    path("<int:pk>/delete/", views.report_delete_view, name="delete"),
]
