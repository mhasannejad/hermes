from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import *

urlpatterns = [
    path('home/', homePage),

    path('login/', login),

    path('profile/update/avatar/', updateAvatar),
    path('profile/update/location/', updateLocation),
    path('profile/update/', updateProfile),
    path('profile/details/', getProfileDetails),
    path('profile/changepassword/', changePassword),

    path('professor/details/', getProfessorDetails),

    path('profile/add/contact/', addContact),
    path('profile/delete/contact/<int:id>/', deleteContact),

    path('profile/add/reference/', addContact),
    path('profile/delete/reference/<int:id>/', deleteReference),

    path('announces/all/', allAnnounces),
    path('announces/all/mine/', allMyAnnounces),
    path('posts/all/', allPosts),
    path('images/all/', allImages),
    path('posts/all/mine/', allMyPosts),
    path('locations/all/', allLocations),
    path('contacttypes/all/', allContactTypes),
    path('skills/all/', allSkills),
    path('appointments/all/', allAppointments),
    path('appointments/all/accepted/', allAppointmentsAccepted),
    path('appointments/all/rejected/', allAppointmentsRejected),
    path('appointments/all/received/', allAppointmentsReceived),

    path('requests/mine/', allMyRequests),

    path('appointments/setup/', setUpAppointment),
    path('appointments/build/', buildNewAppointment),
    path('appointments/reject/', rejectAppointment),

    path('announces/<int:id>/', getAnnounceDetails),
    path('posts/<int:id>/', getPostDetails),

    path('posts/add/', addPost),
    path('posts/file/add/', addPostImage),
    path('announces/add/', addAnnounce),
    path('references/add/', addReference),
    path('contacts/add/', addContact),

    path('posts/delete/<int:id>/', deletePost),
    path('announces/delete/<int:id>/', deleteAnnounce),

    path('images/add/', addImage),

]
