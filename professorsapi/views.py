import base64

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from persiantools.jdatetime import JalaliDate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from professorsapi.decorators import professor_only
from studentsapi.serializers import *


# Create your views here.
### Home page
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def homePage(request):
    locations = Location.objects.all()

    return Response(
        {
            'locations': LocationSerializer(locations, many=True).data
        }
    )


### profile

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def getProfileDetails(request):
    return Response(
        UserSerializerSelfProfessor(request.user, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def getProfessorDetails(request):
    user = User.objects.get(id=request.POST['user_id'])

    return Response(
        UserSerializerProfile(user, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@professor_only
def updateProfile(request):
    user = request.user
    user.name = request.POST['name']
    user.family = request.POST['family']
    user.email = request.POST['email']
    user.bio = request.POST['bio'][:200]
    user.phone = request.POST['phone']
    user.save()
    return Response(UserSerializerSelfProfessor(user, many=False).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def updateAvatar(request):
    image_data = request.POST['avatar']
    ext = request.POST['ext']

    data = ContentFile(base64.b64decode(image_data))

    file_name = f'{time.time()}' + ext
    request.user.avatar.save(file_name, data, save=True)  # image is User's model field

    return Response(UserSerializerSelfProfessor(request.user, many=False).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def addReference(request):
    file_data = request.POST['file']
    file_ext = request.POST['file_ext']

    cover_data = request.POST['cover']
    cover_ext = request.POST['cover_ext']
    file = ContentFile(base64.b64decode(file_data))
    cover = ContentFile(base64.b64decode(cover_data))

    file_name = f'{time.time()}' + file_ext
    cover_name = f'{time.time()}' + cover_ext

    reference = Reference.objects.create(
        name=request.POST['name'],
        description=request.POST['description'],
        user=request.user,
    )

    reference.file.save(file_name, file, save=True)
    reference.cover.save(cover_name, cover, save=True)
    # request.user.avatar.save(file_name, data, save=True)  # image is User's model field

    return Response(UserSerializerSelfProfessor(request.user, many=False).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def deleteReference(request, id):
    reference = Reference.objects.get(id=id)
    if reference.delete():
        return Response(
            UserSerializerProfile(
                request.user, many=False
            ).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def updateLocation(request):
    user = request.user
    location = Location.objects.get(id=request.POST['location_id'])
    user.location = location
    user.save()
    return Response(
        UserSerializerSelfProfessor(user, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def addContact(request):
    user = User.objects.get(id=request.user.id)
    contact_sr = ContactSerializer(data=request.POST, many=False)
    if contact_sr.is_valid():
        contact_sr.save()
        return Response(
            UserSerializerProfile(
                user, many=False
            ).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            contact_sr.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def deleteContact(request, id):
    contact = Contact.objects.get(id=id)
    if contact.delete():
        return Response(
            UserSerializerProfile(
                request.user, many=False
            ).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


### posts

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allPosts(request):
    post = Post.objects.exclude(user=request.user).order_by('-id')
    return Response(
        PostSerializerDetailed(post, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allSkills(request):
    skills = Skill.objects.order_by('-id')
    return Response(
        SkillSerializer(skills, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@professor_only
def allAppointments(request):
    user = User.objects.get(id=request.user.id)
    received = Appointment.objects.filter(professor=user).filter(state=0).order_by('-id')
    rejected = Appointment.objects.filter(professor=user).filter(state=2).order_by('-id')
    accepted = Appointment.objects.filter(professor=user).filter(state=1).order_by('-id')
    return Response(
        {
            'received': AppointmentSerializer(received, many=True).data,
            'rejected': AppointmentSerializer(rejected, many=True).data,
            'accepted': AppointmentSerializer(accepted, many=True).data,
        }, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@professor_only
def allAppointmentsAccepted(request):
    user = User.objects.get(id=request.user.id)
    appointments = Appointment.objects.filter(professor=user).filter(state=1).order_by('-id')
    return Response(
        AppointmentSerializer(appointments, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allAppointmentsRejected(request):
    user = User.objects.get(id=request.user.id)
    appointments = Appointment.objects.filter(professor=user).filter(state=2).order_by('-id')
    return Response(
        AppointmentSerializer(appointments, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@professor_only
def buildNewAppointment(request):
    Appointment.objects.create(
        title=request.data['title'],
        description=request.data['description'],
        time=request.data['time'],
        state=1,
        professor_id=request.user.id,
        student_id=request.data['student_id']
    )
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@professor_only
def setUpAppointment(request):
    appointment = Appointment.objects.get(id=request.data['appointment_id'])
    appointment.time = request.data['time']
    appointment.state = 1
    appointment.save()
    date_in_persian = JalaliDate.fromtimestamp(int(appointment.time)).strftime("%Y/%m/%d")
    # context = {
    #     'subject': appointment.title,
    #     'content': f"""
    #                 روز بخیر  {appointment.student.name} \n
    #                 استاد {appointment.professor.name} درخواست ملاقات شمارا پذیرفتند.
    #                 در تاریخ {date_in_persian} میتوانید به دفتر ایشان مراجعه کنید.
    #
    #             """
    # }
    # message = get_template('layouts/mail/email_layout.html').render(context)
    # msg = EmailMessage(
    #     appointment.title,
    #     message,
    #     'notification@gethermes.ir',
    #     [appointment.student.email],
    # )
    # msg.content_subtype = "html"  # Main content is now text/html
    # msg.send()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@professor_only
def rejectAppointment(request):
    appointment = Appointment.objects.get(id=request.data['appointment_id'])

    appointment.state = 2
    appointment.save()
    # context = {
    #     'subject': appointment.title,
    #     'content': f"""
    #                     روز بخیر  {appointment.student.name} \n
    #                     استاد {appointment.professor.name} درخواست ملاقات شمارا رد کردند.
    #
    #                 """
    # }
    # message = get_template('layouts/mail/email_layout.html').render(context)
    # msg = EmailMessage(
    #     appointment.title,
    #     message,
    #     'notification@gethermes.ir',
    #     ['business.hasannejad@gmail.com'],
    # )
    # msg.content_subtype = "html"  # Main content is now text/html
    # msg.send()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allAppointmentsReceived(request):
    user = User.objects.get(id=request.user.id)
    appointments = Appointment.objects.filter(professor=user).filter(state=0).order_by('-id')
    return Response(
        AppointmentSerializer(appointments, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allImages(request):
    images = PostImage.objects.all()
    return Response(
        PostImageSerializer(images, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allMyPosts(request):
    post = request.user.post_set.order_by('-id')
    return Response(
        PostSerializerDetailed(post, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allMyRequests(request):
    user = User.objects.get(id=request.user.id)

    requests = AnnounceRequest.objects.filter(announce__user=user).order_by('-id')

    return Response(
        AnnounceRequestSerializerDetailed(requests, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def getPostDetails(request, id):
    post = Post.objects.get(id=id)
    return Response(
        PostSerializerDetailed(post, many=False).data, status=status.HTTP_200_OK
    )


### locations

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allLocations(request):
    locations = Location.objects.order_by('-id')
    return Response(
        LocationSerializer(locations, many=True).data, status=status.HTTP_200_OK
    )


### contact types

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allContactTypes(request):
    contactypes = ContactType.objects.order_by('-id')
    return Response(
        ContactTypeSerializer(contactypes, many=True).data, status=status.HTTP_200_OK
    )


### announces

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def allAnnounces(request):
    announce = Announce.objects.exclude(user=request.user).order_by('-id')
    return Response(
        AnnounceSerializerList(announce, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@professor_only
def allMyAnnounces(request):
    announce = request.user.announce_set.order_by('-id')
    return Response(
        AnnounceSerializerList(announce, many=True).data, status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@professor_only
def getAnnounceDetails(request, id):
    announce = Announce.objects.get(id=id)
    return Response(
        AnnounceSerializerList(announce, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def addPost(request):
    cover_data = request.POST['cover']
    cover_ext = request.POST['cover_ext']
    cover = ContentFile(base64.b64decode(cover_data))
    cover_name = f'{time.time()}' + cover_ext
    post = Post.objects.create(
        title=request.POST['title'],
        body=request.POST['body'],
        date=time.time() * 1000,
        user=request.user
    )

    post.cover.save(cover_name, cover, save=True)
    if len(str(request.POST['files']).split(',')) > 0:
        for i in str(request.POST['files']).split(','):
            if len(i) > 0:
                post.postimage_set.add(
                    PostImage.objects.get(id=i)
                )

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def addPostImage(request):
    file = request.POST['file']
    file_ext = request.POST['file_ext']
    file = ContentFile(base64.b64decode(file))
    file_name = f'{time.time()}' + file_ext
    final_file = PostImage.objects.create(
        name=request.POST['file_name'],
    )
    final_file.file.save(file_name, file, save=True)
    return Response(PostImageSerializer(final_file, many=False).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@professor_only
def addAnnounce(request):
    announce = Announce.objects.create(
        title=request.data['title'],
        body=request.data['body'],
        date=time.time() * 1000,
        user=request.user
    )

    cover_data = request.data['cover']


    format, imgstr = cover_data.split(';base64,')
    ext = format.split('/')[-1]
    cover_name = f'{int(time.time())}.{ext}'
    data = ContentFile(base64.b64decode(imgstr))

    announce.cover.save(cover_name, data, save=True)
    print(request.data['skills'])
    for i in str(request.data['skills']).split(','):
        if len(Skill.objects.filter(name__contains=i)) == 0:
            skill = Skill.objects.create(
                name=i
            )
            announce.skills.add(skill)
        else:
            skill = Skill.objects.filter(name__contains=i).first()
            announce.skills.add(skill)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def addContact(request):
    user = User.objects.get(id=request.user.id)
    contact_type = ContactType.objects.get(id=request.POST['type_id'])
    contact = Contact.objects.create(
        name=request.POST['name'],
        value=request.POST['value'],
        owner=user,
        type=contact_type
    )

    return Response(
        UserSerializerProfile(user, many=False).data, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def addImage(request):
    image_data = request.POST['image']
    ext = request.POST['ext']
    image = PostImage.objects.create()
    data = ContentFile(base64.b64decode(image_data))
    file_name = f'{time.time()}' + ext
    image.save(file_name, data, save=True)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def deletePost(request, id):
    post = Post.objects.get(id=id)
    if post.delete():
        return Response(
            UserSerializerSelfProfessor(
                request.user, many=False
            ).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def deleteAnnounce(request, id):
    announce = Announce.objects.get(id=id)
    if announce.delete():
        return Response(
            UserSerializerSelfProfessor(
                request.user, many=False
            ).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def login(request):
    user = authenticate(request, email=request.POST['email'], password=request.POST['password'])
    if user is not None:
        return Response(
            UserSerializerSelfProfessor(user, many=False).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@professor_only
def changePassword(request):
    user = authenticate(request, email=request.user.email, password=request.POST['last_password'])
    if user is not None:
        user.set_password(request.POST['new_password'])
        return Response(
            UserSerializerSelfProfessor(
                user, many=False
            ).data,
            status=status.HTTP_200_OK
        )
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
