from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='leo')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test",
            description="Описание тестовой группы"
        )

        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group
            ).exists()
        )

    def test_edit_post(self):
        new_form_data = {
            'text': 'Новый текст поста',
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit', kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id
                }
            ),
            data=new_form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'post',
                kwargs={
                    'username': self.post.author.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст поста'
            ).exists()
        )
