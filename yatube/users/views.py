from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm
from django.views.generic.base import TemplateView


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class JustStaticPage(TemplateView):
    template_name = 'app_name/just_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = 'Очень простая страница'
        context['just_text'] = ('На создание этой страницы '
                                'у меня ушло пять минут! Ай да я.')
        return context
