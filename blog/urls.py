from django.urls import path
from django.conf.urls import url
from . import views
from . import models
from django.views.generic import ListView

urlpatterns = [
    path('', views.IndexView.as_view(),
         name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit', views.post_edit, name='post_edit'),
    url(r'^publishers/$', views.PublisherList.as_view()),
    url(r'^books/([\w-]+)/$', views.PublisherBookList.as_view()),
    url(r'^authors/(?P<pk>[0-9]+)/$', views.AuthorDetailView.as_view(),
        name='author-detail'),

]
