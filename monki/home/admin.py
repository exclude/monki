from django.contrib import admin

from monki.home.models import (
    New,
    FAQ,
    Rule,
)


@admin.register(New)
class NewAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_at',
        'updated_at',
        'author',
    )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'order',
    )

    list_editable = (
        'order',
    )


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'order',
    )

    list_editable = (
        'order',
    )
