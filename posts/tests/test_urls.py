from django.test import TestCase, Client

from ..models import User, Post, Group


class PostUrlTests (TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа', slug='test-slug',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_is_author = User.objects.create(username='petroff')
        self.user_other = User.objects.create(username='ivanoff')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_is_author)
        Post.objects.create(
            text='Тестовый пост залогиненного юзера',
            author=self.user_is_author,
            pk=1
        )
        Post.objects.create(
            text='Тестовый пост тестового юзера',
            author=self.user_other,
            pk=2
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'group.html',
            '/new/': 'new.html',
            '/petroff/': 'profile.html',
            '/petroff/1/': 'post.html',
            '/petroff/1/edit/': 'new.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_redirect_guest_if_edit_post(self):
        """Редирект для пользователей, не имеющих прав доступа"""
        response = self.guest_client.get('/ivanoff/2/edit/')
        self.assertRedirects(
            response, ('/auth/login/?next=/ivanoff/2/edit/'))

    def test_ursl_for_authorized(self):
        """Доступность страниц для авторизованных пользователей"""

        urls_codes = {
            '/': 200,
            '/group/test-slug/': 200,
            '/new/': 200,
            '/ivanoff/': 200,
            '/ivanoff/2/': 200,
            '/ivanoff/2/edit/': 404,
            '/petroff/': 200,
            '/petroff/1/': 200,
            '/petroff/1/edit': 301,
        }

        for url, code in urls_codes.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_ursl_for_guest(self):
        """Доступность страниц для неавторизованных пользователей"""
        url_codes = {
            '/': 200,
            '/group/test-slug/': 200,
            '/new/': 302,
            '/ivanoff/': 200,
            '/ivanoff/2/': 200,
            '/ivanoff/2/edit/': 302,
            '/petroff/1/': 200,
            '/petroff/1/edit/': 302,
        }
        for url, code in url_codes.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)
