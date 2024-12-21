from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                username=serializer.validated_data['phone_number'],  # Map phone_number to username
                password=make_password(serializer.validated_data['password'])  # Hash the password
            )
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    permission_classes = [AllowAny]  # No Allow unauthenticated access

    def post(self, request):
        print(request)
        phone_number = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=phone_number, password=password)
        print(f"Authenticating user: username={phone_number}, password={password}, Type: {type(user)}")
        print(f"User: {user}")
        if user and isinstance(user, CustomUser):
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        print("Authentication failed")
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
