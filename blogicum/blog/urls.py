from django.urls import path
from . import views


app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("posts/<int:post_id>/", views.PostDetailView.as_view(),
         name="post_detail"),
    path("posts/create/", views.PostCreateView.as_view(),
         name="create_post"),
    path("posts/<int:post_id>/edit", views.PostUpdateView.as_view(),
         name="edit_post"),
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostListView.as_view(),
        name="category_posts",
    ),
    path(
        "profile/edit_profile/",
        views.UserUpdateView.as_view(),
        name="edit_profile",
    ),
    path("profile/<str:username>/", views.UserPostListView.as_view(),
         name="profile"),
    path("posts/<int:post_id>/comment/", views.add_comment,
         name="add_comment"),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>",
        views.edit_comment,
        name="edit_comment",
    ),
    path("posts/<int:post_id>/delete/", views.PostDeleteView.as_view(),
         name="delete_post"),
    path(
        "posts/<int:post_id>/delete_comment/<comment_id>/",
        views.delete_comment,
        name="delete_comment",
    )
]
