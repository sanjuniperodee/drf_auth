import asyncio
import json
import threading
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
import jwt, datetime
from .models import Restaurant, Favorites, Certificate, Tag, RestaurantImage
from .serializers import (
    RestaurantSerializer,
    FavoritesSerializer,
    CertificateSerializer,
)
lock = threading.Lock()
condition = threading.Condition(lock)
@api_view(['GET'])
def get_restaurants(request):
    data = []
    tags = Tag.objects.all()
    all_tags = ['Все']
    for i in tags:
        all_tags.append(i.title)
    for i in Restaurant.objects.all():
        tags = [tag.title for tag in i.tags.all()]
        item = {
            'logo': i.logo.url,
            'id': i.pk,
            'title': i.title,
            'description': i.description,
            'tags': tags,
            'image': i.image.url,
            'slug': i.slug,
            'location': i.location,
            'kitchen': i.kitchen,
            'average': i.average,
            'phone': i.phone_number,
        }
        data.append(item)
    return Response({"restaurants": data, "tags": all_tags})

@api_view(['GET'])
def get_restaurant_by_slug(request, slug):
    try:
        item = Restaurant.objects.get(slug=slug)
        menus = [{"title": i.title, "image": i.image.url} for i in item.menu.all()]
        images = [image.images.url for image in RestaurantImage.objects.filter(post=item)]
        data = {
            'logo': item.logo.url,
            'id': item.pk,
            'title': item.title,
            'description': item.description,
            'tags': [tag.title for tag in item.tags.all()],
            'image': item.image.url,
            'prices': item.prices.split(','),
            'slug': item.slug,
            'location': item.location,
            'kitchen': item.kitchen,
            'average': item.average,
            'phone': item.phone_number,
            'menus': menus,
            'images': images,
            'insta': item.insta,
            'whatsapp': item.whatsapp
        }
        return Response({'data': data})
    except Restaurant.DoesNotExist:
        return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_new_restaurants(request):
    data = []
    for i in Restaurant.objects.all():
        tags = [tag.title for tag in i.tags.all()]
        item = {
            'logo': i.logo.url,
            'id': i.pk,
            'title': i.title,
            'description': i.description,
            'tags': tags,
            'image': i.image.url,
            'slug': i.slug,
            'location': i.location,
            'kitchen': i.kitchen,
            'average': i.average,
            'phone': i.phone_number,
        }
        data.append(item)
    return Response({"restaurants": data})

@api_view(['POST'])
def add_to_favorite(request, userId, restaurantId):
    try:
        user_fav, created = Favorites.objects.get_or_create(user=userId)
        restaurant = Restaurant.objects.get(pk=restaurantId)
        user_fav.restaurants.add(restaurant)
        user_fav.save()
        return Response({"status": "OK"})
    except Restaurant.DoesNotExist:
        return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_favourites(request, userId):
    try:
        user_fav = Favorites.objects.get(user=userId)
        data = []
        for restaurant in user_fav.restaurants.all():
            tags = [tag.title for tag in restaurant.tags.all()]
            item = {
                'logo': restaurant.logo.url,
                'id': restaurant.pk,
                'title': restaurant.title,
                'description': restaurant.description,
                'tags': tags,
                'image': restaurant.image.url,
                'slug': restaurant.slug,
                'location': restaurant.location,
                'kitchen': restaurant.kitchen,
                'average': restaurant.average,
                'phone': restaurant.phone_number,
            }
            data.append(item)
        return Response({"restaurants": data})
    except Favorites.DoesNotExist:
        return Response({'error': 'Favorites not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_certificate(request):
    try:
        raw_data = request.data
        certificate = Certificate(
            sum=raw_data.get('price'),
            user_id=raw_data.get('user_id'),
        )
        certificate.save()
        return Response({'data': "exit"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_certificates_by_id(request, id):
    data = []
    for certificate in Certificate.objects.filter(user_id=id):
        item = {
            'id': certificate.pk,
            'sum': certificate.sum,
            'user_id': certificate.user_id,
            'status': certificate.status,
            'encode': certificate.encode,
        }
        data.append(item)
    return Response({"certificates": data})


redirect_url = None
user_id = None


def set_redirect_url(url):
    global redirect_url
    with condition:
        redirect_url = url
        condition.notify_all()


async def wait_for_redirect_url():
    global redirect_url
    with condition:
        while not redirect_url:
            condition.wait()
        return redirect_url


@api_view(['POST'])
def handle(request):
    global user_id
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    if data.get('result') == 'REJECTED':
        raw_data = request.body
        json_string = raw_data.decode('utf-8')
        data = json.loads(json_string)
        set_redirect_url(data.get('alternative_reason'))
        print(data.get('alternative_reason'))
    else:
        try:
            print()
            raw_data = request.body
            json_string = raw_data.decode('utf-8')
            data = json.loads(json_string)
            print(data.get('approved_params').get('principal'))
            print(data.get('user_id'))
            certificate = Certificate(
                sum=data.get('approved_params').get('principal'),
                user_id=user_id
            )
            certificate.save()  # Use 'await' for asynchronous database operations
        except:
            print('error')
        set_redirect_url(data.get('redirect_url'))

    return Response({'message': 'OK'}, status=200)

@api_view(['GET'])
def redirect_user(request, userId):
    global user_id, redirect_url
    async def asyncfunc():
        await wait_for_redirect_url()

    asyncio.run(asyncfunc())
    url = redirect_url
    print("RETURNED ANSWER")
    set_redirect_url(None)
    user_id = userId
    return Response({'url': url})


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        phone_number = request.data['phone_number']
        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise AuthenticationFailed("user not found")
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'sercet', algorithm='HS256').encode('utf-8')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'token': token
        }
        return response


class UserView(APIView):
    def post(self, request):
        token = request.data.get('jwt')
        print(token)
        if not token:
            raise AuthenticationFailed("Failed to authorize")
        try:
            payload = jwt.decode(token, 'sercet', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Authorization is expired")
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)