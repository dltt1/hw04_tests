from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from http import HTTPStatus

User = get_user_model()


class ContactURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаем постоянного пользователя,группу, пост"""
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
        self.authorized_user.force_login(ContactURLTests.user)
        """Автор"""
        self.user_author = Client()
        self.user_author.force_login(ContactURLTests.post.author)

    def test_index_url(self):
        """Главная страница для неавторизированного пользователя"""
        response = self.guest.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url(self):
        """Страница /group/<slug>/ для неавторизированного пользователя"""
        response = self.guest.get(f'/group/{ContactURLTests.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url(self):
        """Страница profile для неавторизированного пользователя"""
        response = self.guest.get(f'/profile/{ContactURLTests.user.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url(self):
        """Страница /posts/<post_id>/ для неавторизированного пользователя"""
        response = self.guest.get(f'/posts/{ContactURLTests.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_url(self):
        """Страница /posts/<post_id>/edit/ для автора"""
        response = self.user_author.get(
            f'/posts/{ContactURLTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_url_nonauth(self):
        """
        Редирект после редактирования поста для неавт. польз.
        """
        response = self.guest.get(
            f'/posts/{ContactURLTests.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/posts/{ContactURLTests.post.id}/edit/'
            )
        )
        response = self.authorized_user.get(
            f'/posts/{ContactURLTests.post.id}/edit/'
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_url_authoritized(self):
        """Страница /create/ для авторизированного пользователя"""
        response = self.authorized_user.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url(self):
        """Проверка /create/ для неавторизированного пользователя"""
        response = self.guest.get('/create/')
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
        response = self.authorized_user.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_unexisting_page(self):
        """Несуществующая страница, ошибка 404"""
        response = self.guest.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_templates(self):
        """Проверяем шаблоны"""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{ContactURLTests.group.slug}/',
            'posts/profile.html': f'/profile/{ContactURLTests.user.username}/',
            'posts/post_detail.html': f'/posts/{ContactURLTests.post.id}/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertTemplateUsed(response, template)

    def test_guest_redirect_comment(self):
        """Неавт. польз. не иожет писать комментарии"""
        response = self.guest.get(
            f'/posts/{ContactURLTests.post.id}/comment/'
        )
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/posts/{ContactURLTests.post.id}/comment/')
        )

    def test_404_page_not_found(self):
        """Ошибка стр. не существует 404"""
        response = self.guest.get(
            f'/404notfound/'
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )