from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("posts/<int:pk>/",
         views.PostDetailView.as_view(),
         name="post_detail"),
    path("posts/create/", views.PostCreateView.as_view(), name="create"),
    path("posts/<ini:pk>/edit", views.PostUpdateView.as_view(), name="edit"),
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostListView.as_view(),
        name="category_posts",
    ),
    path("profile/<slug:username>/", views.UserPostListView.as_view(),
         name="profile"),
    path("posts/<int:pk>/comment/<int:comment_id>",
         views.add_edit_comment,
         name='add_comment'),
    path("posts/<int:pk>/edit_comment/<int:comment_id>",
         views.add_edit_comment,
         name='edit_comment'),
    path('posts/<int:pk>/delete/', , name='delete'),
    path('posts/<int:pk>/delete_comment/<comment_id>/',
         ,
         name='delete_comment')
]