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
        phone_query = request.query_params.get("phone", "").strip()
        if not phone_query:
            return Response({"error": "Phone query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        total_users = CustomUser.objects.count()    
        exact_match_found = False  # Flag to track if an exact match is found

        # Check for an exact match with a registered user
        try:
            registered_user = CustomUser.objects.get(phone_number=phone_query)
            spam_count = Spam.objects.filter(phone_number=registered_user.phone_number).values('marked_by').distinct().count()
            spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0

            # Add the exact match result
            results.append({
                "name": registered_user.name,
                "phone_number": registered_user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            })
            exact_match_found = True  # Mark that an exact match is found
        except CustomUser.DoesNotExist:
            pass

        # If exact match is found, return immediately
        if exact_match_found:
            return Response(results, status=status.HTTP_200_OK)

        # Include partial matches for registered users
        partial_users_startwith = CustomUser.objects.filter(phone_number__istartswith=phone_query)
        partial_users_contain = CustomUser.objects.filter(phone_number__icontains=phone_query).exclude(phone_number__istartswith=phone_query)
        partial_users = list(partial_users_startwith) + list(partial_users_contain)
        
        for user in partial_users:
            spam_count = Spam.objects.filter(phone_number__icontains=user.phone_number).values('marked_by').distinct().count()
            spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0

            results.append({
                "name": user.name,
                "phone_number": user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2)
            })

        # Include partial matches from contacts
        contact_results = CustomUser.objects.filter(contacts__phone_number__icontains=phone_query).distinct()
        for user in contact_results:
            try:
                # Get all contacts with matching phone numbers
                matching_contacts = user.contacts.filter(phone_number__icontains=phone_query)
                for contact in matching_contacts:
                    # Calculate spam likelihood for each matching contact
                    spam_count = Spam.objects.filter(phone_number=contact.phone_number).values('marked_by').distinct().count()
                    spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0

                    results.append({
                        "name": contact.name,
                        "phone_number": contact.phone_number,
                        "spam_likelihood": round(spam_likelihood, 2)
                    })
                return Response(results, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error processing contact results: {e}")
        
class FetchUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get user ID or phone number from query parameters
        user_id = request.query_params.get("user_id")
        phone_number = request.query_params.get("phone")

        if not user_id and not phone_number:
            return Response({"error": "Either user_id or phone must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the target user based on ID or phone number
            if user_id:
                target_user = CustomUser.objects.get(id=user_id)
            else:
                target_user = CustomUser.objects.get(phone_number=phone_number)

            # Calculate spam likelihood
            total_users = CustomUser.objects.count()
            spam_count = Spam.objects.filter(phone_number=target_user.phone_number).values('marked_by').distinct().count()
            spam_likelihood = (spam_count / total_users) * 100 if total_users > 0 else 0

            # Check if email can be displayed
            can_show_email = request.user in target_user.contacts.all()

            # Prepare response data
            response_data = {
                "name": target_user.name,
                "phone_number": target_user.phone_number,
                "spam_likelihood": round(spam_likelihood, 2),
                "email": target_user.email if can_show_email else None
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

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

class FetchContactsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            result = set()
            current_user_contacts = CustomUser.objects.get(phone_number=user.phone_number).contacts.all().order_by("name")
            contacts_list = [{ "name" : contact.name, "phone_number": contact.phone_number } for contact in current_user_contacts]
            return Response(contacts_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response("No Results Found", status=status.HTTP_404_NOT_FOUND)
