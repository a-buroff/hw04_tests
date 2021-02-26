from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200, verbose_name="Имя сообщества",
        help_text="Не более 200 символов")
    description = models.TextField(
        verbose_name="Описание",
        help_text="Все что объединяет членов этого сообщества")
    slug = models.SlugField(
        unique=True, verbose_name="Адрес",
        help_text="Уникальный адрес группы, он будет частью URL")

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст", help_text="Содержание поста")
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True,
        help_text="Введите дату. По умолчанию будет присвоена текущая.")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts",
        verbose_name="Автор", help_text="Кто написал этот пост?")
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="posts", verbose_name="Сообщество",
        help_text="К какому сообществу отнести этот пост?")

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-pub_date']

    def __str__(self):
        return str(self.text[:15])
