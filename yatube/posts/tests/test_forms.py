from ..forms import PostForm
from ..models import Post, Group
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class PostFormCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        post_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.order_by('-pk')[0].text,
                        form_data['text'])

    def test_post_edit_correct(self):
        edit_post = Post.objects.create(
            author=self.user,
            text='Текст новый 2'
        )
        form_data = {
            'text': 'Тестовая запись с правками'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': edit_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': edit_post.pk}))
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            id=edit_post.pk,
        ).exists())
