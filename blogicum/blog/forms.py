from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        label="Текст комментария",
    )

    class Meta:
        model = Comment
        fields = ('text', )
