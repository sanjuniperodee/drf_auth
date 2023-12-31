from django.urls import path
from .views import *

urlpatterns = [
    path('checkUser', CheckUserView.as_view()),
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('getAllRestaurants', get_restaurants, name='get_restaurants'),
    path('get_restaurant_by_slug/<slug>', get_restaurant_by_slug, name='get_restaurant_by_slug'),
    path('get_certificates_by_id/<id>', get_certificates_by_id, name='get_certificates_by_id'),
    path('add_to_favorite/<userId>/<restaurantId>', add_to_favorite, name='add_to_favorite'),
    path('get_favourites/<userId>', get_favourites, name='get_favourites'),
    path('handle', handle, name='handle'),
    path('get_portfolio_images/<id>', PortfolieImagesView.as_view(), name='get_portfolio_images'),
    path('redirect_user/<uuid>', redirect_user, name='redirect_user'),
    path('set_status_data', set_name, name='set_name'),
    path('activate_certificate/<certificate_id>/<restaurant_id>', activate_certificate, name='activate_certificate'),
    path('', MyLoginView.as_view(), name='login'),
    path('auth/logout/', MyLogoutView.as_view(), name='logout'),
    path('restaurant/create', RestaurantCreateView.as_view(), name='restaurant_create'),
    path('restaurant/all', RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurant/<int:pk>/delete', RestaurantDeleteView.as_view(), name='restaurant_delete'),
    path('restaurant/<int:pk>/edit', RestaurantEditView.as_view(), name='restaurant_edit'),
    path('order/<str:status>', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/delete', deleteOrder, name='order_delete'),
    path('delete_image/<int:image_id>', delete_image, name='delete_image'),
    path('upload-images/<int:id>', upload_images_view, name='upload_images'),
    path('upload-logo/<int:id>', upload_logo_view, name='upload_images'),

]
