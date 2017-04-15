import io
import os
import random
import subprocess
import tempfile
import time

from django.core.files import File as FileStorage
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from imagekit.models import ImageSpecField


class Category(models.Model):
    name = models.CharField(
        verbose_name=_('Category name'),
        max_length=90,
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_('Order'),
        default=0,
    )

    class Meta:
        ordering = (
            'order',
            'name',
        )

        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Board(models.Model):
    category = models.ForeignKey(
        to='Category',
        related_name='boards'
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=32,
    )

    directory = models.CharField(
        verbose_name=_('Board directory'),
        max_length=8,
        db_index=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9]+$',
                message=_('Only letters (lower-case) and numbers are allowed here')
            ),
        ]
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_('Order'),
        default=0,
    )

    default_name = models.CharField(
        verbose_name=_('Default Name'),
        max_length=32,
        default='Anonymous',
    )

    max_replies = models.PositiveIntegerField(
        verbose_name=_('Max Replies'),
        default=200,
    )

    max_length = models.PositiveIntegerField(
        verbose_name=_('Max Lenght'),
        default=2048,
    )

    show_id = models.BooleanField(
        verbose_name=_('Show ID'),
        default=False,
    )

    country_flags = models.BooleanField(
        verbose_name=_('Country Flags'),
        default=False,
    )

    enable_captcha = models.BooleanField(
        verbose_name=_('Enable Captcha'),
        default=False,
    )

    forced_anonymous = models.BooleanField(
        verbose_name=_('Forced Anonymous'),
        default=False,
    )

    locked = models.BooleanField(
        verbose_name=_('Locked'),
        default=False,
    )

    nsfw = models.BooleanField(
        verbose_name=_('NSFW'),
        default=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now=True,
    )

    class Meta:
        ordering = (
            'order',
            'name',
        )

        verbose_name = _('Board')
        verbose_name_plural = _('Boards')

    def __str__(self):
        return '/{0}/ - {1}'.format(self.directory, self.name)

    def get_absolute_url(self):
        return reverse_lazy('board', kwargs={'board': self.directory})

    @property
    def last_post(self):
        t = self.posts.last()

        if not t:
            return None

        return t.created_at


class PostQuerySet(models.QuerySet):

    def last_n(self):
        objects = self.reverse()[:3][::-1]

        if objects:
            return objects

        return None


class PostManager(models.Manager):

    def get_queryset(self):
        return (
            PostQuerySet(self.model, using=self._db)
            .select_related('image', 'video')
            .annotate(num_replies=Count('replies'))
        )

    def last_n(self):
        return self.get_queryset().last_n()


class Post(models.Model):
    board = models.ForeignKey(
        to='Board',
        related_name='posts',
    )

    parent = models.ForeignKey(
        to='self',
        blank=True,
        null=True,
        related_name='replies',
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=90,

        blank=True,
        null=True,
    )

    tripcode = models.CharField(
        verbose_name=_('Tripcode'),
        max_length=90,
        blank=True,
        null=True,
    )

    email = models.EmailField(
        verbose_name=_('E-Mail'),
        blank=True,
        null=True,
    )

    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    subject = models.CharField(
        verbose_name=_('Subject'),
        max_length=90,
        blank=True,
        null=True,
    )

    message = models.TextField(
        verbose_name=_('Message'),
        blank=True,
        null=True,
    )

    message_html = models.TextField(
        verbose_name=_('Message as HTML'),
        blank=True,
        null=True,
        editable=False,
    )

    password = models.CharField(
        verbose_name=_('Password'),
        max_length=90,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP Address'),
        unpack_ipv4=True,
    )

    user_agent = models.CharField(
        verbose_name=_('User-Agent'),
        max_length=2048,
    )

    cid = models.CharField(
        verbose_name=_('CID'),
        max_length=90,
        help_text='Cookie based unique identifier for user.'
    )

    stickied = models.BooleanField(
        verbose_name=_('Stickied'),
        default=False,
    )

    locked = models.BooleanField(
        verbose_name=_('locked'),
        default=False,
    )

    reviewed = models.BooleanField(
        verbose_name=_('Reviewed'),
        default=False,
    )

    visible = models.BooleanField(
        verbose_name=_('Visible'),
        default=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Updated at'),
        auto_now=True,
    )

    bumped_at = models.DateTimeField(
        verbose_name=_('Bumped at'),
        auto_now_add=True,
    )

    objects = PostManager()

    class Meta:
        ordering = ('created_at', )

        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return 'No. {}'.format(self.pk)

    def get_absolute_url(self):
        if not self.parent:
            return reverse_lazy('thread', kwargs={'board': self.board.directory, 'thread': self.pk})

        return reverse_lazy('thread', kwargs={'board': self.board.directory, 'thread': self.parent.pk}) + '#post-{}'.format(self.pk)

    # def clean(self):
    #     if self.image is not None and self.video is not None:
    #         raise

    def save(self, *args, **kwargs):
        if self.body_not_empty:
            from monki.boards.formatting import markdown  # NOQA

            self.message_html = markdown(self.message)

        super().save(*args, **kwargs)

    @property
    def has_file(self):
        return self.content_object is not None

    @property
    def body_not_empty(self):
        return self.message is not None

    @property
    def content_object(self):
        if hasattr(self, 'image'):
            return self.image
        elif hasattr(self, 'video'):
            return self.video

        return None


def upload_to(instance, filename):
    now = timezone.now()

    filename, ext = os.path.splitext(filename)

    filename = 'uploads/{year}/{month}/{filename}{rand}{ext}'.format(
        year=now.year,
        month=now.month,
        filename=int(time.time()),
        rand=random.randint(10, 99),
        ext=ext
    )

    return filename


class File(models.Model):
    post = models.OneToOneField(
        to=Post,
    )

    original_filename = models.CharField(
        verbose_name=_('Original Filename'),
        max_length=256,
    )

    heigth = models.IntegerField(
        verbose_name=_('Heigth'),
    )

    width = models.IntegerField(
        verbose_name=_('Width'),
    )

    size = models.IntegerField(
        verbose_name=_('Size'),
    )

    checksum = models.CharField(
        verbose_name=_('SHA1 checksum'),
        max_length=40,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.filename

    @property
    def playable(self):
        raise NotImplemented

    @property
    def html(self):
        raise NotImplemented

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class Image(File):
    file = models.ImageField(
        verbose_name=_('File'),
        upload_to=upload_to,
        height_field='heigth',
        width_field='width',
    )

    thumbnail = ImageSpecField(
        source='file',
        id='boards:thumbnail',
    )

    @property
    def playable(self):
        _, ext = os.path.splitext(self.file.name)

        return ext == '.gif'

    @property
    def html(self):
        if self.playable:
            tag = '<img width="{thumbnail.width}" height="{thumbnail.height}" src="{thumbnail.url}" class="expandable gif" data-alt="{file.url}">'
        else:
            tag = '<img width="{thumbnail.width}" height="{thumbnail.height}" src="{thumbnail.url}" class="expandable" data-alt="{file.url}">'

        return tag.format(thumbnail=self.thumbnail, file=self.file)


class Video(File):
    file = models.FileField(
        verbose_name=_('File'),
        upload_to=upload_to,
    )

    image = models.ImageField(
        verbose_name=_('Image'),
        upload_to=upload_to,
        height_field='heigth',
        width_field='width',
    )

    thumbnail = ImageSpecField(
        source='image',
        id='boards:thumbnail',
    )

    @property
    def playable(self):
        return True

    @property
    def html(self):
        tag = '<img width="{thumbnail.width}" height="{thumbnail.height}" src="{thumbnail.url}" class="expandable" data-mode="video" data-alt="{file.url}" />'

        return tag.format(thumbnail=self.thumbnail, file=self.file)

    def save(self, *args, **kwargs):
        # TODO: Move to Python-RQ in future
        fd, output_file = tempfile.mkstemp()

        input_file = self.file.file.temporary_file_path()

        subprocess.call([
            'avconv',
            '-i', input_file,  # input file (video)
            '-v', 'quiet',     # shhhhh
            '-r', '1',         # frame rate
            '-vframes', '1',   # frames to output
            '-ss', '1',        # timestamp
            '-f', 'image2',    # format
            '-y',              # overwrite output
            output_file        # output file (image)
        ], stdout=subprocess.DEVNULL)

        f = io.open(fd, mode='rb')
        self.image = FileStorage(f, name='screenshot.jpg')

        super().save(*args, **kwargs)


class Banner(models.Model):
    image = models.ImageField(
        verbose_name=_('Image'),
        upload_to='banners/'
    )

    nsfw = models.BooleanField(
        verbose_name=_('NSFW'),
        default=True,
    )

    def __str__(self):
        return '{}'.format(self.image.name)


class Ban(models.Model):
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP Address'),
    )

    reason = models.CharField(
        verbose_name=_('Reason'),
        max_length=255,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
        verbose_name=_('Expired at'),
        blank=True,
        null=True,
    )

    banned_by = models.ForeignKey(
        verbose_name=_('Banned by'),
        to=settings.AUTH_USER_MODEL,
        editable=False,
    )

    def __str__(self):
        return '{}'.format(self.ip_address)
