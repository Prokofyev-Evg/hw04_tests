from posts.models import Post
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {
            'text': _('Текст'),
            'group': _('Группа'),
        }
