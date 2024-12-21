from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Spam
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated

class MarkSpamView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        phone_number = request.data.get("phone_number")
        user = request.user
        Spam.objects.create(phone_number=phone_number, marked_by=user)
        isSpam = [{"name" : CustomUser.objects.get(phone_number=spam_num.phone_number).name, "phone_number" : spam_num.phone_number} for spam_num in Spam.objects.all()]  
        print(isSpam)
        print(dir(Spam.objects))
        return Response({"message": "Number marked as spam"}, status=status.HTTP_200_OK)
    
class ListSpamNumbers(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            spam_list = [{"name" : CustomUser.objects.get(phone_number=spam_num.phone_number).name, "phone_number" : spam_num.phone_number, "marked-spam-by": spam_num.marked_by.name} for spam_num in Spam.objects.all()]  
            print(spam_list)
            return Response(spam_list, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
class SearchByNameView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        name_query = request.query_params.get("name", "")
        users = CustomUser.objects.filter(name__icontains=name_query).order_by('name')
        results = [{"name": user.name, "phone_number": user.phone_number} for user in users]
        return Response(results, status=status.HTTP_200_OK)
    
class SearchByPhoneView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        phone_query = request.query_params.get("phone", "")
        users = CustomUser.objects.filter(phone_number__icontains=phone_query)
        results = [{"name": user.name, "phone_number": user.phone_number} for user in users]
        return Response(results, status=status.HTTP_200_OK)

class FetchUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = CustomUser.objects.get(name=request.user.name)
            details = {
                "name": user.name,
                "phone_number": user.phone_number,
                "email": user.email if request.user in user.contacts.all() else None,
            }
            return Response(details, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class FetchAllContacts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            all_users = CustomUser.objects.all()
            all_contacts = [{"name" : user.name, "phone_number" : user.phone_number } for user in all_users]
            return Response(all_contacts, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

