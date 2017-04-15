from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class New(models.Model):
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=130,
    )

    text = models.TextField(
        verbose_name=_('Text'),
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now=True,
    )

    author = models.ForeignKey(
        verbose_name=_('Author'),
        to=settings.AUTH_USER_MODEL,
        editable=False,
    )

    class Meta:
        verbose_name = 'New'
        verbose_name_plural = 'News'
        ordering = ('-created_at', )

    def __str__(self):
        return '{}'.format(self.title)


class FAQ(models.Model):
    question = models.TextField(
        verbose_name=_('Question'),
    )

    answer = models.TextField(
        verbose_name=_('Answer'),
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_('Order'),
        default=0,
    )

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ('order', )

    def __str__(self):
        return '{}'.format(self.question)


class Rule(models.Model):
    text = models.TextField(
        verbose_name=_('Text'),
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_('Order'),
        default=0,
    )

    class Meta:
        verbose_name = 'Rule'
        verbose_name_plural = 'Rules'
        ordering = ('order', )

    def __str__(self):
        return '{}'.format(self.text)
