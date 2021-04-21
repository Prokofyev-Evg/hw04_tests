# posts/tests/tests_url.py
from django.test import TestCase, Client
from posts.models import Post, Group, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest = User.objects.create_user(username='guest')
        cls.user = User.objects.create_user(username='user')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test",
            description="Описание тестовой группы"
        )
        cls.userpost = Post.objects.create(
            text='Заголовок тестового поста авторизованного пользователя',
            group=cls.group,
            author=cls.user
        )
        cls.guestpost = Post.objects.create(
            text='Заголовок тестового поста неавторизованного пользователя',
            group=cls.group,
            author=cls.guest
        )

    def test_pages_access_all_users(self):
        urls_list = [
            '/',
            '/group/test/',
            '/about/author/',
            '/about/tech/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.userpost.id}/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_pages_access_authorized_users(self):
        urls_list = [
            '/new/',
            f'/{self.user.username}/{self.userpost.id}/edit/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_pages_access_non_authorized_users(self):
        urls_list = [
            '/new/',
            f'/{self.user.username}/{self.userpost.id}/edit/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_edit_post_access_anonymous_users(self):
        response = self.guest_client.get(
            f'/{self.guest.username}/{self.userpost.id}/edit/'
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_post_access_authorized_author(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.userpost.id}/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post_access_authorized_non_author(self):
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.guestpost.id}/edit/'
        )
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            ('index.html', '/'),
            ('about/author.html', '/about/author/'),
            ('about/tech.html', '/about/tech/'),
            ('group.html', '/group/test/'),
            ('newpost.html', '/new/'),
            ('newpost.html', f'/{self.user.username}/{self.userpost.id}/edit/')
        ]
        for template, reverse_name in templates_url_names:
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
