from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import Profile
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name','mobile_no', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def create(self, validated_data):
        validated_data = self.validated_data
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        profile = Profile.objects.create(user=user)
        return user

    # def save(self, request):
    #     validated_data = self.validated_data
    #     password = validated_data.pop('password')
    #     user = User(**validated_data)
    #     user.set_password(password)
    #     user.save()
    #     profile = Profile.objects.create(user=user)
    #     return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name','mobile_no', 'role']
        extra_kwargs = {
            'email':{'read_only': True},
            'role': {'read_only': True},
       }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['password', 'email', 'tokens']

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        return {
            'email': user.email,
            'tokens': user.tokens
        }

class ProfileSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(required=False)



    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'age', 'location','profile_pic']

    def update(self, instance, validated_data):
        """ Update user and profile fields """

        # Extract and update user data separately
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user  # Get related user
            for attr, value in user_data.items():
                setattr(user, attr, value)  # Set new values
            user.save()

        # Update Profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

