from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from .models import NewUser, Profile
from .serializers import RegisterSerializer
from blog.models import Notification, UserNotificationInfo, Grade
from math_api.utils import front_url


class UserProfileCustomPermissions(BasePermission):
    message = "user that owner of this profile can access this profile"
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_superuser
    
def get_grade_link(data):
    grade = Grade.objects.filter(name=data)
    value = ''''''
    if len(grade) > 0:
        value = f'''
            .
            .
            وبما انك في الصف {data}
            تقدر تتابع جميع كورسات {data}
            من خلال الرابط التالي :
            > <a href="{front_url}/courses/{grade[0].id}">{front_url}/courses/{grade[0].id}</a>
        '''
        return value
    else:
        return value
    
class CustomUserCreate(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        data = request.data
        reg_serializer = RegisterSerializer(data=data)
        if reg_serializer.is_valid():
            newuser = reg_serializer.save()
            if newuser:
                profile = get_object_or_404(Profile, user__phone = data['phone'])
                if profile:
                    profile.parent_phone = data['profile']['parent_phone']
                    profile.state = data['profile']['state']
                    profile.gender = data['profile']['gender']
                    profile.grade = data['profile']['grade']
                    profile.save()
                    welcome_notification = Notification.objects.create(
                        to_user=profile.user,
                        title='تهانينا 🎉',
                        context=f'''
                            لقد تم إنشاء حسابك علي المنصة بنجاح 🥳
                            يمكنك الأن تصفح المنصة بكل سهولة والتعلم بكل سهولة
                            بدون تضييع وقت وفلوس ومجهود في السنتر 🥱
                            تقدر من خلال منصتنا تتعلم جميع الدروس ومتابعة كل ماهو جديد
                            وفي كمان امتحانات مستمرة وجوائز لكل المتفوقين
                            هنشجعك تذاكر بكل سهولة وبدون اي حجه 😜
                            كمان بننزل خصومات كبيرة علي الكورسات كل فترة 💸
                            {get_grade_link(profile.grade)}
                            .
                            .
                            بالتوفيق ياصديقي ❤️
                            .
                            مع تحيات : فريق الدعم الفني                          
                        '''
                    )
                    if welcome_notification:
                        UserNotificationInfo.objects.create(
                            notification = welcome_notification,
                            user = profile.user
                        )
                    
                    
                    
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    newuser.delete()
                return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
    
class BlacklistTokenUpdateView(APIView):
    permission_classes= [AllowAny]
    authentication_classes = ()
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)