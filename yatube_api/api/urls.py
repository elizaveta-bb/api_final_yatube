from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

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

API_VERSION = 'v1/'

urlpatterns = [
    path(API_VERSION + '', include(router.urls)),
    path(API_VERSION + 'auth/', include('djoser.urls')),
    path(API_VERSION + 'auth/', include('djoser.urls.jwt')),

    path(API_VERSION + 'jwt/create/',
         TokenObtainPairView.as_view(), name='jwt_obtain'),
    path(API_VERSION + 'jwt/refresh/',
         TokenRefreshView.as_view(), name='jwt_refresh'),
    path(API_VERSION + 'jwt/verify/',
         TokenVerifyView.as_view(), name='jwt_verify'),
]
