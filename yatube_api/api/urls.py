from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

from .serializers import CustomTokenObtainPairSerializer
from .views import PostViewSet, CommentViewSet, FollowViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register(
    r'posts/(?P<post_id>[^/.]+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('jwt/create/', TokenObtainPairView.as_view(
        serializer_class=CustomTokenObtainPairSerializer
    ), name='jwt_obtain'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
]
