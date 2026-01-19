from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title, User

MAX_DISPLAY_LENGTH = 30


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio_info',
        'role',
        'is_staff_display',
        'is_superuser_display',
    )
    list_editable = ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role',)

    @admin.display(description='Инфо')
    def bio_info(self, obj):
        return obj.bio[:MAX_DISPLAY_LENGTH]

    @admin.display(boolean=True, description='staff')
    def is_staff_display(self, obj):
        return obj.is_staff

    @admin.display(boolean=True, description='super')
    def is_superuser_display(self, obj):
        return obj.is_superuser


admin.site.register(Review)
admin.site.register(Comment)


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
