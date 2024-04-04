import asyncio
import base64
import json
import threading
from datetime import datetime, timedelta
import requests
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import JsonResponse
from rest_framework import permissions

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

from .models import *
from .serializers import UserSerializer, PortfolieImagesSerializer
from .forms import *
from django.db.models import Count, Sum, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.views import LoginView, LogoutView
from .forms import MyAuthenticationForm, RestaurantForm, RestaurantImageForm

lock = threading.Lock()
condition = threading.Condition(lock)

class HandleLeadRequest(APIView):
    def post(self, request):
        data = json.loads(request.body)
        context = "Новая заявка на звонок"

        context += "\nИмя: " + str(data.get('name'))
        context += "\nНомер телефона: " + str(data.get('phone_number'))
        context += "\nМероприятие: " + str(data.get('party'))
        message = MIMEMultipart()

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
        return Response(status=status.HTTP_200_OK)
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


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
        images = [image.images.url for image in RestaurantImage.objects.filter(post=item)]
        data = {
            'logo': item.logo.url,
            'id': item.pk,
            'title': item.title,
            'description': item.description,
            'tags': [tag.title for tag in item.tags.all()],
            'work_days_1': item.work_days_1,
            'work_days_2': item.work_days_2,
            'work_hours_1': item.work_hours_1,
            'work_hours_2': item.work_hours_2,
            'image': item.image.url,
            'prices': [price.sum for price in item.sum_of_credit.all()],
            'period': [period.months for period in item.period_of_credit.all()],
            'slug': item.slug,
            'location': item.location,
            'kitchen': item.kitchen,
            'average': item.average,
            'phone': item.phone_number,
            # 'menus': item.menu,
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

@api_view(['GET'])
def get_certificates_by_id(request, id):
    data = []
    for certificate in Certificate.objects.filter(user__pk=id):
        item = {
            'id': certificate.pk,
            'sum': certificate.sum.sum,
            'user_id': certificate.user_id,
            'status': certificate.status,
        }
        if certificate.status:
            item = {
                'id': certificate.pk,
                'sum': certificate.sum.sum,
                'user_id': certificate.user.pk,
                'status': certificate.status,
                'encode': certificate.encode,
                'restaurant': certificate.restaurant.title,
                'end_date': certificate.end_date
            }

        data.append(item)
    return Response({"certificates": data})


@api_view(['POST'])
def handle(request):
    data = json.loads(request.body)
    print(data.get('uuid'))
    print(data)
    status = Status(
        status=data
    )
    status.save()
    status = Status.objects.get(uuid=data.get('uuid'))
    status.stats = 'Выдано'
    if data.get('result'):
        if data.get('result') == 'APPROVED':
            status.status = "Одобрено"
        else:
            status.status = "Отказано"
    message = MIMEMultipart()
    context = "Статус: " + status.status
    if data.get("first_name"):
        context += "\nНа имя: " + data.get('first_name') + " " + data.get('last_name')
    else:
        context += "\nНа имя : " + status.user.first_name + " " + status.user.last_name
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
        status.redirect_url = data.get('alternative_reason')
        status.reject_reason = data.get('alternative_reason')
        print(data.get('alternative_reason'))
    elif data.get('status') == 'ISSUED':
        raw_data = request.body
        json_string = raw_data.decode('utf-8')
        data = json.loads(json_string)
        certificate = Certificate(
            sum=SumOfCredit.objects.get(sum=int(data.get('approved_params').get('principal'))),
            period=PeriodOfCredit.objects.get(months=int(data.get('approved_params').get('period'))),
            user=status.user,
            restaurant=status.restaurant
        )
        certificate.save()
        with open("auth//template.html", "r") as f:
            email_template = f.read()
        email_template = email_template.replace("Акжонов Досжан Дарахнович", status.user.first_name)
        email_template = email_template.replace("30000 ₸", str(certificate.sum))
        email_template = email_template.replace("408948", "Не активирован")
        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = status.user.email
        message["Subject"] = "Поздравляем! У вас новый сертификат"
        message.attach(MIMEText(email_template, "html"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, status.user.email, message.as_string())
            server.sendmail(smtp_username, "admin@reddel.kz", message.as_string())
    else:
        status.redirect_url = data.get('redirect_url')
    status.save()
    return Response({'message': 'OK'}, status=200)

@api_view(['GET'])
def redirect_user(request, uuid):
    global redirect_url
    try:
        status = Status.objects.get(uuid=uuid)
        if status.redirect_url is None:
            return Response(status=500)
        print("RETURNED ANSWER")
        return Response({'url': status.redirect_url})
    except:
        return Response({},status=500)


@api_view(['POST'])
def set_name(request):
    data = json.loads(request.body)
    print(data)
    status = Status(
        user = User.objects.get(pk=data.get('user_id')),
        restaurant = Restaurant.objects.get(pk=data.get('restaurant_id')),
        period_of_credit = PeriodOfCredit.objects.get(months=int(data.get('period'))),
        sum_of_credit = SumOfCredit.objects.get(sum=int(data.get('sum'))),
        uuid=data.get('uuid')
    )
    status.save()
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


# @api_view(['GET'])
# def admin(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         return render(request, 'admin.html')
#     return redirect("login_admin")
#
#
# @api_view(['GET'])
# def partners(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         return render(request, 'partners.html', {"restaurants": Restaurant.objects.all()})
#     return redirect("login_admin")
#
#
# @api_view(['GET', 'POST'])
# def login_admin(request):
#     if request.user.is_authenticated and request.user.is_superuser :
#         return redirect("admin1")
#
#     if request.method == 'POST':
#         print(request.POST['login'])
#         print(request.POST['password'])
#         try:
#             user = authenticate(username=request.POST['login'], password=request.POST['password'])
#             login(request, user)
#             print("authorized")
#             return redirect("admin1")
#         except:
#             print('error')
#     return render(request, 'login.html')


class PortfolieImagesView(APIView):
    def get(self, request, id):
        try:
            portfolio_images = PortfolieImages.objects.get(id=id)
            serializer = PortfolieImagesSerializer(portfolio_images)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, id):
        if len(PortfolieImages.objects.filter(id=id)) > 0:
            image = PortfolieImages.objects.get(id=id)
            image.image = request.data['image']
            image.save()
            return Response({}, status=status.HTTP_202_ACCEPTED)
        serializer = PortfolieImagesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            image = PortfolieImages.objects.get(id=id)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)



class MyLoginView(LoginView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    permission_classes = (permissions.AllowAny,)
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('restaurant_list')
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=self.request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('restaurant_list')
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'}, status=404)


class MyLogoutView(LogoutView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('login')

class RestaurantCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_partner.html'
    permission_classes = [IsAdminUser]

    def get(self, request):
        form = RestaurantForm()
        images = RestaurantImage.objects.filter(post__isnull=True)
        return Response({'form': form, 'image_form': RestaurantImageForm(), 'images': images})

    def post(self, request):
        print(2131231)
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save()
            return Response({'success': True, 'restaurant_id': restaurant.id})
        print(form.errors)
        return Response({'success': False})


def delete_image(request, image_id):
    image = RestaurantImage.objects.get(id=image_id)
    image.delete()
    return Response({'success': True})


def upload_images_view(request, id):
    if request.method == 'POST' and request.FILES.getlist('images'):
        uploaded_images = request.FILES.getlist('images')

        # try:
        for image in uploaded_images:
            RestaurantImage.objects.create(images=image, post=Restaurant.objects.get(pk=id))  # Assuming your Image model has an 'image_file' field
        return JsonResponse({'message': 'Images uploaded successfully'}, status=201)
        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'No images received'}, status=400)
def upload_logo_view(request, id):
    if request.method == 'POST' and request.FILES.getlist('images'):
        uploaded_images = request.FILES.getlist('images')

        # try:
        for image in uploaded_images:
            restauran = Restaurant.objects.get(pk=id)
            restauran.logo = image
            restauran.save()
        return JsonResponse({'message': 'Images uploaded successfully'}, status=201)
        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'No images received'}, status=400)

class RestaurantListView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'all_partners.html'

    def get(self, request):
        queryset = Restaurant.objects.all()
        total_restaurants = queryset.count()
        # Обработка поиска
        search_query = request.GET.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(food_type__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        # Обработка сортировки
        sort_by_orders = request.GET.get('sort_orders')
        sort_by_amount = request.GET.get('sort_amount')

        if sort_by_orders:
            queryset = queryset.annotate(num_orders=Count('orders')).order_by(
                'num_orders' if sort_by_orders == 'asc' else '-num_orders')
        elif sort_by_amount:
            queryset = queryset.annotate(total_amount=Sum('orders__sum_of_credit__sum')).order_by(
                'total_amount' if sort_by_amount == 'asc' else '-total_amount')

        return Response({'restaurants': queryset, 'total_restaurants': total_restaurants})


class UserListView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'all_users.html'

    def get(self, request):
        queryset = User.objects.all()
        total_users = queryset.count()
        # Обработка поиска
        search_query = request.GET.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )

        return Response({'users': queryset, 'total_restaurants': total_users})


class CertificateListView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'all_certificates.html'

    def get(self, request):
        queryset = Certificate.objects.all()
        total_users = queryset.count()
        # Обработка поиска
        search_query = request.GET.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(sum__sum__icontains=search_query) |
                Q(restaurant__title__icontains=search_query)
            )

        return Response({'certificates': queryset, 'total_restaurants': total_users})

class EditBanner(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'EditBanner.html'

    def get(self, request):
        return Response({'banner': Banner.objects.first()})

    def post(self, request):
        image_file = request.FILES.get('image')

        if image_file:
            # Create or update your Banner model instance
            banner_instance = Banner.objects.first()  # Adjust this to fetch the banner you want to update/create
            banner_instance.image = image_file
            banner_instance.save()
            return Response({'banner': Banner.objects.first()})
        return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)


class RestaurantEditView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'edit_partner.html'

    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        images = RestaurantImage.objects.filter(post=restaurant)
        form = RestaurantForm(instance=restaurant)
        tags = Tag.objects.all()
        return Response({'restaurant': restaurant, 'images': images, 'form': form, 'tags': tags})

    def post(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        images = RestaurantImage.objects.filter(post=restaurant)
        print('1')

        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            restaurant = form.save()
        return redirect('restaurant_edit', pk=restaurant.pk)



class RestaurantDeleteView(DeleteView):
    permission_classes = [IsAdminUser]
    model = Restaurant
    success_url = reverse_lazy('restaurant_list')  # Укажите ваш путь, куда перенаправлять после удаления
    template_name = 'all_partners.html'  # Создайте этот шаблон в соответствии с вашими нуждами

    def delete(self, request, *args, **kwargs):
        # Ваш код обработки удаления
        return super().delete(request, *args, **kwargs)


class OrderListView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'all_orders.html'

    def get(self, request, status):
        queryset = Status.objects.filter(status=status)
        total_orders = queryset.count()
        average = 0
        if total_orders > 0:
            # найти средний чек всех ордеров
            for i in queryset:
                average+=i.sum_of_credit.sum
            average /= total_orders
        search_query = request.GET.get('search_query')
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(restaurant__title__icontains=search_query) |
                Q(sum_of_credit__sum__icontains=search_query) |
                Q(period_of_credit__months__icontains=search_query) |
                Q(status__icontains=search_query)
            )

        # Обработка сортировки
        sort_by_orders = request.GET.get('sort_sum')

        if sort_by_orders:
            queryset = queryset.annotate(total_amount=Sum('sum_of_credit__sum')).order_by(
                'total_amount' if sort_by_orders == 'asc' else '-total_amount')


        return Response({'orders': queryset, 'total_orders': total_orders, 'average': average, 'status': status})


def deleteOrder(request, pk):
    order = Status.objects.get(pk=pk)
    order.delete()
    return JsonResponse({'message': 'ok'})