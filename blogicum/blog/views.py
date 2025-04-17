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

from .models import Post, Category, Comment
from .forms import CommentForm


class PostMixin:
    model = Post
    ordering = "-created_at"
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True
        )
        for post in queryset:
            post.comment_count = Comment.objects.filter(post=post).count()
        return queryset


class PostFormMixin:
    model = Post
    exclude = ("author", "is_published", "created_at")
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["pk"]})


class PostListView(PostMixin, ListView):
    template_name = "index.html"

    def get_queryset(self):
        return super().get_queryset().filter(category__is_published=True)


class CategoryPostListView(PostMixin, ListView):
    template_name = "category.html"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return super().get_queryset().filter(category=self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(PostMixin, DetailView):
    template_name = "blog/detail.html"

    def get_queryset(self):
        return super().get_queryset().filter(category__is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm
        context["comments"] = Comment.objects.filter(
            post=self.get_object()).order_by(
            "created_at"
        )
        return context


def add_edit_comment(request, pk, comment_id):
    if not request.user.is_authenticated:
        redirect("registration/login.html")
    if comment_id is not None:
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.author != request.user:
            redirect("blog:post_detail", pk=pk)
    else:
        instance = None
    form = CommentForm(request.POST or None, instance=instance)
    context = {"form": form}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = Post.objects.get(pk=pk)
        comment.author = request.user
        comment.save()
        return redirect("blog:post_detail", pk=pk)
    context["comment_form"] = form
    context["post"] = Post.objects.get(pk=pk)
    return render(request, "blog/detail.html", context)


class UserPostListView(PostMixin, ListView):
    template_name = "blog/profile.html"

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user == self.user:
            return Post.objects.filter(author=self.user)
        return super().get_queryset().filter(
            author=self.user,
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.user
        return context


class PostCreateView(LoginRequiredMixin, PostFormMixin, CreateView):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["category"].queryset = Category.objects.filter(
            is_published=True)
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostFormMixin, UpdateView):
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            return redirect("blog:post_detail",
                            kwargs={"pk": self.kwargs["pk"]})
        return obj


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/detail.html"
    success_url = reverse_lazy("blog:index")

    def test_func(self):
        return self.get_object().author == self.request.user


def delete_comment(request, pk, comment_id):
    if not request.user.is_authenticated:
        redirect("registration/login.html")
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        redirect("blog:post_detail", pk=pk)
    Comment.objects.get(pk=comment_id).delete()
    return redirect("blog:post_detail", pk=pk)
