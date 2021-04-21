from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='UserName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group_a = Group.objects.create(
            title="Тестовая группа A",
            slug="test_a",
            description="Описание тестовой группы A"
        )
        cls.group_b = Group.objects.create(
            title="Тестовая группа B",
            slug="test_b",
            description="Описание тестовой группы B"
        )
        # cls.post = Post.objects.create(
        #     text='Заголовок тестовой задачи',
        #     group=cls.group_a,
        #     author=cls.user
        # )
        cls.post = []
        for i in range(20):
            cls.post.append(Post.objects.create(
                text=f'Заголовок тестовой задачи {i}',
                group=cls.group_a,
                author=cls.user
            ))

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'newpost.html': reverse('new_post'),
            'group.html': (
                reverse('show_group_post', kwargs={'slug': 'test_a'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        post_object = response.context['page'][0]
        self.assertEqual(post_object.author, self.user)
        self.assertEqual(post_object.pub_date, self.post[-1].pub_date)
        self.assertEqual(post_object.text, self.post[-1].text)
        self.assertEqual(post_object.group, self.post[-1].group)
        self.assertEqual(len(response.context['page']), 10)

    def test_group_correct_context(self):
        response = self.authorized_client.get((
            reverse('show_group_post', kwargs={'slug': 'test_a'})
        ))
        post_object = response.context['page'][0]
        self.assertEqual(post_object.author, self.user)
        self.assertEqual(post_object.pub_date, self.post[-1].pub_date)
        self.assertEqual(post_object.text, self.post[-1].text)
        self.assertEqual(post_object.group, self.post[-1].group)

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

    def test_index_has_post(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertIn(self.post[-1], response.context['page'])

    def test_group_a_has_post(self):
        response = self.authorized_client.get(
            reverse('show_group_post', kwargs={'slug': 'test_a'})
        )
        self.assertIn(self.post[-1], response.context['page'])

    def test_group_b_has_not_post(self):
        response = self.authorized_client.get(
            reverse('show_group_post', kwargs={'slug': 'test_b'})
        )
        self.assertNotIn(self.post[-1], response.context['page'])

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post[0].id
                }
            )
        )
        self.assertEqual(response.context['post'], self.post[0])

    def test_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(response.context['page'][0], self.post[-1])
        self.assertEqual(response.context['author'], self.user)

    def test_post_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post[0].id
            })
        )
        post_context = {
            'post': self.post[0],
            'user': self.user
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                context = response.context[key]
                self.assertEqual(context, value)
