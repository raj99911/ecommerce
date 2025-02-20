from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,RetrieveUpdateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, pagination
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer, UserSerializer,ProfileSerializer
from .models import User,Profile
from rest_framework_simplejwt.views import TokenObtainPairView

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid()

            # token, created = Token.objects.get_or_create(user=user)
            # return Response({"token": token.key, "user": UserSerializer(user).data})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserRegistration(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         user = serializer.save()
    #         profile = Profile.objects.create(user=user)
    #         profile.save()
    #
    #     return Response(serializer.data,status=status.HTTP_201_CREATED)



class ProfileView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get_object(self):
        return self.request.user.profile



class Dashboard(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'userdashboard.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff :
            return Response(template_name='admindashboard.html')
        else:
            return Response(template_name='userdashboard.html')



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # refresh_token = request.data["refresh"]
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()


            return Response({"message": "Successfully logged out"},status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'Detail':str(e)},status=status.HTTP_400_BAD_REQUEST)




