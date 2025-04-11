from django.contrib import admin

from .models import Category, Location, Post, Comment

admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug')
    search_fields = ('title', 'slug')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name')
    search_fields = ('name')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'pub_date', 'author',
                    'location', 'category')
    search_fields = ('title', 'pub_date', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at', 'author',
                    'is_published')
    search_fields = ('created_at', 'text', 'author')
