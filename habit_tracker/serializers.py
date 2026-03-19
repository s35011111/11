
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from habit_tracker.models import CustomUser, Habit
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser

        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser

        fields = ['id', 'username', 'email',  'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'date_joined']


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',)
