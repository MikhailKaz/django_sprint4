from datetime import datetime, timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.views.generic.edit import ModelFormMixin

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


User = get_user_model()


def get_posts(author: AbstractUser = None):
    """Вспомогательная функция для получения постов."""
    condition = Q(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(timezone.utc),
    )
    if author is not None and not author.is_anonymous:
        query = Post.objects.filter(Q(author__pk=author.pk) | condition)
    else:
        query = Post.objects.filter(condition)
    return (
        query.select_related('author', 'category', 'location')
        .annotate(comment_count=Count('comments'))
        # https://code.djangoproject.com/ticket/32811
        .order_by('-pub_date')
    )


#
# Профили
#


class ProfilePage(ListView):
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', self.request.user.username)
        self.profile = get_object_or_404(User, username=username)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return get_posts(self.request.user).filter(author__pk=self.profile.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'profile': self.profile,
        })
        return context


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'email', 'username']

    def get_success_url(self):
        url = reverse('blog:edit_profile')
        return f'{url}?success=1'

    def get_object(self, queryset=None):
        return self.request.user


#
# Посты
#


class BlogIndexPage(ListView):
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_posts()


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return get_posts(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class UpdatePostView(UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != self.request.user:
            return redirect(reverse('blog:post_detail', args=[kwargs['pk']]))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != self.request.user:
            return redirect(reverse('blog:post_detail',
                                    args=[self.kwargs['pk']]))
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return get_posts(self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_queryset(self):
        return (
            get_posts(self.request.user)
            .filter(author__pk=self.request.user.pk)
        )

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


#
# Комментарии
#


class CreateCommentView(
    LoginRequiredMixin,
    generic.detail.SingleObjectMixin,
    generic.FormView
):
    model = Post
    form_class = CommentForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.pk])


class EditCommentViewBase(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_pk']])

    def get_queryset(self):
        return self.model.objects.filter(
            post__pk=self.kwargs['post_pk'],
            author=self.request.user
        ).select_related('author')


class UpdateCommentView(EditCommentViewBase, UpdateView):
    form_class = CommentForm


class DeleteCommentView(EditCommentViewBase, DeleteView):
    pass


#
# Категории
#


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return get_posts().filter(category__pk=self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
