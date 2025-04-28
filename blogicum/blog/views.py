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
    model = Post
    fields = ["title", "text", "pub_date", "location", "category", "image"]
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.object.pk})


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
        return super().get_queryset().filter(category=self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(PostMixin, DetailView):
    template_name = "blog/detail.html"

    def get_queryset(self):
        return super().get_queryset().filter(category__is_published=True)


@login_required
def add_edit_comment(request, pk, comment_id=None):
    if comment_id is not None:
        instance = get_object_or_404(Comment, pk=comment_id)
        if instance.author != request.user:
            return redirect("blog:post_detail", pk=pk)
    else:
        instance = None
    form = CommentForm(request.POST or None, instance=instance)
    context = {"form": form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.post = Post.objects.get(pk=pk)
        instance.author = request.user
        instance.save()
        return redirect("blog:post_detail", pk=pk)
    context["comment_form"] = form
    context["post"] = Post.objects.get(pk=pk)
    context["comments"] = Comment.objects.filter(
        post=context["post"]
    ).order_by("created_at")
    return render(request, "blog/detail.html", context)


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
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")

    def test_func(self):
        return self.get_object().author == self.request.user


@login_required
def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(initial={'text': comment.text})
    if comment.author != request.user:
        return redirect("blog:post_detail", pk=pk)
    if request.method == 'GET':
        return render(request, "blog/comment.html", {"comment": comment,
                                                     "form": form})
    else:
        Comment.objects.get(pk=comment_id).delete()
        return redirect("blog:post_detail", pk=pk)


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
