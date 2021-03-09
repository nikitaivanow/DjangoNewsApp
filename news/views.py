from django.shortcuts import render,get_object_or_404 , redirect
from django.views.generic import  ListView, DetailView, CreateView, TemplateView
from  django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from .models import News, Category
from .forms import NewsForm, UserRegisterForm, UserLoginForm, ContactForm
from .utils import MyMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from  django.contrib.auth import  login, logout
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.postgres.search import SearchVector



def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user =form.save()
			login(request, user)
			messages.success(request, 'Вы успешно зарегистрировались')
			return redirect('home')
		else:
			messages.error(request, 'Ошибка регистрации')
	else:
		form = UserRegisterForm()
	return render(request, 'news/register.html', {'form' : form})

def user_login(request):
	if request.method == 'POST':
		form = UserLoginForm(data = request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			return redirect('home')
	else:
		form = UserLoginForm()
	return render(request, 'news/login.html', {"form" : form})


def user_logout(request):
	logout(request)
	return redirect ('login')

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['content'],
			'ballffe@yandex.ru', ['nikitaivanov@mail.ee'], fail_silently = False )
			if mail:
				messages.success(request, 'Письмо отправленно')
				return redirect('contact')
			else:
				messages.error(request, 'Ошибка отправки')
		else:
			messages.error(request, 'Ошибка регистрации')
	else:
		form = ContactForm()
	return render(request, 'news/contact.html', {'form' : form})

class HomeNews(ListView) :
	model = News
	template_name = 'news/news_list.html'
	context_object_name = 'news'
	mixin_prop = 'helloworld'
	paginate_by = 4
	# extra_context = {'title' : 'Главная'}

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = 'Главная страница'
		return context

	def get_queryset(self):

		return News.objects.filter(is_published=True).select_related('category')


class NewsByCategory(ListView):
	model = News
	template_name = 'news/news_list.html'
	context_object_name = 'news'

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = 'Главная страница'
		return context

	def get_queryset(self):
		return News.objects.filter (category_id=self.kwargs['category_id'] ,is_published=True).select_related('category')





def index(request):
	news = News.objects.all()
	context = {
		'news': news,
		'title' : 'Список новостей'
	}
	return render(request, 'news/index.html', context)


# def get_category(request , category_id):
# 	news = News.objects.filter(category_id = category_id)
# 	category = Category.objects.get(pk=category_id)
# 	return render(request, 'news/category.html', {'news' : news,  'category' : category})


class ViewNews(DetailView):
	model = News
	# template_name = 'news/news_detail.html'
	# pk_url_kwarg = 'news_id'
	context_object_name = 'news_item'

# def view_news(request , news_id):
# 	# news_item = News.objects.get(pk=news_id)
# 	news_item = get_object_or_404(News,pk=news_id)
# 	return render(request, 'news/view_news.html', {'news_item' : news_item})


class CreateNews(LoginRequiredMixin, CreateView):
	form_class = NewsForm
	template_name = 'news/add_news.html'


# def add_news(request):
# 	if request.method == 'POST':
# 		form = NewsForm(request.POST)
# 		if form.is_valid():
# 			# print(form.cleaned_data)
# 			# news = News.objects.create(**form.cleaned_data)
# 			news = form.save()
# 			return redirect(news)
# 	else:
# 		form = NewsForm()
# 	return render(request, 'news/add_news.html', {'form' : form})

class Search(ListView):
	template_name = 'news/search.html'
	context_object_name = 'news'
	paginate_by = 4

	def get_queryset(self):
		return News.objects.filter(content__icontains = self.request.GET.get('q'))

	def get_context_data(self,*, object_list=None, **kwargs):
		conext = super().get_context_data(**kwargs)
		return conext