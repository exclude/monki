from django.contrib import admin
from django.core.files import File
from django.conf import settings

from imagekit.admin import AdminThumbnail

from monki.boards.models import (
    Ban,
    Banner,
    Board,
    Category,
    Image,
    Post,
    Video,
)
from monki.boards.forms import ImageForm, VideoForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'order',
    )

    list_editable = (
        'order',
    )


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'category',
        'order',
        'max_replies',
        'max_length',
        'show_id',
        'country_flags',
        'enable_captcha',
        'forced_anonymous',
        'locked',
        'nsfw',
        'created_at',
    )

    list_editable = (
        'category',
        'order',
        'max_replies',
        'max_length',
        'show_id',
        'country_flags',
        'enable_captcha',
        'forced_anonymous',
        'locked',
        'nsfw',
    )


class ImageInline(admin.StackedInline):
    model = Image
    form = ImageForm
    can_delete = False


class VideoInline(admin.StackedInline):
    model = Video
    form = VideoForm
    can_delete = False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'board',
        'subject',
        'name',
        'tripcode',
        'cid',
        'ip_address',
        'created_at',
        'updated_at',
        'bumped_at',
    )

    list_filter = (
        'board',
    )

    search_fields = (
        'subject',
        'name',
        'tripcode',
        'ip_address',
        'cid',
    )

    ordering = (
        '-created_at',
    )

    inlines = (
        ImageInline,
        VideoInline,
    )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'original_filename',
        'admin_thumbnail',
        'size',
        'width',
        'heigth',
        'checksum',
    )

    admin_thumbnail = AdminThumbnail(image_field='thumbnail')

    actions = (
        'turn_potato',
    )

    def turn_potato(self, request, queryset):
        count = 0

        placeholder = str(settings.BASE_DIR / 'static' / 'img' / 'anders_bateva.png')

        with open(placeholder, 'rb') as file:
            for image in queryset:
                image.file = File(file, name=image.original_filename)
                image.save()

                count += 1

        self.message_user(request, '{} image(s) was potato\'d'.format(count))

    turn_potato.short_description = 'Turn into a potato'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'admin_thumbnail',
    )

    admin_thumbnail = AdminThumbnail(image_field='thumbnail')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'admin_thumbnail',
    )

    admin_thumbnail = AdminThumbnail(image_field='image')


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'reason',
        'created_at',
        'expires_at',
        'banned_by',
    )

    search_fields = (
        'ip_address',
    )

    def save_model(self, request, obj, form, change):
        obj.banned_by = request.user
        obj.save()
