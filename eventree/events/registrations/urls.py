from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    # Registration URLs
    path('', views.RegistrationListView.as_view(), name='registration_list'),
    path('<int:pk>/', views.RegistrationDetailView.as_view(), name='registration_detail'),
    path('<int:pk>/invite/', views.InviteGuestView.as_view(), name='invite_guest'),
    
    # Invitation URLs
    path('invitations/', views.InvitationListView.as_view(), name='invitation_list'),
    path('invitations/<uuid:token>/', views.InvitationDetailView.as_view(), name='invitation_detail'),
    path('invitations/<uuid:token>/accept/', views.InvitationAcceptView.as_view(), name='invitation_accept'),
    path('invitations/<uuid:token>/decline/', views.InvitationDeclineView.as_view(), name='invitation_decline'),
    
    # Verification URLs
    path('verify/<str:token>/', views.VerifyRegistrationView.as_view(), name='verify_registration'),
]
