from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.CharField(max_length=255, unique=True, verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=255, unique=True, verbose_name='Номер телефона')
    username = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255, null=True, verbose_name='Пароль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    # USERNAME_FIELD = phone_number

    def __str__(self):
        return self.first_name + " " + self.last_name + " : " + str(self.pk)



class Tag(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    def __str__(self):
        return self.title


class ImageModel(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField(verbose_name='Картинка')
    def __str__(self):
        return self.title


class Restaurant(models.Model):
    logo = models.ImageField(null=True, verbose_name='Логотип')
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(null=True, verbose_name='Описание')
    image = models.ImageField(null=True, verbose_name='Главная фотография')
    tags = models.ManyToManyField(Tag, default=None, verbose_name='Категории')
    average = models.CharField(max_length=255, null=True, verbose_name='Средний чек')
    food_type = models.CharField(max_length=255, verbose_name='Тип еды')
    phone_number = models.CharField(max_length=255, verbose_name='Номер телефона')
    menu = models.ManyToManyField(ImageModel, default=None, null=True, verbose_name='Меню')
    sales = models.ImageField(null=True, default=None, verbose_name='Акции')
    prices = models.CharField(null=True, max_length=255, verbose_name='Цены для сертификата')
    slug = models.SlugField(null=True, verbose_name='ссылка')
    location = models.CharField(max_length=255, null=True, verbose_name='Адресс')
    kitchen = models.CharField(max_length=255, null=True, verbose_name='Кухня')
    novy = models.BooleanField(default=False, verbose_name='Скрыть')
    insta = models.CharField(max_length=255, null=True, verbose_name='Instagram')
    whatsapp = models.CharField(max_length=255, null=True, verbose_name='Whatsapp')
    work_hours = models.CharField(max_length=255, null=True, verbose_name='Часы работы')

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'
    def __str__(self):
        return self.title + ": " + str(self.pk)


class RestaurantImage(models.Model):
    post = models.ForeignKey(Restaurant, default=None, on_delete=models.CASCADE)
    images = models.ImageField()
    def __str__(self):
        return self.post.title


class Favorites(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    restaurants = models.ManyToManyField(Restaurant, default=None, null=True)


class Certificate(models.Model):
    sum = models.FloatField(verbose_name='Сумма')
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE, verbose_name='Пользователь')
    encode = models.CharField(max_length=255, null=True, blank=True, verbose_name='Код сертификата')
    status = models.BooleanField(default=False, blank=True, verbose_name='Акитивирован')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Начало активации')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Срок')
    restaurant = models.ForeignKey(Restaurant, default=None, on_delete=models.CASCADE, null=True, verbose_name='Ресторан')

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'


class Status(models.Model):
    title = models.CharField(max_length=255, verbose_name='Статус')
    body = models.TextField(verbose_name='Тело запроса')

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
    def __str__(self):
        return self.title