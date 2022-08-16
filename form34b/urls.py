from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.is_server_up),
    path('candidates', views.candidates),
    path('candidates/<int:id>', views.candidate),
    path('forms', views.forms),
    path('forms/<int:id>', views.form),
    path('tallies', views.forms_summary),
]