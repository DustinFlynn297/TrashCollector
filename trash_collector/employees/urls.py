from django.urls import path

from . import views

# TODO: Determine what distinct pages are required for the user stories, add a path for each in urlpatterns

app_name = "employees"
urlpatterns = [
    path('', views.index, name="index"),
    path('new/', views.create, name='create'),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('trash_picked_up/<int:customer_id>/', views.trash_picked_up, name="trash_picked_up"),
    path('filter_by_day/', views.filter_by_day, name="filter_by_day"),
    path('customer_info/<int:customer_id>/', views.customer_info, name="customer_info"),
]