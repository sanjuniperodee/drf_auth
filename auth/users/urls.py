from django.urls import path
from .views import *

urlpatterns = [
    path('checkUser', CheckUserView.as_view()),
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('getAllRestaurants', get_restaurants, name='get_restaurants'),
    path('get_restaurant_by_slug/<slug>', get_restaurant_by_slug, name='get_restaurant_by_slug'),
    path('create_certificate', create_certificate, name='create_certificate'),
    path('get_certificates_by_id/<id>', get_certificates_by_id, name='get_certificates_by_id'),
    path('add_to_favorite/<userId>/<restaurantId>', add_to_favorite, name='add_to_favorite'),
    path('get_favourites/<userId>', get_favourites, name='get_favourites'),
    path('handle', handle, name='handle'),
    path('redirect_user/<uuid>', redirect_user, name='redirect_user'),
    path('set_name/<uuid>/<first_name>/<last_name>', set_name, name='set_name'),
    path('activate_certificate/<certificate_id>/<restaurant_id>', activate_certificate, name='activate_certificate'),
    path('admin1', admin, name='admin1'),
    path('login_admin', login_admin, name='login_admin'),
    path('get_portfolio_images/<id>', PortfolieImagesView.as_view()),
    path('partners', partners, name='partners')

]
