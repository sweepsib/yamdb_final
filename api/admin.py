from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'pub_date', 'author',)
    search_fields = ('author',)
    list_filter = ('pub_date', 'review',)
    empty_value_display = 'No data'


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'score', 'pub_date', 'author',)
    search_fields = ('title', 'author',)
    list_filter = ('pub_date', 'title',)
    empty_value_display = 'No data'


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category', 'genre_list', 'description',)
    search_fields = ('name', 'year', 'category', 'genre',)
    list_filter = ('year', 'category', 'genre',)
    empty_value_display = 'No data'

    def genre_list(self, obj):
        return obj.values_list('genre__name', flat=True)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'role', 'username', 'bio',
    )
    search_fields = ('first_name', 'last_name', 'email', 'role', 'username',)
    list_filter = ('role', 'first_name', 'username', 'last_name',)
    empty_value_display = 'No data'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(User, UserAdmin)
