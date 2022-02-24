from rest_framework import serializers
from .models import MyUser
from django.core.validators import EmailValidator


class LoginModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = []

    def is_valid(self, raise_exception=False):
        valid = super(LoginModelSerializer, self).is_valid()
        temp_errors = {}
        for field in ['login', 'password']:
            if field not in self.initial_data:
                temp_errors[field] = 'This field is required'

        if len(temp_errors) > 0:
            self._errors.update(**temp_errors)

            return False

        self.validated_data['login'] = self.initial_data['login']
        self.validated_data['password'] = self.initial_data['password']

        return valid

    def get_instance(self):
        login = self.validated_data['login']
        return MyUser.objects.get(email=login)


class PrivateCreateUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ["first_name", "last_name", "email", "is_admin", "password"]

    def is_valid(self, raise_exception=False):
        temp_data = self.initial_data.copy()
        valid = super(PrivateCreateUserModelSerializer, self).is_valid()

        for field in ['other_name', 'phone', 'birthday', 'city', 'additional_info']:
            if field in temp_data:
                self.validated_data[field] = temp_data[field]

        return valid


class PrivateUpdateUserModelSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    other_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_admin = serializers.BooleanField(required=False)
    birthday = serializers.DateField(required=False)
    city = serializers.IntegerField(required=False)
    additional_info = serializers.CharField(required=False)


# class PrivateUpdateUserModelSerializer(serializers.ModelSerializer):
#     fields = ['first_name', 'last_name', 'other_name', 'phone', 'id', 'birthday', 'city', 'additional_info',
#               'email', 'is_admin']
#
#     class Meta:
#         model = MyUser
#         fields = []
#
#     def is_valid(self, raise_exception=False):
#         temp_data = self.initial_data.copy()
#         valid = super(PrivateUpdateUserModelSerializer, self).is_valid()
#
#         for field in self.fields:
#             if field in temp_data:
#                 self.validated_data[field] = temp_data[field]
#
#         return valid


# class UpdateUserModelSerializer(PrivateUpdateUserModelSerializer):
#     class Meta:
#         model = MyUser
#         fields = []
#
#     def __init__(self):
#         self.fields = ['first_name', 'last_name', 'other_name', 'phone', 'birthday', 'email']


class UpdateUserModelSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    other_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
