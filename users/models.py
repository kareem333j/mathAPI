from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save

class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, phone,first_name, last_name, password, **other_fields):
        other_fields.setdefault('is_superuser',True)
        other_fields.setdefault('is_staff',True)
        
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')
        
        
        return self.create_user(email, phone,first_name, last_name, password, **other_fields)
    
    def create_user(self, email, phone,first_name, last_name, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        if not phone:
            raise ValueError(_('You must provide an phone number'))
        
        email = self.normalize_email(email)
        user = self.model(email=email,phone=phone, first_name=first_name, last_name=last_name,**other_fields)
        user.set_password(password)
        user.save()
        
        return user

class NewUser(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(_('email'), max_length=150, unique=True)
    phone = models.CharField(_('phone number'),
        max_length=11,
        unique=True
    )
    # username = models.CharField(_('username'),max_length=150, unique=True)
    first_name = models.CharField(_('first_name'),max_length=150)
    last_name = models.CharField(_('last_name'),max_length=150)
    start_date = models.DateField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = CustomAccountManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email','first_name','last_name']
    
    def profile(self):
        profile = Profile.objects.get(user=self)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Profile(models.Model):
    class PublicProfiles(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_private=False)
        
    gender_choices = (
        ("ذكر", "ذكر"),
        ("انثي", "انثي"),
    )
    state_choices = (
        ("الإسكندرية", "الإسكندرية"),
        ("الإسماعيلية", "الإسماعيلية"),
        ("كفر الشيخ", "كفر الشيخ"),
        ("أسوان", "أسوان"),
        ("أسيوط", "أسيوط"),
        ("الأقصر", "الأقصر"),
        ("الوادي الجديد", "الوادي الجديد"),
        ("شمال سيناء", "شمال سيناء"),
        ("البحيرة", "البحيرة"),
        ("بني سويف", "بني سويف"),
        ("بورسعيد", "بورسعيد"),
        ("البحر الأحمر", "البحر الأحمر"),
        ("الجيزة", "الجيزة"),
        ("الدقهلية", "الدقهلية"),
        ("جنوب سيناء", "جنوب سيناء"),
        ("دمياط", "دمياط"),
        ("سوهاج", "سوهاج"),
        ("السويس", "السويس"),
        ("الشرقية", "الشرقية"),
        ("الغربية", "الغربية"),
        ("الفيوم", "الفيوم"),
        ("القاهرة", "القاهرة"),
        ("القليوبية", "القليوبية"),
        ("قنا", "قنا"),
        ("مطروح", "مطروح"),
        ("المنوفية", "المنوفية"),
        ("المنيا", "المنيا"),
    )
    grade_choices = (
        ('الصف الأول الثانوي','الصف الأول الثانوي'),
        ('الصف الثاني الثانوي','الصف الثاني الثانوي'),
        ('الصف الثالث الثانوي','الصف الثالث الثانوي')
    )
    user = models.OneToOneField(NewUser, on_delete=models.CASCADE, related_name='Profile')
    parent_phone = models.CharField(_('parent number'),max_length=11, unique=True)
    state = models.CharField(max_length=150, blank=True, choices=state_choices)
    gender = models.CharField(max_length=100, blank=True, choices=gender_choices)
    grade = models.CharField(max_length=100, blank=True, choices=grade_choices)
    is_private = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    extra_permissions = models.BooleanField(default=False)
    
    objects = models.Manager()
    public = PublicProfiles()
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.save()
        
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
    
post_save.connect(create_user_profile, sender=NewUser)
# post_save.connect(save_user_profile, sender=NewUser)