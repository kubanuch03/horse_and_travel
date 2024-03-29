from decouple import config

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags

from rest_framework import serializers
from .models import CustomUser




class ConfirmEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "password",
            "password2",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Пароль не совпадает, попробуйте еще раз"}
            )
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data.get("username", ""),
            phone_number=validated_data.get("phone_number", ""),
            password=validated_data["password"],
            token_auth=get_random_string(64),
        )

        current_site = get_current_site(self.context["request"])
        domain = current_site.domain
        protocol = "https" if self.context["request"].is_secure() else "http"
        confirmation_link = reverse(
            "users:confirm_email", kwargs={"token": user.token_auth}
        )



        subject = "Подтверждение почты"

        # message = f"""Подтвердите почту по ссылке: \n\n{protocol}://{domain}{confirmation_link}\nВаши данные:\n почта: {client.email}\n пароль: {validated_data["password"]}"""
        html_message = render_to_string('app_user/confirm_email.html', {
                    'protocol': protocol,
                    'domain': domain,
                    'confirmation_link': confirmation_link,
                    'client_email': user.email,
                    'client_password': validated_data["password"],
                })
        text_message = strip_tags(html_message)

        

        email = EmailMultiAlternatives(subject, text_message, from_email=config("EMAIL_HOST_USER"), to=[validated_data["email"]])
        email.attach_alternative(html_message, "text/html")  
        email.send()
        make_password(validated_data["password"])

        return user


class LoginUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password")