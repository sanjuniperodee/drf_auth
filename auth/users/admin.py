from django.contrib import admin

from .models import *


class PostImageAdmin(admin.StackedInline):
    model = RestaurantImage

class CertificateAdmin(admin.ModelAdmin):
    list_filter = ('status', 'restaurant', 'start_date', 'end_date')
    list_display = ('id', 'user', 'restaurant', 'status',)


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number')


class StatusAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    # list_display = ('id', 'user', 'restaurant', 'status',)


@admin.register(Restaurant)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageAdmin]
    list_display = ('title', 'id', 'phone_number', 'description',)

    class Meta:
        model = Restaurant


@admin.register(RestaurantImage)
class PostImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Certificate, CertificateAdmin)

# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'restaurant', 'status',)
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

admin.site.register(Favorites)
admin.site.register(Tag)
admin.site.register(Banner)
admin.site.register(User, UserAdmin)
admin.site.register(ImageModel)
admin.site.register(Status, StatusAdmin)

admin.site.register(SumOfCredit)
admin.site.register(PeriodOfCredit)

@admin.register(PortfolieImages)
class PostImageAdmin(admin.ModelAdmin):
    pass
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
