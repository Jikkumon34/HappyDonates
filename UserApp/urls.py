from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.register_user, name='register_user'),
    path('api/create_post', views.saveOrUpdate_user_post, name='create_post'),
    path('api/create_post/<int:post_id>', views.saveOrUpdate_user_post, name='update_delete_post'),
    path('api/post/', views.fetch_post, name='post'),
    path('api/post/<int:post_id>/', views.fetch_post, name='post_detail'),
    path('api/create_donation', views.saveOrUpdate_user_donation, name='create_donation'),
    path('api/create_donation/<int:donation_id>', views.saveOrUpdate_user_donation, name='update_delete_donation'),
    path('api/donation/', views.fetch_donation, name='donation'),
    path('api/donation/<int:donation_id>/', views.fetch_donation, name='donation_detail'),
    path('api/profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('api/districts/', views.all_districts, name='all-districts'),
    path('api/posters/', views.all_posters, name='all-posters'),
    path('api/subcategories/<int:main_category_id>/', views.subcategories_by_main_category,
         name='subcategories-by-main-category'),
    path('api/user/info/', views.get_user_info, name='get_user_info'),
    path('api/user/posts-donations/', views.user_posts_and_donations, name='user-posts-donations'),
    path('api/donation-categories/', views.donation_category_list, name='donation-category-list'),


]
