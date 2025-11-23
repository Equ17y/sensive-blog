from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    list_filter = ('published_at', 'tags')
    search_fields = ('title', 'text')
    raw_id_fields = ('author', 'tags', 'likes')
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Post, PostAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

admin.site.register(Tag, TagAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'published_at')
    list_filter = ('published_at',)
    search_fields = ('text',)
    raw_id_fields = ('post', 'author')

admin.site.register(Comment, CommentAdmin)