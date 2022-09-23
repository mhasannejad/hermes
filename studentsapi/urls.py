from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('home/', mainPage),
    path('appointments/', getAppointments),
    path('appointments/mine/', getAllUserAppointments),
    path('appointments/create/', addAppointment),
    path('announcerequest/create/', addAnnounceRequest),
    path('appointments/delete/<int:id>/', deleteAppointment),
    path('appointments/<int:id>/', getAppointment),
    path('appointments/user/<int:id>/', getAppointmentForUser),
    path('professor/profile/<int:id>/', getProfessorProfile),
    path('professor/all/', getProfessors),
    path('post/<int:id>/', getPostDetails),
    path('post/all/', allPosts),
    path('circle/all/', getCircles),
    path('circle/add/', addCircleToProfile),
    path('circle/delete/', deleteMyCircle),
    path('circle/mine/', getMyCircles),
    path('professors/filtered/', allProfessorsFiltered),
    path('announces/filtered/', allAnnouncesFiltered),
    path('professors/filtered/search/', filterProfessorsByText),
    path('announces/filtered/search/', filterAnnouncesByText),
    path('post/filter/', allPostsFilterByGroup),
    path('post/filter/search/', filterPostsByText),
    path('profile/update/', updateProfile),
    path('profile/update/avatar/', updateAvatar),
    path('profile/update/password/', updatePassword),
    path('profile/update/avatar/file/', updateAvatarFile),
    path('announce/all/', allAnnounces),
    path('filter/all/', getPostFilters),
    path('filter/all/professors/', getProfessorFilters),
    path('filter/all/announces/', getAnnounceFilters),
    path('announce/<int:id>/', getAnnounceDetails),
    path('mydata/', userData),

]
