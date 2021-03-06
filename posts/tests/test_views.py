from django import forms
from django.urls import reverse
from django.test import TestCase, Client
from django.core.paginator import Paginator

from ..models import User, Post, Group


class PostPagesTests (TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create(username='ivanoff')
        user_is_author = User.objects.create(username='petroff')

        group = Group.objects.create(
            title='Тестовая группа', slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.post1 = Post.objects.create(
            author=author,
            text='Тестовый пост stand-alone',
        )
        cls.post2 = Post.objects.create(
            author=author,
            group=group,
            text='Тестовый пост в тестовой группе',
        )
        cls.post3 = Post.objects.create(
            author=user_is_author,
            text='Тестовый пост юзера-автора',
        )

    def setUp(self):
        self.user = User.objects.get(username='petroff')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': 'test-slug'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        posts = response.context['page']
        for post in posts:
            if post.id == PostPagesTests.post1.id:
                self.assertEqual(post.text, 'Тестовый пост stand-alone')
                self.assertEqual(post.author.username, 'ivanoff')
                self.assertEqual(post.group, None)
            if post.id == PostPagesTests.post2.id:
                self.assertEqual(post.text, 'Тестовый пост в тестовой группе')
                self.assertEqual(post.author.username, 'ivanoff')
                self.assertEqual(post.group.title, 'Тестовая группа')
            if post.id == PostPagesTests.post3.id:
                self.assertEqual(post.text, 'Тестовый пост юзера-автора')
                self.assertEqual(post.author.username, 'petroff')
                self.assertEqual(post.group, None)

    def test_group_posts_page_shows_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )

        context_group = response.context['group']
        context_page0 = response.context['page'][0]

        self.assertEqual(
            context_group.title, 'Тестовая группа'
        )
        self.assertEqual(
            context_group.description, 'Описание тестовой группы'
        )
        self.assertEqual(
            context_page0.author.username, 'ivanoff'
        )
        self.assertEqual(
            context_page0.text, 'Тестовый пост в тестовой группе'
        )
        self.assertEqual(
            context_page0.group.title, 'Тестовая группа'
        )

    def test_post_with_no_group_should_not_appear_in_group(self):
        """Шаблон без указания группы не должен попасть в группу"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(
            len(response.context['page']), 1
        )

    def test_new_post_page_shows_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        response = self.authorized_client.get(
            reverse('new_post')
        )

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_shows_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        form_title = "Редактировать запись"
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': 'petroff', 'post_id': PostPagesTests.post3.id})
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['form_title'], form_title)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'ivanoff'})
        )
        self.assertEqual(response.context['author'].username, 'ivanoff')
        self.assertEqual(response.context['viewer'], 'petroff')

        # под ivanoff создано 2 поста, cls.post1 и cls.post2
        self.assertEqual(response.context['paginator'].count, 2)

        self.assertIsInstance(response.context['paginator'], Paginator)

    def test_post_id_shows_correct_context(self):
        """Шаблон отдельного поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': 'ivanoff', 'post_id': PostPagesTests.post2.id})
        )
        self.assertEqual(response.context['author'].username, 'ivanoff')
        self.assertEqual(response.context['viewer'], 'petroff')
