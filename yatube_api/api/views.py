from rest_framework import (
    pagination,
    viewsets,
    permissions,
    filters
)
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from posts.models import Post, Follow, Group
from .serializers import (
    PostSerializer,
    CommentSerializer,
    FollowSerializer,
    GroupSerializer
)

User = get_user_model()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр списка групп и детальной информации о группе."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]


class PostViewSet(viewsets.ModelViewSet):
    """Полный CRUD для постов с пагинацией."""
    pagination_class = pagination.LimitOffsetPagination
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        """Автоматическое сохранение автора поста."""
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD для комментариев к конкретному посту."""
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Получение комментариев только для указанного поста."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        # return Comment.objects.filter(post=post).select_related('author')
        return post.comments.select_related('author')

    def perform_create(self, serializer):
        """Автоматическое связывание комментария с постом и автором."""
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Управление подписками на других пользователей."""
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        """Получение подписок текущего пользователя."""
        return Follow.objects.filter(
            user=self.request.user).select_related('following')

    def perform_create(self, serializer):
        """Автоматическое сохранение подписки для текущего пользователя."""
        serializer.save(user=self.request.user)
