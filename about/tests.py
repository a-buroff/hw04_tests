from django.urls import reverse
from django.test import TestCase, Client


class PostPagesTests (TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_bout_is_accessible_for_guest(self):
        """Адреса about/author и about/tech доступны для guest"""
        response_author = self.guest_client.get(reverse('about:author'))
        response_tech = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response_author.status_code, 200)
        self.assertEqual(response_tech.status_code, 200)

    def test_about_is_using_correct_views_and_templates(self):
        """Адреса author и tech используют правильные view и шаблоны"""
        template_author = 'about/about_author.html'
        template_tech = 'about/about_tech.html'
        response_author = self.guest_client.get('/about/author/')
        response_tech = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response_author, template_author)
        self.assertTemplateUsed(response_tech, template_tech)
