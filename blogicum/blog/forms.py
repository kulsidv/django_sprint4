from django import forms

from .models import Comment, Post


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        label="Текст комментария",
    )

    class Meta:
        model = Comment
        fields = ('text', )


class PostForm(forms.ModelForm):
    title = forms.CharField(
        label="Название поста",
    )
    text = forms.CharField(
        label="Текст поста"
    )
    pub_date = forms.DateField(
        label="Дата публикации"
    )
    location = forms.CharField(
        label="Локация"
    )
    category = forms.CharField(
        label="Категория поста"
    )

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category')
