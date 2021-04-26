from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.conf import settings

from posts.models import Post, Group, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='UserName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group",
            description="Описание тестовой группы"
        )
        cls.post = Post.objects.create(
            text='Заголовок тестовой задачи',
            group=cls.group,
            author=cls.user
        )

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'newpost.html': reverse('new_post'),
            'group.html': (
                reverse('show_group_post', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        self.check_post_context_on_page(response.context['page'][0])

    def test_index_paginator(self):
        batch_size = settings.PAGINATOR_PER_PAGE_VAL * 2
        objs = (Post(
            text='Test %s' % i,
            group=self.group,
            author=self.user
        ) for i in range(batch_size))
        Post.objects.bulk_create(objs, batch_size)
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            len(response.context['page']),
            settings.PAGINATOR_PER_PAGE_VAL
        )

    def test_group_correct_context(self):
        response = self.authorized_client.get((
            reverse('show_group_post', kwargs={'slug': self.group.slug})
        ))
        self.check_post_context_on_page(response.context['page'][0])

    def test_new_post_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_group_has_not_post(self):
        new_group = Group.objects.create(
            title="Новая тестовая группа",
            slug="new_group",
            description="Описание новой тестовой группы"
        )
        response = self.authorized_client.get(
            reverse('show_group_post', kwargs={'slug': new_group.slug})
        )
        self.assertEqual(response.context['page'].paginator.count, 0)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.check_post_context_on_page(response.context['post'])

    def test_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.check_post_context_on_page(response.context['page'][0])

    def test_post_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.check_post_context_on_page(response.context['post'])
        self.assertEqual(response.context['user'], self.user)

    def check_post_context_on_page(self, post_object):
        self.assertEqual(post_object.author, self.user)
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.group, self.post.group)
