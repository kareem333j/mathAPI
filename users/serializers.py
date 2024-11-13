from rest_framework import serializers
from .models import NewUser,Profile
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewUser
        fields = ('phone','first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)  
        instance = self.Meta.model(**validated_data)
        if password is not None: # if password is ((NOT) None) set it
            instance.set_password(password)
        instance.save()
        return instance
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id','parent_phone', 'state','gender','grade')
        # extra_kwargs = {}
    
    
class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = NewUser
        fields = ('id','phone','first_name','last_name','profile','email',  'password', 'password2')


    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = NewUser.objects.create(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user