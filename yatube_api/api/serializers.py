from rest_framework import serializers
from posts.models import Post, Comment, Follow
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ('id', 'text', 'pub_date', 'author', 'image')
        read_only_fields = ('pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        required=False
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        read_only_fields = ('created',)

    def validate(self, data):
        if 'post' not in data and not self.instance:
            raise serializers.ValidationError("Post is required.")
        return data


class FollowSerializer(serializers.ModelSerializer):
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
                message='You are already following this user.'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user == data['following']:
            raise serializers.ValidationError("You cannot follow yourself.")
        return data
