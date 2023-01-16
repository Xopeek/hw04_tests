from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Name2')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тестовая запись для тестов',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names_all_user = [
            '/',
            '/group/Slug/',
            '/profile/Name2/',
            '/posts/1/',
        ]
        self.url_names_only_authorized = [
            '/posts/1/edit/',
            '/create/'
        ]

    def test_urls_anonymous(self):
        for address in self.url_names_all_user:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_redirect_anonymous(self):
        for address in self.url_names_only_authorized:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_create_post_author_and_create_post(self):
        for address in self.url_names_only_authorized:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_not_found_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/Slug/': 'posts/group_list.html',
            '/profile/Name2/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
