import asyncio
import base64
import json
import threading
from datetime import datetime, timedelta
import requests
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, get_object_or_404, redirect

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime, timedelta
from django.utils import timezone
import jwt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Restaurant, Favorites, Certificate, Tag, RestaurantImage, Status
from .models import User
from .serializers import UserSerializer

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
            'id': i.pk
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
            'work_hours': item.work_hours.split(';'),
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
        user_fav, created = Favorites.objects.get_or_create(user=User.objects.get(pk=userId))
        restaurant = Restaurant.objects.get(pk=restaurantId)
        user_fav.restaurants.add(restaurant)
        user_fav.save()
        return Response({"status": "OK"})
    except Restaurant.DoesNotExist:
        return Response({'error': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_favourites(request, userId):
    try:
        user_fav = Favorites.objects.get(user=User.objects.get(pk=userId))
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
    for certificate in Certificate.objects.filter(user=User.objects.get(pk=id)):
        item = {
            'id': certificate.pk,
            'sum': certificate.sum,
            'user_id': certificate.user_id,
            'status': certificate.status,
        }
        if certificate.status:
            item = {
                'id': certificate.pk,
                'sum': certificate.sum,
                'user_id': certificate.user_id,
                'status': certificate.status,
                'encode': certificate.encode,
                'restaurant': certificate.restaurant.title,
                'end_date': certificate.end_date
            }

        data.append(item)
    return Response({"certificates": data})


redirect_url = {}
name = {}
surname = {}

@api_view(['POST'])
def handle(request):
    global redirect_url, name, surname
    data = json.loads(request.body)
    status = Status(title='Выдано', body=str(data))
    if data.get('result'):
        if data.get('result') == 'APPROVED':
            status.title = "Одобрено"
        else:
            status.title = "Отказано"
    status.save()
    message = MIMEMultipart()
    context = "Статус: " + status.title
    if data.get("first_name"):
        context += "\nНа имя: " + data.get('first_name') + " " + data.get('last_name')
    else:
        context += "\nНа имя : " + name[data.get('uuid')] + " " + surname[data.get('uuid')]
    if data.get('alternative_reason'):
        context += "\nПричина отказа: " + data.get('alternative_reason')
    context += "\nНаминал: " + str(data.get('approved_params').get('principal'))
    context += "\nСрок: " + str(data.get('approved_params').get('period'))

    message.attach(MIMEText(context))
    message["From"] = "support@reddel.kz"
    message["To"] = "admin@reddel.kz"
    message["Subject"] = "Новая заявка"

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "noreply.reddel@gmail.com"
    smtp_password = "hfft yumf trrp vczw"

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, "admin@reddel.kz", message.as_string())
    server.quit()
    print(data)
    if data.get('result') == 'REJECTED':
        raw_data = request.body
        json_string = raw_data.decode('utf-8')
        data = json.loads(json_string)
        redirect_url[data.get('uuid')] = data.get('alternative_reason')
        print(data.get('alternative_reason'))
    elif data.get('status') == 'ISSUED':
        raw_data = request.body
        json_string = raw_data.decode('utf-8')
        data = json.loads(json_string)
        user = User.objects.get(pk=data.get('reference_id'))
        certificate = Certificate(
            sum=data.get('approved_params').get('principal'),
            user=user
        )
        certificate.save()
        with open("auth//template.html", "r") as f:
            email_template = f.read()
        email_template = email_template.replace("Акжонов Досжан Дарахнович", user.first_name)
        email_template = email_template.replace("30000 ₸", str(certificate.sum))
        email_template = email_template.replace("408948", "Не активирован")
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = user.email
        message["Subject"] = "Поздравляем! У вас новый сертификат"
        message.attach(MIMEText(email_template, "html"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, user.email, message.as_string())
            server.sendmail(smtp_username, "admin@reddel.kz", message.as_string())
    else:
        redirect_url[data.get('uuid')] = data.get('redirect_url')

    return Response({'message': 'OK'}, status=200)

@api_view(['GET'])
def redirect_user(request, uuid):
    global redirect_url
    try:
        url = redirect_url[uuid]
        if(len(url) == 0):
            return Response(status=500)
        redirect_url[uuid] = ''
        print("RETURNED ANSWER")
        return Response({'url': url})
    except:
        return Response({},status=500)


@api_view(['POST'])
def set_name(request, uuid, first_name, last_name):
    global name, surname
    name[uuid] = first_name
    surname[uuid] = last_name
    return Response(status=200)


@api_view(['POST'])
def activate_certificate(request, certificate_id, restaurant_id):
    print(certificate_id)
    print(restaurant_id)
    # try:
    certificate = Certificate.objects.get(pk=certificate_id)
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    end_date = timezone.now() + timedelta(days=30 * 6)
    user = User.objects.get(pk=certificate.user.id)

    code = generate_certificate_code(restaurant.title, certificate_id, timezone.now(), user.first_name, user.last_name)
    certificate.encode = code
    certificate.status = True
    certificate.start_date = datetime.now()
    certificate.end_date = end_date
    certificate.restaurant = restaurant  # Set the restaurant
    certificate.save()
    text = "В вашем ресторане " + restaurant.title + " был активирован сертификат на сумму " + str(certificate.sum) + "\nКод активации сертификата: " + str(code)[:10] + "\nФИО: " + user.first_name + " " + user.last_name + \
           "\nНомер телефона: " + user.phone_number
    requests.get("https://api.mobizon.kz/service/message/sendsmsmessage?recipient=" + restaurant.phone_number.replace('(', '').replace(')', '').replace(' ', '').replace('_', '') + "&text=" + text + "&apiKey=kz0502f56621750a9ca3ac636e8301e235c2b647839531f2994222514c786fb6ff2178")
    recipient_email = user.email
    with open("auth//template.html", "r") as f:
        email_template = f.read()
    smtp_username = "noreply.reddel@gmail.com"
    smtp_password = "hfft yumf trrp vczw"
    email_template = email_template.replace("Акжонов Досжан Дарахнович" , user.first_name)
    email_template = email_template.replace("30000 ₸", str(certificate.sum))
    email_template = email_template.replace("408948", str(code)[:10])

    message = MIMEMultipart()
    message["From"] = smtp_username
    message["To"] = recipient_email
    message["Subject"] = "Поздравляем! Вы активировали сертификат"
    message.attach(MIMEText(email_template, "html"))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient_email, message.as_string())
        server.sendmail(smtp_username, "admin@reddel.kz", message.as_string())


    return Response({'message': 'Certificate activated successfully.'}, status=200)
    # except Certificate.DoesNotExist:
    #     return Response({'message': 'Certificate not found.'}, status=404)
    # except Restaurant.DoesNotExist:
    #     return Response({'message': 'Restaurant not found.'}, status=404)
    # except:


def generate_certificate_code(restaurant_id, certificate_id, current_datetime, first_name, last_name):
    data_to_encode = f'{certificate_id}-{restaurant_id}-{current_datetime}-{first_name}-{last_name}'

    encoded_bytes = data_to_encode.encode('utf-8')
    encoded_string = base64.b64encode(encoded_bytes).decode('utf-8')
    return encoded_string


class CheckUserView(APIView):

    def post(self, request):
        phone_number = request.data['phone_number']
        email = request.data['email']

        if len(User.objects.filter(phone_number=phone_number)) + len(User.objects.filter(email=email)) == 0:
            return Response({}, status=200)
        return Response({}, status=400)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            phone_number = request.data['phone_number']
            user = User.objects.filter(phone_number=phone_number).first()
            payload = {
                'id': user.id,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, 'sercet', algorithm='HS256').encode('utf-8')

            # Set the JWT token in the response
            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'token': token
            }
            return response
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        phone_number = request.data['phone_number']
        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise AuthenticationFailed("user not found")
        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
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


@api_view(['GET'])
def admin(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'admin.html')
    return redirect("login_admin")


@api_view(['GET', 'POST'])
def login_admin(request):
    print(request.user.is_superuser.__str__() + " " + request.user.username)
    if request.method == 'POST':
        print(request.POST['login'])
        print(request.POST['password'])
        try:
            user = authenticate(username=request.POST['login'], password=request.POST['password'])
            login(request, user)
            print("authorized")
            return redirect("admin1")
        except:
            print('error')
    return render(request, 'login.html')
