from django.urls import path
from .views import LoginView, LogoutView, PrivateUserList, PrivateUser, UserList, User, CurrentUser

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('private/users', PrivateUserList.as_view(), name='private_users'),
    path('private/users/<int:pk>', PrivateUser.as_view(), name='private_user'),
    path('users', UserList.as_view(), name='users'),
    path('current', CurrentUser.as_view(), name='current_user'),
    path('users/<int:pk>', User.as_view(), name='user'),
]
