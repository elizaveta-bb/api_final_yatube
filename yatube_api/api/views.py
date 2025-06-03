from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
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
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'group'
        ).prefetch_related('comments')

        author_username = self.request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)

        group_slug = self.request.query_params.get('group')
        if group_slug:
            queryset = queryset.filter(group__slug=group_slug)

        return queryset.order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого поста")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужой пост")
        instance.delete()

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(
            comments,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return Comment.objects.filter(post=post).select_related('author')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied(
                "Вы не можете редактировать чужой комментарий"
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужой комментарий")
        instance.delete()


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(
            user=self.request.user
        ).select_related('following')

    def perform_create(self, serializer):
        following = serializer.validated_data['following']
        if self.request.user == following:
            raise ValidationError(
                {"following": "Вы не можете подписаться на самого себя"}
            )
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Получить список подписчиков текущего пользователя."""
        followers = Follow.objects.filter(
            following=request.user
        ).select_related('user')
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def following(self, request):
        """Получить список подписок текущего пользователя."""
        following = self.get_queryset()
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)
