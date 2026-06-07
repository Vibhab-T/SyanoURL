from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


#serializers classes are sort of a mixture of DTO, Validators, .net ko mapper/adapter classes jasto 
#basically the serializer class is called when recievinf and sending the data via APIs
#Serializers le suruma proper format(json) ma lagdincha, and it can validate, save, and create data. 


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")

    def validate(self, data): 
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # extends the default jwt login respoins to include basic user info
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data