from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import Restaurant, RestaurantImage, SumOfCredit, PeriodOfCredit, Tag

class RestaurantImageForm(ModelForm):
    class Meta:
        model = RestaurantImage
        fields = ['images']

class RestaurantForm(ModelForm):
    images = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False,
        label='Добавить фотографии',
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),  # Provide queryset of Tag objects
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label='Категории',
    )
    class Meta:
        model = Restaurant
        fields = ['logo', 'title', 'description', 'location', 'average','tags','image',
                  'kitchen', 'phone_number', 'work_days_1', 'sum_of_credit', 'period_of_credit',
                  'work_hours_1', 'work_days_2', 'work_hours_2', 'images', 'whatsapp', 'insta', 'slug']


    # period_of_credit = forms.ModelMultipleChoiceField(
    #     queryset=PeriodOfCredit.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     label='Срок кредита',
    #     required=False
    # )
    #
    # sum_of_credit = forms.ModelMultipleChoiceField(
    #     queryset=SumOfCredit.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     label='Сумма кредита'
    # )

    def save(self, commit=True):
        restaurant = super().save(commit=commit)

        if self.cleaned_data.get('tags1'):
            restaurant.tags.add(self.cleaned_data['tags1'])

        if self.cleaned_data.get('tags2'):
            restaurant.tags.add(self.cleaned_data['tags2'])

        for sum_of_credit in self.cleaned_data['sum_of_credit']:
            restaurant.sum_of_credit.add(sum_of_credit)

        for period_of_credit in self.cleaned_data['period_of_credit']:
            restaurant.period_of_credit.add(period_of_credit)

        image = self.cleaned_data['images']
        if image:
            RestaurantImage.objects.create(post=restaurant, images=image)

        return restaurant



class MyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Дополнительные настройки формы, если необходимо
        # Например, можно изменить атрибуты полей или добавить свои поля

    def clean(self):
        cleaned_data = super().clean()
        # Дополнительная валидация, если необходимо
        return cleaned_data
