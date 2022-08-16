from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group

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
        self.authoritized_user = Client()
        self.authoritized_user.force_login(self.user)
        """Автор"""
        self.user_author = Client()
        self.user_author.force_login(self.post.author)

    def test_index_url(self):
        """Главная страница для неавторизированного пользователя"""
        response = self.guest.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url(self):
        """Страница /group/<slug>/ для неавторизированного пользователя"""
        response = self.guest.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        """Страница profile для неавторизированного пользователя"""
        response = self.guest.get('/profile/test/')
        self.assertEqual(response.status_code, 200)

    def test_posts_url(self):
        """Страница /posts/<post_id>/ для неавторизированного пользователя"""
        post_id = self.post.id
        response = self.guest.get(f'/posts/{post_id}/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url(self):
        """Страница /posts/<post_id>/edit/ для автора"""
        post_id = self.post.id
        response = self.user_author.get(f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url(self):
        """Редирект после редактирования поста для неавт. польз."""
        post_id = self.post.id
        response = self.guest.get(f'/posts/{post_id}/edit/', follow=True)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{post_id}/edit/'))
        response = self.authoritized_user.get(f'/posts/{post_id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_url_authoritized(self):
        """Страница /create/ для авторизированного пользователя"""
        response = self.authoritized_user.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_url(self):
        """Проверка /create/ для неавторизированного пользователя"""
        response = self.guest.get('/create/')
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
        response = self.authoritized_user.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_unexisting_page(self):
        """Несуществующая страница, ошибка 404"""
        response = self.guest.get('/unexisting_page/')
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        """Проверяем шаблоны"""
        post_id = self.post.id
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/test/',
            'posts/post_detail.html': f'/posts/{post_id}/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authoritized_user.get(url)
                self.assertTemplateUsed(response, template)
