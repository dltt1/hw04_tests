import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description'
        )
        cls.form_data = {
            'text': 'test-post',
            'group': cls.group.id,
            'image': cls.uploaded
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, 'test-post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, PostFormTests.group)

    def test_edit_post(self):
        post = Post.objects.create(
            author=PostFormTests.user,
            text='test-post',
            group=PostFormTests.group
        )
        new_uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )
        PostFormTests.form_data['image'] = new_uploaded
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
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': new_post_text, 'group': new_group.id},
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, new_post_text)
        self.assertEqual(post.author, PostFormTests.user)
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
