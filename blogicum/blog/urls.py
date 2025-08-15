from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    #
    # Профили
    #
    path('profile/', views.ProfilePage.as_view(), name='my_profile'),
    path('profile/<username>/', views.ProfilePage.as_view(), name='profile'),
    path('profile_edit/', views.UpdateProfile.as_view(), name='edit_profile'),
    #
    # Посты
    #
    path('', views.BlogIndexPage.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:pk>/edit/', views.UpdatePostView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/', views.DeletePostView.as_view(),
         name='delete_post'),
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),
    #
    # Комментарии
    #
    path('posts/<int:pk>/comment/', views.CreateCommentView.as_view(),
         name='add_comment'),
    path('posts/<int:post_pk>/edit_comment/<int:pk>',
         views.UpdateCommentView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_pk>/delete_comment/<int:pk>',
         views.DeleteCommentView.as_view(),
         name='delete_comment'),
    #
    # Категории
    #
    path('category/<slug:category_slug>/', views.CategoryListView.as_view(),
         name='category_posts'),
]
