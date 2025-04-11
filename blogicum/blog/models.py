from django.db import models
from django.contrib.auth import get_user_model
from core.models import BigModel

User = get_user_model()


class Post(BigModel):
    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="posts")
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Местоположение",
        related_name="post"
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name="post"
    )
    image = models.ImageField('Фото', upload_to='posts_image', blank=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = "-pub_date"

    def __str__(self):
        return self.title


class Category(BigModel):
    title = models.CharField("Заголовок", max_length=256)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        max_length=64,
        unique=True,
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, "
            "дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(BigModel):
    name = models.CharField("Название места", max_length=256)

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.title


class Comment(BigModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="comments")
    text = models.TextField("Текст", blank=False)
    post = models.ForeignKey(
        Post,
        on_delete=models.DO_NOTHING,
        verbose_name="Пост публикации",
        related_name="comments"
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.text[20] + '...'
