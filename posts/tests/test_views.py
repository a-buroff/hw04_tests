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
        Post.objects.create(
            author=author,
            text='Тестовый пост stand-alone',
            pk=0,
        )
        Post.objects.create(
            author=author,
            group=group,
            text='Тестовый пост в тестовой группе',
            pk=1,
        )
        Post.objects.create(
            author=user_is_author,
            text='Тестовый пост юзера-автора',
            pk=2,
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

    def to_remove(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        posts_text_0 = response.context['page'][0].text
        posts_author_0 = response.context['page'][0].author
        # здесь должно получиться None
        posts_group_0 = response.context['page'][0].group

        posts_text_1 = response.context['page'][1].text
        posts_author_1 = response.context['page'][1].author
        posts_group_1 = response.context['page'][1].group

        posts_text_2 = response.context['page'][1].text
        posts_author_2 = response.context['page'][1].author
        posts_group_2 = response.context['page'][1].group

        self.assertEqual(posts_text_0, 'Тестовый пост stand-alone')
        self.assertEqual(posts_author_0.username, 'ivanoff')
        self.assertEqual(posts_group_0, None)

        self.assertEqual(posts_text_1, 'Тестовый пост в тестовой группе')
        self.assertEqual(posts_author_1.username, 'ivanoff')
        self.assertEqual(posts_group_1.title, 'Тестовая группа')

        self.assertEqual(posts_text_2, 'Тестовый пост юзера-автора')
        self.assertEqual(posts_author_2.username, 'petroff')
        self.assertEqual(posts_group_2.title, None)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        posts = response.context['page']
        for post in posts:
            if post.pk == 0:
                self.assertEqual(post.text, 'Тестовый пост stand-alone')
                self.assertEqual(post.author.username, 'ivanoff')
                self.assertEqual(post.group, None)
            if post.pk == 1:
                self.assertEqual(post.text, 'Тестовый пост в тестовой группе')
                self.assertEqual(post.author.username, 'ivanoff')
                self.assertEqual(post.group.title, 'Тестовая группа')
            if post.pk == 2:
                self.assertEqual(post.text, 'Тестовый пост юзера-автора')
                self.assertEqual(post.author.username, 'petroff')
                self.assertEqual(post.group, None)

    def test_group_posts_page_shows_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(
            response.context['group'].title, 'Тестовая группа'
        )
        self.assertEqual(
            response.context['group'].description, 'Описание тестовой группы'
        )
        self.assertEqual(
            response.context['page'][0].author.username, 'ivanoff'
        )
        self.assertEqual(
            response.context['page'][0].text, 'Тестовый пост в тестовой группе'
        )
        self.assertEqual(
            response.context['page'][0].group.title, 'Тестовая группа'
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
                    kwargs={'username': 'petroff', 'post_id': 2})
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
        self.assertEqual(response.context['post_count'], 2)
        self.assertIsInstance(response.context['paginator'], Paginator)

    def test_post_id_shows_correct_context(self):
        """Шаблон отдельного поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': 'ivanoff', 'post_id': 1})
        )
        self.assertEqual(response.context['author'].username, 'ivanoff')
        self.assertEqual(response.context['viewer'], 'petroff')
