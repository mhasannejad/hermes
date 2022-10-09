import time
from django.db import models
from accounts.models import *
from django.conf import settings


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class ProfessorGroup(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    description = models.TextField(max_length=1500, null=True, default=None)

    def __str__(self):
        return self.name


class Expertise(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    description = models.TextField(max_length=1500, null=True, default=None)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    icon = ThumbnailerImageField(upload_to='icons', null=True)

    def __str__(self):
        return f'{self.id}  |  {self.name}'


class CircleType(models.Model):
    name = models.CharField(max_length=100, null=True)
    icon = ThumbnailerImageField(upload_to='icons', null=True)
    description = models.TextField(max_length=500, null=True)


class Circle(models.Model):
    name = models.CharField(max_length=100, null=True)
    logo = ThumbnailerImageField(upload_to='logos', null=True)
    description = models.TextField(max_length=500, null=True)
    type = models.ForeignKey(CircleType, on_delete=models.SET_NULL, null=True)


class User(AbstractBaseUser):
    name = models.CharField(max_length=100, null=True)
    family = models.CharField(max_length=100, null=True)
    id_code = models.CharField(max_length=100, null=True)
    stud_code = models.CharField(max_length=100, null=True)
    entrance_date = models.IntegerField(null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    expertise = models.ForeignKey(Expertise, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(ProfessorGroup, on_delete=models.SET_NULL, null=True)
    avatar = ThumbnailerImageField(upload_to='avatars/', default=None, null=True)
    phone = models.CharField(max_length=100, null=True)
    bio = models.CharField(max_length=500, null=True)
    # announcerequests = models.ForeignKey('AnnounceRequest', on_delete=models.CASCADE,null=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True,

    )
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser

    MODES = (
        (0, 'supervisor'),
        (1, 'student'),
        (2, 'professor'),
    )
    mode = models.IntegerField(choices=MODES, default=1)

    circles = models.ManyToManyField(Circle, blank=True)

    # notice the absence of a "Password field", that is built in.
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    @property
    def references(self):
        return self.reference_set.order_by('-id')

    @property
    def token(self):
        return Token.objects.get(user=self).key

    @property
    def posts(self):
        return self.post_set.all()

    @property
    def announces(self):
        return self.announce_set.all()

    @property
    def contacts(self):
        return self.contact_set.all()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if Token.objects.filter(user=self).count() == 0:
            print('token created ')
            Token.objects.create(user=self)

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return str(self.name)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def official_name(self):
        if self.mode==2:
            return 'dr. ' + self.name +' '+ self.family
        else:
            return ''

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin


class Post(models.Model):
    title = models.CharField(max_length=100, null=True, default=None)
    body = models.TextField(max_length=2500, null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.IntegerField(null=True)
    cover = ThumbnailerImageField(upload_to='covers', null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # self.date = round(time.time()*1000)

    @property
    def images(self):
        return self.postimage_set.all()


class PostImage(models.Model):
    file = models.FileField(upload_to='posts/files/', null=True)
    name = models.CharField(max_length=100, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)


class Appointment(models.Model):
    title = models.CharField(max_length=100, null=True, default=None)
    description = models.CharField(max_length=500, null=True, default=None)
    time = models.IntegerField(null=True, default=None)  # millis
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='student')
    professor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='professor')
    done = models.BooleanField(default=False)
    STATES = (
        (0, 'sent'),
        (1, 'confirmed'),
        (2, 'rejected'),
    )
    state = models.IntegerField(null=True, choices=STATES, default=0)


class ContactType(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    icon = models.ImageField(upload_to='icons/contacttypes/', null=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    value = models.CharField(max_length=500, null=True, default=None)
    type = models.ForeignKey(ContactType, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.type} | {self.value}'


class Setting(models.Model):
    NAMES = (
        (settings.MAIN_PAGE_PROFS_DISPLAY_LOCATION, 'select which location to be displayed in app main page'),
    )
    key = models.IntegerField(null=True, unique=True, choices=NAMES)
    value = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'{self.NAMES[self.key][1]}  |  {self.value}'


class Reference(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    description = models.TextField(max_length=500, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to='references', null=True)
    cover = ThumbnailerImageField(upload_to='covers', null=True)


class Skill(models.Model):
    name = models.CharField(max_length=100, null=True, default=None)
    description = models.TextField(max_length=500, null=True)


class Announce(models.Model):
    title = models.CharField(max_length=100, null=True, default=None)
    body = models.TextField(max_length=2500, null=True, )
    cover = models.ImageField(upload_to='announce/covers/', null=True)
    date = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    skills = models.ManyToManyField(Skill)

    @property
    def requests(self):
        return self.announcerequest_set.all()


class AnnounceRequest(models.Model):
    description = models.TextField(max_length=100, null=True, )
    announce = models.ForeignKey(Announce, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
