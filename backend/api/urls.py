from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/me/', views.get_current_user, name='current_user'),
    path('swappable-slots/', views.get_swappable_slots, name='swappable_slots'),
    path('swap-request/', views.create_swap_request, name='create_swap_request'),
    path('swap-response/<int:request_id>/', views.respond_to_swap, name='respond_to_swap'),
    path('swap-requests/', views.get_swap_requests, name='get_swap_requests'),
]