from django.test import TestCase, Client
from django.urls import reverse

from ..models import User, Post, Group


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create(username='ivanoff')
        group = Group.objects.create(
            title='Тестовая группа', slug='test-slug',
            description='Описание тестовой группы'
        )
        # создаем пост 13 постов без группы и 13 в группе
        for i in range(0, 13):
            i = i + 1
            Post.objects.create(
                author=author,
                text=f'Тестовый пост {i}',
            )
            Post.objects.create(
                author=author,
                group=group,
                text='Тестовый пост {i} в тестовой группе',
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        """На первой странице index должно быть 10 постов"""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['page'].object_list), 10)

    def test_second_page_containse_three_records(self):
        """На третей странице index должно быть 6 постов"""
        response = self.client.get(reverse('index') + '?page=3')
        self.assertEqual(len(response.context['page'].object_list), 6)

    def test_first_group_page_containse_ten_records(self):
        """На первой странице группы должно быть 10 постов"""

        response = self.client.get(reverse(
            'group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page'].object_list), 10)

    def test_second_group_page_containse_three_records(self):
        """На второй странице группы должно быть 3 поста"""
        response = self.client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page'].object_list), 3)
