from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Post, Comment, Follow

User = get_user_model()


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'image')
    search_fields = ('text', 'author__username')
    list_filter = ('pub_date', 'author')
    empty_value_display = '-пусто-'
    readonly_fields = ('pub_date',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'created')
    search_fields = ('text', 'author__username', 'post__text')
    list_filter = ('created', 'author')
    empty_value_display = '-пусто-'
    readonly_fields = ('created',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')
    search_fields = ('user__username', 'following__username')
    list_filter = ('user', 'following')
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
