from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from posts.models import Post, Comment, Follow, Group

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Group."""
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')
        read_only_fields = ('id', 'slug')


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Post с обработкой изображений."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    image = serializers.ImageField(required=False, allow_null=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Post
        fields = ('id', 'text', 'pub_date', 'author', 'image', 'group')
        read_only_fields = ('pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment с автоматическим определением автора."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        required=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        read_only_fields = ('created',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow с валидацией подписок."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('id', 'user', 'following')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate_following(self, value):
        """Проверка, что пользователь не пытается подписаться на себя."""
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT-аутентификации."""
    username = serializers.CharField(
        error_messages={
            'blank': 'Обязательное поле.',
            'required': 'Обязательное поле.'
        }
    )
    password = serializers.CharField(
        error_messages={
            'blank': 'Обязательное поле.',
            'required': 'Обязательное поле.'
        }
    )
