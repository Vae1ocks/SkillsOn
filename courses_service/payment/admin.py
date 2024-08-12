from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'price', 'created', 'completed')

    search_fields = ('user', 'course__name')

    list_filter = ('completed', 'created')

    list_editable = ('completed',)

    ordering = ('-created',)

    fields = ('user', 'course', 'price', 'completed')

    readonly_fields = ('created',)


admin.site.register(Order, OrderAdmin)
