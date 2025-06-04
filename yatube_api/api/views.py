from rest_framework import pagination, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from posts.models import Post, Comment, Follow, Group
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()

    def create(self, request, *args, **kwargs):
        """Создание нового поста с автором-текущим пользователем."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        """Автоматическое сохранение автора поста."""
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """Обновление поста с проверкой авторства."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance.author != request.user:
            return Response(
                {"detail": "Вы не являетесь автором этого поста"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление поста с проверкой авторства."""
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "Вы не можете удалить чужой пост"},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD для комментариев к конкретному посту."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Получение комментариев только для указанного поста."""
        post_id = self.kwargs.get('post_id')
        if not post_id:
            return Comment.objects.none()
        return Comment.objects.filter(post_id=post_id).select_related('author')

    def create(self, request, *args, **kwargs):
        """Создание комментария к посту с валидацией."""
        post_id = int(kwargs.get('post_id', -1))
        if not post_id:
            return Response(
                {"detail": "Не указан ID поста"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not Post.objects.filter(id=post_id).exists():
            return Response(
                {"detail": "Пост не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['post'] = post_id
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        """Автоматическое связывание комментария с постом и автором."""
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)

    def update(self, request, *args, **kwargs):
        """Обновление комментария с проверкой авторства."""
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "Вы не можете редактировать чужой комментарий"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление комментария с проверкой авторства."""
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "Вы не можете удалить чужой комментарий"},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    """Управление подписками на других пользователей."""
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Получение подписок текущего пользователя с поиском."""
        search_query = self.request.query_params.get('search', '')
        queryset = Follow.objects.filter(
            user=self.request.user,
            following__username__icontains=search_query
        ).select_related('following')
        return queryset

    def create(self, request, *args, **kwargs):
        """Создание новой подписки с валидацией."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        following = serializer.validated_data['following']
        if request.user == following:
            return Response(
                {"following": "Вы не можете подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Follow.objects.filter(user=request.user,
                                 following=following).exists():
            return Response(
                {"following": "Вы уже подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        """Автоматическое сохранение подписки для текущего пользователя."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Получение списка подписчиков текущего пользователя."""
        followers = Follow.objects.filter(
            following=request.user
        ).select_related('user')
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def following(self, request):
        """Получение списка пользователей, на которых подписан текущий."""
        following = self.get_queryset()
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
