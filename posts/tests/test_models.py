from django.test import TestCase

from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create(username='ivanoff')
        group = Group.objects.create(title='Тестовая группа')
        # Создаём тестовую запись в БД
        cls.post = Post.objects.create(
            group=group,
            author=author,
            text='Тестовый текст длиной более 15 символов',
        )

    def test_verbose_name_post(self):
        """verbose_name в полях поста совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Содержание поста',
            'pub_date': 'Введите дату. По умолчанию будет присвоена текущая.',
            'author': 'Кто написал этот пост?',
            'group': 'К какому сообществу отнести этот пост?',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str_post(self):
        post = PostModelTest.post
        expected_str_post = 'Тестовый текст '
        self.assertEqual(
            post.__str__(), expected_str_post)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        cls.group = Group.objects.create(
            title='ПЛП',
            description='Партия любителей пива',
            slug='test-slug'
        )

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Имя сообщества',
            'description': 'Описание',
            'slug': 'Адрес',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Не более 200 символов',
            'description': 'Все что объединяет членов этого сообщества',
            'slug': 'Уникальный адрес группы, он будет частью URL',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_str_group(self):
        group = GroupModelTest.group
        expected_str_group = 'ПЛП'
        self.assertEqual(
            group.__str__(), expected_str_group)
