from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255, null=True)
    REQUIRED_FIELDS = []



class Tag(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ImageModel(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField()
    def __str__(self):
        return self.title


class Restaurant(models.Model):
    logo = models.ImageField(null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    image = models.ImageField(null=True)
    tags = models.ManyToManyField(Tag, default=None)
    average = models.CharField(max_length=255, null=True)
    food_type = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    menu = models.ManyToManyField(ImageModel, default=None, null=True)
    sales = models.ImageField(null=True, default=None)
    prices = models.CharField(null=True, max_length=255)
    slug = models.SlugField(null=True)
    location = models.CharField(max_length=255, null=True)
    kitchen = models.CharField(max_length=255, null=True)
    novy = models.BooleanField(default=False)
    insta = models.CharField(max_length=255, null=True)
    whatsapp = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.title


class RestaurantImage(models.Model):
    post = models.ForeignKey(Restaurant, default=None, on_delete=models.CASCADE)
    images = models.ImageField()
    def __str__(self):
        return self.post.title


class Favorites(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    restaurants = models.ManyToManyField(Restaurant, default=None, null=True)


class Certificate(models.Model):
    sum = models.FloatField()
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    encode = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, default=None, on_delete=models.CASCADE)