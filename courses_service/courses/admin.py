from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}


class CourseCommentInline(admin.TabularInline):
    model = CourseComment
    readonly_fields = ('author', 'author_name', 'body', 'created')
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class LessonInLine(admin.TabularInline):
    model = Lesson


class ContentInLine(GenericTabularInline):
    model = Content
    ct_field = 'content_type'
    ct_fk_field = 'obj_id'
    extra = 1
    raw_id_fields = ['lesson']


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    inlines = [ContentInLine]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    inlines = [ContentInLine]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    inlines = [ContentInLine]


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    inlines = [ContentInLine]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'category', 'price', 'created', 'moderated', 'draft']
    list_filter = ['category', 'moderated', 'draft']
    search_fields = ['title', 'author_name']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created']
    actions = ['mark_as_moderated']
    inlines = [CourseCommentInline, LessonInLine]
    raw_id_fields = ['category']

    def get_queryset(self, request):
        queryset = Course.objects.all()
        return queryset

    def mark_as_moderated(self, request, queryset):
        queryset.update(moderated=True)
    mark_as_moderated.short_description = "Пометить курс как прошедший модерацию"


class ContentInlineForLesson(admin.TabularInline):
    model = Content
    extra = 1
    fields = ['content_type', 'obj_id', 'order']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'draft', 'moderated']
    list_filter = ['draft', 'moderated', 'course']
    search_fields = ['title', 'course__title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order']
    inlines = [ContentInlineForLesson]
    raw_id_fields = ['course']