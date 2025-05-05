from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from .models import Post, Category, Comment
from .forms import CommentForm


class PostMixin:
    pk_url_kwarg = 'post_id'
    model = Post
    ordering = "-pub_date"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            self.ordering
        )


class PostFormMixin:
    pk_url_kwarg = 'post_id'
    model = Post
    fields = ["title", "text", "pub_date", "location", "category", "image"]
    template_name = "blog/create.html"


class PostListView(PostMixin, ListView):
    template_name = "blog/index.html"

    def get_queryset(self):
        return super().get_queryset().filter(category__is_published=True,
                                             pub_date__lte=timezone.now())


class CategoryPostListView(PostMixin, ListView):
    template_name = "blog/category.html"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return super().get_queryset().filter(category=self.category.pk,
                                             pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(PostMixin, DetailView):
    template_name = "blog/detail.html"

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if self.request.user == post.author:
            return Post.objects.filter(author=self.request.user)
        return super().get_queryset().filter(category__is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = Comment.objects.filter(
            post=self.get_object()).order_by(
            "created_at"
        )
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect("blog:post_detail", post_id=post_id)
    context = {
        "post": post,
        "form": form,
        "comments": Comment.objects.filter(post=post).order_by("created_at")
    }
    return render(request, "blog/detail.html", context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html',
                  {'form': form, 'comment': comment})


class UserPostListView(PostMixin, ListView):
    template_name = "blog/profile.html"

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user == self.user:
            return Post.objects.filter(author=self.user)
        return super().get_queryset().filter(
            author=self.user,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by(self.ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.user
        return context


class PostCreateView(LoginRequiredMixin, PostFormMixin, CreateView):
    def get_success_url(self):
        return reverse_lazy("blog:profile",
                            kwargs={"username": self.object.author})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = Category.objects.filter(
            is_published=True)
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostFormMixin, UpdateView):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect("blog:post_detail", post_id=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"post_id": self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    pk_url_kwarg = 'post_id'
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blog:profile",
                            kwargs={"username": self.object.author})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == 'GET':
        return render(request, "blog/comment.html", {"comment": comment})
    else:
        Comment.objects.get(pk=comment_id).delete()
        return redirect("blog:post_detail", post_id=post_id)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ("username", "first_name", "last_name", "email")
    template_name = "registration/registration_form.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        print(self.object.username)
        return reverse_lazy("blog:profile", kwargs={"username":
                                                    self.object.username})
