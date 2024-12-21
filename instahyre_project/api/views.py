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

        # Prevent marking own number as spam
        if phone_number == user.phone_number:
            return Response({"error": "You cannot mark your own number as spam."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate spam entries
        spam_entry_exists = Spam.objects.filter(phone_number=phone_number, marked_by=user).exists()
        if spam_entry_exists:
            return Response({"message": "This number is already marked as spam by you."}, status=status.HTTP_200_OK)

        # Create a new spam entry
        Spam.objects.create(phone_number=phone_number, marked_by=user)
        return Response({"message": "Number marked as spam."}, status=status.HTTP_200_OK)
    
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
        name_query = request.query_params.get("name", "").strip()
        if not name_query:
            return Response({"error": "Name query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Users whose names start with the query
        starts_with_results = CustomUser.objects.filter(name__istartswith=name_query)

        # Users whose names contain the query but don't start with it
        contains_results = CustomUser.objects.filter(name__icontains=name_query).exclude(name__istartswith=name_query)

        # Combine results, prioritize starts_with
        results = list(starts_with_results) + list(contains_results)

        # Create response data with spam likelihood
        total_users = CustomUser.objects.count()
        response_data = []
        for user in results:
            spam_count = Spam.objects.filter(phone_number=user.phone_number).values('marked_by').distinct().count()
            spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0
            response_data.append({
                "name": user.name,
                "phone_number": user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            })

        return Response(response_data, status=status.HTTP_200_OK)

class SearchByPhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phone_query = request.query_params.get("phone", "")
        users = CustomUser.objects.filter(phone_number__icontains=phone_query)
        total_users = CustomUser.objects.count()

        results = []
        for user in users:
            spam_count = Spam.objects.filter(phone_number=user.phone_number).values('marked_by').distinct().count()
            spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0
            results.append({
                "name": user.name,
                "phone_number": user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            })

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

class FetchUserDetailsByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user ID from query parameters
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the target user by ID
            target_user = CustomUser.objects.get(id=user_id)

            # Calculate spam likelihood
            total_users = CustomUser.objects.count()
            spam_count = Spam.objects.filter(phone_number=target_user.phone_number).values('marked_by').distinct().count()
            spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0

            # Determine if email can be shown
            show_email = request.user in target_user.contacts.all()

            # Prepare response data
            response_data = {
                "name": target_user.name,
                "phone_number": target_user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2),
                "email": target_user.email if show_email else None
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class FetchAllContacts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            all_users = CustomUser.objects.all()
            all_contacts = [{"name" : user.name, "phone_number" : user.phone_number } for user in all_users]
            return Response(all_contacts, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

