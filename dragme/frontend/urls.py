"""savannah URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

import frontend.views as views

urlpatterns = [
    path('', views.home, name='index'),
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),

    path('login/', views.login, name='login'),
    path('manage/', views.manage_shows, name='manage_shows'),
    path('manage/<int:show_id>/', views.manage_show, name='manage_show'),
    path('manage/<int:show_id>/edit', views.edit_show, name='edit_show'),
    path('manage/<int:show_id>/add', views.add_event, name='add_event'),
    path('manage/<int:show_id>/event/<int:event_id>/', views.manage_event, name='manage_event'),
    path('manage/<int:show_id>/event/<int:event_id>/edit', views.edit_event, name='edit_event'),
    path('manage/<int:show_id>/event/<int:event_id>/add', views.add_talent, name='add_talent'),
    path('manage/<int:show_id>/event/<int:event_id>/delete', views.delete_event, name='delete_event'),
    path('manage/<int:show_id>/event/<int:event_id>/talent/<int:talent_id>/', views.edit_talent, name='edit_talent'),
    path('manage/<int:show_id>/event/<int:event_id>/remove/<int:talent_id>/', views.delete_talent, name='delete_talent'),

    path('shows/', views.shows, name='shows'),
    path('performers/', views.performers, name='performers'),
    path('performers/<int:profile_id>/', views.profile, name='profile'),
    path('store/', views.store, name='store'),

    path('event/<int:event_id>/', views.event, name='show_event'),
]
