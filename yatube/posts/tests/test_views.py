from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms


from ..models import Post, Group


User = get_user_model()


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Name')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для тестов',
            group=cls.group
        )
        posts = []
        for i in range(1, 11):
            post = Post(
                author=cls.user,
                text='Тестовая запись',
            )
            posts.append(post)
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

    def test_pages_uses_correct_template(self):
        """URL-адреса используют соответствующий шаблон"""
        self.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={'slug': 'Slug'})):
                'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': 'Name'})):
                'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': 1})):
                'posts/post_detail.html',
            (reverse('posts:post_edit', kwargs={'post_id': 1})):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_list = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), post_list)

    def test_group_post_correct_contex(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        post_group_list = list(Post.objects.filter(
            group_id=self.group.id
        )[:10])
        self.assertEqual(list(response.context['page_obj']), post_group_list)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Name'})
        )
        post_profile = list(Post.objects.filter(author_id=self.user.id)[:10])
        self.assertEqual(list(response.context['page_obj']), post_profile)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_old_create_post_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_create_post_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_show_group_correct(self):
        """Группа правильно отображается на страницах."""
        form_fields = {
            reverse('posts:index'): Post.objects.filter(
                group=self.post.group
            )[0],
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                Post.objects.filter(group=self.post.group)[0],
            reverse('posts:profile', kwargs={'username': self.post.author}):
                Post.objects.filter(group=self.post.group)[0],
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    def test_group_not_in_mistake_group(self):
        """Пост не попал в другую группу."""
        form_fields = {
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                Post.objects.exclude(group=self.post.group)
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_paginator_correct(self):
        """Пагинатор правильно отображает страницы."""
        paginator_reverse = {
            'index': reverse('posts:index'),
            'profile': reverse('posts:profile',
                               kwargs={'username': self.post.author})
        }
        for place, page in paginator_reverse.items():
            with self.subTest(place=place):
                response_page_1 = self.authorized_client.get(page)
                response_page_2 = self.authorized_client.get(page + '?page=2')
                self.assertEqual(len(response_page_1.context['page_obj']), 10)
                self.assertEqual(len(response_page_2.context['page_obj']), 1)
