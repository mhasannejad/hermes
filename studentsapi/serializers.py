from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ImageField

from coreapp.models import *


class ThumbnailSerializer(ImageField):
    def __init__(self, alias, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_only = True
        self.alias = alias

    def to_representation(self, value):
        if not value:
            return None

        url = thumbnail_url(value, self.alias)
        request = self.context.get('request', None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class ContactTypeSerializer(ModelSerializer):
    class Meta:
        model = ContactType
        fields = '__all__'


class ContactSerializer(ModelSerializer):
    type = ContactTypeSerializer(many=False)

    class Meta:
        model = Contact
        fields = '__all__'


class PostImageSerializer(ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'


class PostSerializer(ModelSerializer):
    images = PostImageSerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'images', 'date', 'cover']


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token


class UserSerializerSelf(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'family', 'id_code', 'stud_code', 'entrance_date', 'email', 'avatar',
                  'phone', 'bio', 'mode']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        depth = 1


class ExpertiseSerializer(ModelSerializer):
    class Meta:
        model = Expertise
        fields = '__all__'


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class GroupSerializer(ModelSerializer):
    class Meta:
        model = ProfessorGroup
        fields = '__all__'


class ReferenceSerializer(ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'


class SkillSerializer(ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class UserSerializerListItem2(ModelSerializer):
    expertise = ExpertiseSerializer(many=False)
    avatar = ThumbnailSerializer(alias='avatar')
    location = LocationSerializer(many=False)
    official_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'name', 'family', 'email', 'expertise', 'avatar', 'location', 'phone', 'bio', 'official_name']


class AnnounceSerializerList2(ModelSerializer):
    user = UserSerializerListItem2(many=False)
    skills = SkillSerializer(many=True)

    class Meta:
        model = Announce
        fields = ['id', 'title', 'body', 'cover', 'date', 'user', 'skills']


class AnnounceRequestSerializer(ModelSerializer):
    student = UserSerializerListItem2()
    professor = UserSerializerListItem2()
    announce = AnnounceSerializerList2()

    class Meta:
        model = AnnounceRequest
        fields = ['id', 'description', 'student', 'professor', 'announce']


class AnnounceSerializerList(ModelSerializer):
    user = UserSerializerListItem2(many=False)
    skills = SkillSerializer(many=True)
    requests = AnnounceRequestSerializer(many=True)

    class Meta:
        model = Announce
        fields = ['id', 'title', 'body', 'cover', 'date', 'user', 'skills', 'requests']


class UserSerializerProfile(ModelSerializer):
    posts = PostSerializer(many=True)
    announces = AnnounceSerializerList(many=True)
    contacts = ContactSerializer(many=True)
    avatar = ThumbnailSerializer(alias='avatar')
    expertise = ExpertiseSerializer(many=False)
    group = GroupSerializer(many=False)
    location = LocationSerializer(many=False)
    references = ReferenceSerializer(many=True)
    official_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'name', 'family', 'email', 'posts', 'contacts', 'avatar', 'group', 'expertise', 'location',
                  'references', 'phone', 'bio', 'official_name', 'announces']
        depth = 4


class UserSerializerListItem(ModelSerializer):
    expertise = ExpertiseSerializer(many=False)
    avatar = ThumbnailSerializer(alias='avatar')
    location = LocationSerializer(many=False)
    official_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'name', 'family', 'email', 'expertise', 'avatar', 'location', 'phone', 'bio', 'official_name']


class AppointmentSerializer(ModelSerializer):
    professor = UserSerializerProfile(many=False)
    student = UserSerializerProfile(many=False)

    class Meta:
        model = Appointment
        fields = ['id', 'title', 'description', 'time', 'student', 'professor', 'state']


class AppointmentSerializerInsert(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'title', 'description', 'student', 'professor']


class PostSerializerDetailed(ModelSerializer):
    images = PostImageSerializer(many=True)
    user = UserSerializerListItem(many=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'images', 'date', 'user', 'cover']


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id']


class AnnounceRequestSerializerDetailed(ModelSerializer):
    announce = AnnounceSerializerList(many=False)
    student = UserSerializerProfile(many=False)

    class Meta:
        model = AnnounceRequest
        fields = ['id', 'description', 'announce', 'student']


class AnnounceSerializerDetails(ModelSerializer):
    user = UserSerializerListItem(many=False)
    skills = SkillSerializer(many=True)
    requests = AnnounceRequestSerializer(many=True)

    class Meta:
        model = Announce
        fields = ['id', 'title', 'body', 'cover', 'date', 'user', 'skills']


class AnnounceRequestSerializerInsert(ModelSerializer):
    class Meta:
        model = AnnounceRequest
        fields = ['description', 'announce', 'student']


class CircleTypeSerializer(ModelSerializer):
    class Meta:
        model = CircleType
        fields = '__all__'


class CircleSerializer(ModelSerializer):
    type = CircleTypeSerializer(many=False)

    class Meta:
        model = Circle
        fields = '__all__'


class UserSerializerSelfProfessor(ModelSerializer):
    location = LocationSerializer(many=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'family', 'id_code', 'email', 'token', 'avatar',
                  'phone', 'bio', 'location']
