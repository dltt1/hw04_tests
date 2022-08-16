from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description'
        )
        cls.form_data = {
            'text': 'test-post',
            'group': cls.group.id,
        }
        cls.post = Post.objects.create(
            text=cls.form_data['text'],
            author=cls.user,
            group=cls.group,
        )


    def test_create_post(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'test'}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text=self.form_data['text'],
            ).exists()
        )

    def test_edit_post(self):
        self.form_data['text'] = 'test-post1'
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=self.form_data['text'],
            ).exists(),
        )