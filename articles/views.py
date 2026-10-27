from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from .models import Article

User = get_user_model()

def archive(request):

    posts = Article.objects.all()
    context = {
        'posts': posts
    }
    return render(
        request,
        'archive.html',
        context
    )

def get_article(request, article_id):

    try:
        post = Article.objects.get(id=article_id)
        context = {
            'post': post
        }
        return render(
            request,
            'article.html',
            context
        )
    except Article.DoesNotExist:
        raise Http404("Статья не найдена")

def create_post(request):

    if not request.user.is_authenticated:
        raise Http404(
            "Для создания статьи требуется авторизация"
        )

    form = {
        'title': '',
        'text': '',
        'errors': ''
    }

    if request.method == "POST":
        form['title'] = request.POST.get(
            'title', ''
        ).strip()
        form['text'] = request.POST.get(
            'text', ''
        ).strip()
        title = form['title']
        text = form['text']

        if not title or not text:
            form['errors'] = "Не все поля заполнены"

        elif len(title) > 200:
            form['errors'] = (
                "Название статьи не должно "
                "превышать 200 символов"
            )

        elif Article.objects.filter(
            title__iexact=title
        ).exists():
            form['errors'] = (
                "Статья с таким названием уже существует"
            )

        else:
            article = Article.objects.create(
                title=title,
                text=text,
                author=request.user
            )
            return redirect(
                'get_article',
                article_id=article.id
            )

    return render(
        request,
        'create_post.html',
        {'form': form}
    )

def register(request):

    if request.user.is_authenticated:
        return redirect('archive')
    form = {
        'username': '',
        'email': '',
        'errors': ''
    }

    if request.method == "POST":

        username = request.POST.get(
            'username', ''
        ).strip()

        email = request.POST.get(
            'email', ''
        ).strip()

        password = request.POST.get(
            'password', ''
        )

        form['username'] = username
        form['email'] = email

        if not username or not email or not password:

            form['errors'] = "Не все поля заполнены"

        elif len(username) > 150:

            form['errors'] = (
                "Логин не должен превышать 150 символов"
            )

        elif User.objects.filter(
            username__iexact=username
        ).exists():

            form['errors'] = (
                "Пользователь с таким логином уже существует"
            )

        else:
            try:
                username_validator = UnicodeUsernameValidator()
                username_validator(username)

                validate_email(email)

                new_user = User(
                    username=username,
                    email=email
                )

                validate_password(
                    password,
                    user=new_user
                )

            except ValidationError as error:
                form['errors'] = " ".join(error.messages)

            else:
                try:
                    User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )

                except IntegrityError:
                    form['errors'] = (
                        "Не удалось создать пользователя. "
                        "Возможно, логин уже занят."
                    )

                else:
                    return redirect('user_login')

    return render(
        request,
        'register.html',
        {'form': form}
    )

def user_login(request):

    if request.user.is_authenticated:
        return redirect('archive')
    form = {
        'username': '',
        'errors': ''
    }

    if request.method == "POST":
        username = request.POST.get(
            'username', ''
        ).strip()
        password = request.POST.get(
            'password', ''
        )
        form['username'] = username

        if not username or not password:
            form['errors'] = "Не все поля заполнены"

        else:

            # Проверяем логин и пароль
            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect('archive')

            else:
                form['errors'] = (
                    "Неверный логин или пароль"
                )

    return render(
        request,
        'login.html',
        {'form': form}
    )


@require_POST
def user_logout(request):

    logout(request)

    return redirect('archive')
