from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, PostForm, CommentForm
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like
from django.http import JsonResponse
import json

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = False
            user.is_superuser = False
            user.save()
            return redirect('login')  # arahkan ke halaman login
    else:
        form = RegisterForm()
    return render(request, 'api/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'api/login.html', {'error': 'Invalid credentials'})
    return render(request, 'api/login.html')


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return redirect('login')  # redirect ke halaman login

     
@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'social/home.html', {'posts': posts, 'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.save()
    return redirect('home')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # unlike
    return redirect('home')

@login_required
def ajax_like_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        liked = Like.objects.filter(user=request.user, post=post).exists()

        if liked:
            Like.objects.filter(user=request.user, post=post).delete()
            action = 'unliked'
        else:
            Like.objects.create(user=request.user, post=post)
            action = 'liked'

        return JsonResponse({
            'action': action,
            'like_count': post.like_set.count(),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment_ajax(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        content = data.get('content')
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.create(user=request.user, post=post, content=content)
        return JsonResponse({
            'username': comment.user.username,
            'content': comment.content,
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def home(request):
    posts = Post.objects.all()

    for post in posts:
        post.liked_by_user = post.like_set.filter(user=request.user).exists()

    return render(request, 'social/home.html', {'posts': posts})