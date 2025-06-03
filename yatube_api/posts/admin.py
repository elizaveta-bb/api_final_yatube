from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Post, Comment, Follow, Group

User = get_user_model()


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    empty_value_display = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'image')
    search_fields = ('text', 'author__username')
    list_filter = ('pub_date', 'author')
    empty_value_display = '-пусто-'
    readonly_fields = ('pub_date',)
    raw_id_fields = ('author',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'created')
    search_fields = ('text', 'author__username', 'post__text')
    list_filter = ('created', 'author')
    empty_value_display = '-пусто-'
    readonly_fields = ('created',)
    raw_id_fields = ('author', 'post')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user', 'following')
    empty_value_display = '-пусто-'
    raw_id_fields = ('user', 'following')
