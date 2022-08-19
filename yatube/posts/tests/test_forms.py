from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description'
        )
        cls.form_data = {
            'text': 'test-post',
            'group': cls.group.id,
        }

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=PostFormTests.form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.user.username}
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, 'test-post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostFormTests.group)

    def test_edit_post(self):
        post = Post.objects.create(
            author=PostFormTests.user,
            text='test-text',
            group=PostFormTests.group
        )
        new_post_text = 'new-text'
        new_group = Group.objects.create(
            title='new-test-group',
            slug='new-test-slug',
            description='new-test-description'
        )
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=PostFormTests.form_data,
            follow=True
        )
        response_new_group = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': new_post_text, 'group': new_group.id},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id}),
        )
        self.assertRedirects(
            response_new_group,
            reverse('posts:post_detail', kwargs={'post_id': post.id}),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, new_post_text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, new_group)
        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(PostFormTests.group.slug,))
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count,
            0
        )

    def test_unauth_user_cant_publish_post(self):
        response = self.guest.get(
            reverse('posts:post_create'),
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=/create/'
        )
