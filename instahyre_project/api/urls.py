from django.urls import path
from .views import (
    MarkSpamView, SearchByNameView, SearchByPhoneView, FetchUserDetailsView, FetchAllContacts, ListSpamNumbers, FetchUserDetailsByIdView
)

urlpatterns = [
    path('spam/', MarkSpamView.as_view(), name='mark-spam'),
    path('search/name/', SearchByNameView.as_view(), name='search-by-name'),
    path('search/phone/', SearchByPhoneView.as_view(), name='search-by-phone'),
    path('user/details/', FetchUserDetailsView.as_view(), name='fetch-user-details'),
    path('get-all-contacts/', FetchAllContacts.as_view(), name='fetch-all-users-details'),
    path('get-all-spam-details/', ListSpamNumbers.as_view(), name='list-all-spam-number-details'),
    path('user/details-by-id/', FetchUserDetailsByIdView.as_view(), name='fetch-user-details-by-id'),
]
