from django.contrib import admin

from .models import Restaurant, RestaurantImage, Tag, Certificate, Favorites, ImageModel, User, Status


class PostImageAdmin(admin.StackedInline):
    model = RestaurantImage


@admin.register(Restaurant)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageAdmin]

    class Meta:
        model = Restaurant


@admin.register(RestaurantImage)
class PostImageAdmin(admin.ModelAdmin):
    pass

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'status',)
    # list_display = ('id', 'user', 'restaurant', 'status',)
    # actions = ['mark_as_activated', 'mark_as_non_activated']
    #
    # def mark_as_activated(self, request, queryset):
    #     queryset.update(status=True)
    #
    # def mark_as_non_activated(self, request, queryset):
    #     queryset.update(status=False)
    #
    # mark_as_activated.short_description = "Mark selected certificates as Activated"
    # mark_as_non_activated.short_description = "Mark selected certificates as Non-Activated"

# admin.site.register(Certificate)
admin.site.register(Favorites)
admin.site.register(Tag)
admin.site.register(User)
admin.site.register(ImageModel)
admin.site.register(Status)
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
