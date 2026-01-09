from django.contrib import admin
from .models import Title, Category, Genre


class TitleInLine(admin.TabularInline):
    model = Title
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    ordering = ('name',)
    inlines = (TitleInLine,)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    list_filter = ('name',)
    ordering = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'category',
        'get_genres',
        'year',
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('year', 'category',)
    ordering = ('id',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('genre').select_related('category')

    @admin.display(description='Жанр')
    def get_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])


admin.site.empty_value_display = 'Не задано'