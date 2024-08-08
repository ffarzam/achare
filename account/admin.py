from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import RecycleUser, User


# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = (
        "phone",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    list_filter = (
        "phone",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    fieldsets = (
        (None, {"fields": ("phone", "email", "password", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("phone", "email")
    ordering = []


@admin.register(RecycleUser)
class RecycleUserAdmin(admin.ModelAdmin):
    actions = ["restore_deleted_items"]
    list_display = (
        "phone",
        "deleted_at",
    )

    def get_queryset(self, request):
        return RecycleUser.deleted_object.filter(is_deleted=True)

