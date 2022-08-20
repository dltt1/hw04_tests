import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, Client, override_settings
from posts.models import Post, Group
from django.urls import reverse
from django import forms

from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаем пользователя,группу, пост"""
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        """Пользователь"""
        self.guest = Client()
        """Авторизированный пользователь"""
        self.authorized_user = Client()
        self.authorized_user.force_login(PostViewTests.user)
        """Автор"""
        self.user_author = Client()
        self.user_author.force_login(PostViewTests.post.author)

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': PostViewTests.group.slug}
                )
            ),
            'posts/profile.html': (
                reverse(
                    'posts:profile',
                    kwargs={'username': PostViewTests.user.username}
                )
            ),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': str(PostViewTests.post.id)}
                )
            ),
        }
        for template, reverse_name in templates_names.items():
            with self.subTest(template=template):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostViewTests.user)
        self.assertEqual(post.text, PostViewTests.post.text)
        self.assertEqual(post.group, PostViewTests.post.group)

    def test_post_create_page_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_user.get(reverse('posts:post_create'))
        is_edit = response.context['is_edit']
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form = response.context['form'].fields[value]
                self.assertIsInstance(form, expected)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn('is_edit', response.context)
        is_edit = response.context['is_edit']
        self.assertIsInstance(is_edit, bool)
        self.assertEqual(is_edit, False)

    def test_post_edit_page_context(self):
        """
        Шаблон post_edit сформирован
        с правильным контекстом.
        """
        response = self.user_author.get(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': str(
                        PostViewTests.post.id)}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form = response.context['form'].fields[value]
                self.assertIsInstance(form, expected)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn('is_edit', response.context)
        is_edit = response.context['is_edit']
        self.assertIsInstance(is_edit, bool)
        self.assertEqual(is_edit, True)

    def test_index_page(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest.get(reverse('posts:index'))
        self.check_context_contains_page_or_post(response.context)

    def test_group_list_page(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostViewTests.group.slug}))
        self.check_context_contains_page_or_post(response.context)
        self.assertEqual(
            response.context.get('group').description,
            PostViewTests.group.description
        )
        self.assertEqual(
            response.context.get('group').slug,
            PostViewTests.group.slug
        )
        self.assertEqual(
            response.context.get('group').title,
            PostViewTests.group.title
        )

    def test_profile_page(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostViewTests.user.username}))
        self.check_context_contains_page_or_post(response.context)

        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], PostViewTests.user)

    def test_post_detail_page(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': str(
                        PostViewTests.post.id)}))
        self.check_context_contains_page_or_post(response.context, post=True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание'
        )
        """Создаем 13 постов для паджинатора."""
        cls.posts = [
            Post(
                text=f'text {num}',
                author=cls.user,
                group=cls.group
            )
            for num in range(1, 14)
        ]
        Post.objects.bulk_create(cls.posts)

    def test_index_paginator(self):
        """Тестируем 1 страницу паджинатора страницы index."""
        response = self.guest.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_paginator(self):
        """Тестируем 2 страницу паджинатора страницы index."""
        response = self.guest.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_paginator(self):
        """Тестируем паджинатор страницы group_list."""
        response = self.guest.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_paginator(self):
        """Тестируем паджинатор страницы profile."""
        response = self.guest.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)
