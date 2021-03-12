from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.contrib.auth import (
    get_user_model,
    password_validation,
    authenticate,
)
from django.shortcuts import get_object_or_404

from django.contrib.auth.password_validation import validate_password
from django.core import validators
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserRegSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    username = serializers.CharField(
        required=True, max_length=50,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    password = serializers.CharField(
        min_length=6, max_length=50, write_only=True,
        style={
            'input_type': 'password'
        })
    confirm_password = serializers.CharField(
        min_length=6, max_length=50, write_only=True,
        style={
            'input_type': 'password'
        })

    class Meta:
        model = User
        fields = ("username", "email", "password", "confirm_password", 'address')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('Password mismatch')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CustomUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=50, required=True
    )
    password = serializers.CharField(
        max_length=60, required=True, write_only=True,
        style={
            'input_type': 'password',
        },
    )

    # class Meta:
    #     model = User
    #     fields = ('email')

    def validate(self, attrs):
        try:
            user = authenticate(**attrs)
        except:
            raise serializers.ValidationError("Login ValidationError")
        # if user and user.is_active:
        if user:
            return user
        return serializers.ValidationError("Unable to log in with provided credentials.")


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "address"]
