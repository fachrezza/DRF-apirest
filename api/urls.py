
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('auth/', obtain_auth_token),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    
    # Tempatkan ini sebelum router
    path('', views.home, name='home'),

    # Router API harus di bawah
    path('', include(router.urls)),

    path('add_comment_ajax/<int:post_id>/', views.add_comment_ajax, name='add_comment_ajax'),
    # path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('like-post/<int:post_id>/', views.ajax_like_post, name='ajax_like_post'),
]
