from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views import generic

from rest_framework import viewsets

from monki.boards.forms import PostForm
from monki.boards.models import Banner, Board, Category, Post
from monki.boards.serializers import (
    BoardSerializer, CategorySerializer, PostSerializer, ThreadSerializer
)


class BoardView(generic.edit.FormMixin, generic.ListView):
    template_name = 'board/index.html'
    form_class = PostForm
    paginate_by = 10

    @cached_property
    def board(self):
        return get_object_or_404(Board, directory=self.kwargs['board'])

    @cached_property
    def thread(self):
        thread = self.kwargs.get('thread')

        if thread:
            return get_object_or_404(Post, pk=thread, parent__isnull=True)

        return None

    def get_banner(self):
        return Banner.objects.order_by('?').first()

    def get_queryset(self):
        if self.thread:
            return self.thread

        return self.board.posts.filter(parent__isnull=True).order_by('-bumped_at')

    def get_paginate_by(self, queryset):
        if self.thread:
            return None

        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'board': self.board,
            'form': self.get_form(),
            'thread': self.thread,
            'banner': self.get_banner(),
        })

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.request = request

        if form.is_valid():
            return self.form_valid(form)

        return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save()

        response = HttpResponseRedirect(self.get_success_url(obj))

        if form.cleaned_data.get('name'):
            response.set_signed_cookie(
                'name',
                form.cleaned_data.get('name'),
                max_age=settings.CSRF_COOKIE_AGE,
                httponly=True,
            )

        return response

    def get_initial(self):
        return {
            'board': self.board,
            'parent': self.thread,
            'password': self.request.COOKIES.get('post_password'),
            'name': self.request.get_signed_cookie('name', None),
        }

    def get_success_url(self, obj):
        return obj.board.get_absolute_url()


class KusabaCompatView(generic.RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        board = self.kwargs.get('board')
        thread = self.kwargs.get('thread')

        if thread:
            return reverse('thread', kwargs={'board': board,
                                             'thread': thread})

        return reverse('board', kwargs={'board': board})


class PostView(generic.DetailView):
    model = Post
    template_name = 'board/_partials/post.html'


class PostDeleteView(UserPassesTestMixin, generic.DeleteView):
    model = Post

    def test_func(self):
        if self.request.user.is_staff:
            return True

        if self.request.get_signed_cookie('cid') == self.get_object().cid:
            return True

    def get_success_url(self):
        return self.get_object().board.get_absolute_url()

    def handle_no_permission(self):
        messages.error(self.request, 'You don\'t own this post')

        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        pk = self.object.pk
        success_url = self.get_success_url()

        self.object.delete()

        messages.success(self.request, 'The Post #{} was deleted successfully.'.format(pk))

        return HttpResponseRedirect(success_url)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class CatalogView(generic.ListView):
    model = Post
    paginate_by = 100
    template_name = 'board/catalog.html'

    @cached_property
    def board(self):
        return get_object_or_404(Board, directory=self.kwargs['board'])

    def get_banner(self):
        return Banner.objects.order_by('?').first()

    def get_queryset(self):
        return (
            self.board.posts
            .filter(parent__isnull=True)
            .order_by('-bumped_at')
        )[:100]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'board': self.board,
            'banner': self.get_banner(),
        })

        return context


class CategoryViewSet(viewsets.ModelViewSet):
    allowed_methods = ['GET']
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None


class BoardViewSet(viewsets.ModelViewSet):
    allowed_methods = ['GET']
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    pagination_class = None


class ThreadViewSet(viewsets.ModelViewSet):
    allowed_methods = ['GET']
    serializer_class = ThreadSerializer
    queryset = Post.objects.filter(parent=None)


class PostViewSet(viewsets.ModelViewSet):
    allowed_methods = ['GET']
    serializer_class = PostSerializer
    queryset = Post.objects.all()
