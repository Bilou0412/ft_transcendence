from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

def validate_password_strength(value):
    """Checks if the password meets strength requirements."""
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[@$!%*?&]", value):
        raise ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &).")


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password, validate_password_strength]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'email']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return value

    def validate(self, data):
        # Vérifie si les mots de passe correspondent
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Supprime le champ de confirmation
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password, validate_password_strength])
    old_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password, validate_password_strength])

class UserSerializer42(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

    def create(self, validated_data):
        # Créez l'utilisateur sans mot de passe
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=True  # Activez l'utilisateur immédiatement
        )
        user.save()
        return user