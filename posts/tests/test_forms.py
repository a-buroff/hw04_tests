from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostCreateFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='petroff')
        self.group = Group.objects.create(
            title='Тестовая группа', slug='test-slug'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        Post.objects.create(
            group=self.group,
            text='Тестовый текст1',
            author=self.user
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст'}
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась тестовая запись
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст2'
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'petroff', 'post_id': 1}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'post',
                kwargs={'username': 'petroff', 'post_id': 1}
            )
        )
        # Проверяем, что число постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст2',
            ).exists()
        )
