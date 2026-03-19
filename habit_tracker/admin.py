from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from habit_tracker.models import Habit, CustomUser


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'place', 'action',
                    'habit_type', 'reward', 'connected_habit', 'start_time',
                    'is_public']
    list_filter = ['user', 'habit_type', 'is_public']
    search_fields = ['user', 'place', 'action', ]

    list_per_page = 20
    ordering = ['start_time']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser', 'groups',
                                    'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
