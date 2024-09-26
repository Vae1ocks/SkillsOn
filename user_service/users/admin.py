from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Chat, Message


class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "balance",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "profile_picture",
                    "about_self",
                    "categories_liked",
                    "balance",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


admin.site.register(User, UserAdmin)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ["author", "text", "created"]
    readonly_fields = ["created"]


class ChatAdmin(admin.ModelAdmin):
    list_display = ["id", "get_users"]
    filter_horizontal = ("users",)
    inlines = [MessageInline]

    def get_users(self, obj):
        return ", ".join([user.email for user in obj.users.all()])


admin.site.register(Chat, ChatAdmin)
