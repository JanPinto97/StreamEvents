from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list_view, name='event_list'),                         # Llistat d'esdeveniments
    path('create/', views.event_create_view, name='event_create'),              # Crear esdeveniment
    path('<int:pk>/', views.event_detail_view, name='event_detail'),            # Detall d'esdeveniment
    path('<int:pk>/edit/', views.event_update_view, name='event_update'),       # Editar esdeveniment
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),     # Eliminar esdeveniment
    path('my-events/', views.my_events_view, name='my_events'),                 # Els meus esdeveniments
    path('category/<str:category>/', views.events_by_category_view, name='events_by_category'),  # Per categoria
    
    # Etiquetes
    path('tags/', views.tag_cloud_view, name='tag_cloud'),
    path('tags/<str:tag>/', views.events_by_tag_view, name='events_by_tag'),
    path('api/tags-autocomplete/', views.tags_autocomplete_view, name='tags_autocomplete'),

]
