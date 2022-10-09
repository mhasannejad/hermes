import base64

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import *


# Create your views here.

#### Appointments

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAppointments(request, professor_id):
    professor = User.objects.get(id=professor_id)
    appointments = Appointment.objects.filter(student=request.user).filter(professor=professor)
    sr = AppointmentSerializer(appointments, many=True)
    return Response(sr.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllUserAppointments(request):
    appointments = Appointment.objects.filter(student=request.user).order_by('-time')
    sr = AppointmentSerializer(appointments, many=True)
    return Response(sr.data)


@api_view(['GET'])
def getAppointment(request, id):
    appointment = Appointment.objects.get(id=id)
    sr = AppointmentSerializer(appointment, many=False)
    return Response(sr.data)


@api_view(['GET'])
def getAppointmentForUser(request):
    appointments = Appointment.objects.filter(student=request.user).order_by('-id')
    sr = AppointmentSerializer(appointments, many=True)
    return Response(sr.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addAppointment(request):
    appointment = Appointment.objects.create(
        title=request.data['title'],
        description=request.data['description'],
        professor_id=request.data['professor_id'],
        time=0,
        student=request.user
    )
    """
    context = {
        'subject': appointment.title,
        'content': f
    #                روز بخیر  {appointment.professor.name} \n
     #               دانشجو {appointment.student.name} درخواست قرار ملاقات  دارد.  
      #              لطفا در اپلیکیشن برسی کنید. 
               
    }
    message = get_template('layouts/mail/email_layout.html').render(context)
    msg = EmailMessage(
        appointment.title,
        message,
        'notification@gethermes.ir',
        [appointment.professor.email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()"""

    return Response(AppointmentSerializer(appointment).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteAppointment(request, id):
    appointment = Appointment.objects.get(id=id)
    appointment.delete()
    return Response(status=status.HTTP_200_OK)


#### professor profile

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateProfile(request):
    user = request.user
    user.stud_code = request.data['stud_code']
    user.id_code = request.data['id_code']
    if request.data['email'] != '' and len(request.data['email']) > 0:
        user.email = request.data['email']
    user.bio = request.data['bio'][:200]
    user.phone = request.data['phone']
    user.name = request.data['name']
    user.family = request.data['family']
    user.save()
    return Response(UserSerializerSelf(user, many=False).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updatePassword(request):
    success = request.user.check_password(request.data['previous_pass'])
    if not success:
        return Response(status=status.HTTP_403_FORBIDDEN)

    request.user.set_password(request.data['new_pass'])
    return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAvatar(request):
    image_data = request.POST['avatar']
    ext = request.POST['ext']

    data = ContentFile(base64.b64decode(image_data))

    file_name = f'{time.time()}' + ext
    request.user.avatar.save(file_name, data, save=True)  # image is User's model field

    return Response(UserSerializerSelf(request.user, many=False).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateAvatarFile(request):
    print(request.FILES)

    myfile = request.data.get('image')

    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    request.user.avatar = uploaded_file_url

    return Response(UserSerializerSelf(request.user, many=False).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfessorProfile(request, id):
    professor = User.objects.get(id=id)
    if professor.mode != User.MODES[2][0]:
        return Response(status=status.HTTP_409_CONFLICT)
    appointments = Appointment.objects.filter(student=request.user).filter(professor=professor).order_by('-id')
    appointments_sr = AppointmentSerializer(appointments, many=True)
    professor_sr = UserSerializerProfile(professor, many=False)
    return Response({
        'professor': professor_sr.data,
        'appointments': appointments_sr.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getProfessors(request):
    professors = User.objects.filter(mode=2)
    return Response(
        UserSerializerListItem(professors, many=True).data
    )


### Main page

@api_view(['GET'])
def mainPage(request):
    main_page = Setting.objects.get(key=settings.MAIN_PAGE_PROFS_DISPLAY_LOCATION)
    location = Location.objects.get(id=main_page.value)
    profs = User.objects.filter(location=location).filter(mode=User.MODES[2][0])
    sr = UserSerializerListItem(profs, many=True)
    return Response(
        {
            'profs': sr.data
        }
    )


#### posts

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPostDetails(request, id):
    post = Post.objects.get(id=id)
    return Response(
        PostSerializerDetailed(post, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def allPosts(request):
    post = Post.objects.order_by('-id')
    return Response(
        PostSerializerDetailed(post, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def allPostsFilterByGroup(request):
    groups = request.POST['groups'].split(',')
    expertise = request.POST['expertise'].split(',')
    professors = request.POST['professors'].split(',')
    print(request.POST)
    print(groups)
    print(expertise)
    if groups == ['']:
        groups = []

    if expertise == ['']:
        print(expertise)
        expertise = []

    if professors == ['']:
        professors = []

    print((professors))
    posts = Post.objects.filter(Q(user__group__in=groups) | Q(user__expertise__in=expertise) | Q(user__in=professors))
    print(len(posts))
    # posts = Post.objects.all()

    return Response(
        PostSerializerDetailed(posts, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def allProfessorsFiltered(request):
    print(request.data['expertise'])
    groups = list(map(lambda x: x['id'], request.data['groups']))
    expertise = list(map(lambda x: x['id'], request.data['expertise']))
    locations = list(map(lambda x: x['id'], request.data['locations']))
    print(request.POST)
    print(groups)
    print(locations)
    if groups == ['']:
        groups = []

    if expertise == ['']:
        print(expertise)
        expertise = []

    if locations == ['']:
        locations = []

    profs = User.objects.filter(Q(group__in=groups) | Q(expertise__in=expertise) | Q(location__in=locations)).filter(
        mode=2)
    posts = Post.objects.all()

    return Response(
        UserSerializerListItem(profs, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def allAnnouncesFiltered(request):
    skills = request.POST['skills'].split(',')
    expertise = request.POST['expertise'].split(',')
    professors = request.POST['professors'].split(',')
    print(request.POST)
    if skills == ['']:
        skills = []

    if expertise == ['']:
        expertise = []

    if professors == ['']:
        professors = []

    announces = Announce.objects.filter(
        Q(user__expertise__in=expertise) | Q(skills__in=skills) | Q(user__in=professors))
    # posts = Post.objects.all()

    return Response(
        AnnounceSerializerList(announces, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def allAnnounces(request):
    announce = Announce.objects.order_by('-id')
    return Response(
        AnnounceSerializerList(announce, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAnnounceDetails(request, id):
    announce = Announce.objects.get(id=id)
    return Response(
        AnnounceSerializerList(announce, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addAnnounceRequest(request):
    announce, created = AnnounceRequest.objects.get_or_create(
        student=request.user,
        announce_id=request.data['announce_id'],
        description=request.data['description']
    )
    if created:
        return Response(
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getPostFilters(request):
    groups = ProfessorGroup.objects.all()
    expertise = Expertise.objects.all()
    professors = User.objects.filter(mode=2)
    return Response(
        {
            'groups':
                GroupSerializer(groups, many=True).data,
            'expertise': ExpertiseSerializer(expertise, many=True).data,
            'professors': UserSerializerListItem(professors, many=True).data
        }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getProfessorFilters(request):
    groups = ProfessorGroup.objects.all()
    expertise = Expertise.objects.all()
    locations = Location.objects.all()
    return Response(
        {
            'groups':
                GroupSerializer(groups, many=True).data,
            'expertise': ExpertiseSerializer(expertise, many=True).data,
            'locations': LocationSerializer(locations, many=True).data
        }
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getAnnounceFilters(request):
    skills = Skill.objects.all()
    expertise = Expertise.objects.all()
    professors = User.objects.filter(mode=2)
    return Response(
        {
            'skills':
                SkillSerializer(skills, many=True).data,
            'expertise': ExpertiseSerializer(expertise, many=True).data,
            'professors': UserSerializerListItem(professors, many=True).data
        }
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def filterPostsByText(request):
    search_term = request.POST['search_term']
    posts = Post.objects.filter(Q(title__contains=search_term) | Q(body__contains=search_term))
    return Response(
        PostSerializerDetailed(posts, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def filterProfessorsByText(request):
    search_term = request.POST['search_term']
    profs = User.objects.filter(name__contains=search_term).filter(mode=2)
    return Response(
        UserSerializerListItem(profs, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def filterAnnouncesByText(request):
    search_term = request.POST['search_term']
    announces = Announce.objects.filter(Q(title__contains=search_term) | Q(body__contains=search_term))
    return Response(
        AnnounceSerializerList(announces, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getCircles(request):
    circles = Circle.objects.all()
    return Response(
        CircleSerializer(circles, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def addCircleToProfile(request):
    print(request.POST)
    user = User.objects.get(id=request.user.id)
    circle = Circle.objects.get(id=request.POST['circle_id'])
    if circle not in user.circles.all():
        circle.user_set.add(user)
    else:
        pass
    return Response(
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteMyCircle(request):
    print(request.POST)
    user = User.objects.get(id=request.user.id)
    circle = Circle.objects.get(id=request.POST['circle_id'])
    user.circles.remove(circle)
    return Response(
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getMyCircles(request):
    user = User.objects.get(id=request.user.id)
    return Response(
        CircleSerializer(
            user.circles.all(), many=True
        ).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def userData(request):
    user = User.objects.get(id=request.user.id)
    sr = UserSerializerSelf(user)
    return Response(
        sr.data, status=status.HTTP_200_OK
    )
