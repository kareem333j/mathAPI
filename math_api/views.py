from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import *
from users.models import Profile, NewUser
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse
from django.conf import settings
from blog.models import *
import json
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from django.db.models import Q, Value
from django.db.models.functions import Concat
from datetime import datetime
from decimal import Decimal
from .utils import send_notification_for_subscribers,send_notification_sessions_for_subscribers,send_activation_message, front_url,send_notification_for_added_course

# custom token override
from rest_framework_simplejwt.views import TokenObtainPairView


# #################################
# tokens view
class MyTokenObtainPairSerializerView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# #################################
# custom permissions
class UserProfileCustomPermissions(BasePermission):
    message = "user that owner of this account can access this only.!"

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser or request.user.is_staff
    
class UserCustomPermissions(BasePermission):
    message = "user that owner of this account can access this only.!"

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.user == request.user or request.user.is_superuser or request.user.is_staff
        else:
            return False

class UserIsAuthenticated(BasePermission):
    message = "Authentication needed"

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return True
        return False

class AdminAndStaffCustomPermissions(BasePermission):
    message = "لا تمتلك صلاحية الوصول الي هذه البيانات"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.is_staff
        else:
            return False
        
class AdminAndStaffCustomExtraPermissions(BasePermission):
    message = "لا تمتلك صلاحية الوصول الي هذه البيانات"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser or (request.user.is_staff and request.user.Profile.extra_permissions)
        else:
            return False
        
class AdminPermissions(BasePermission):
    message = "لا تمتلك صلاحية الوصول الي هذه البيانات"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser
        else:
            return False

class SubLecturePermissions(BasePermission):
    message = "لا يمكن الوصول الي محتوي الكورس إلا عند الدفع...!"

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated:
            course = get_object_or_404(Course, pk=view.kwargs["pk"])
            user_course = UserCourse.objects.filter(course=course, user=user).first()
            if user_course is not None:
                if request.user.is_superuser or request.user.is_staff or request.user.Profile.is_vip:
                    return True
                return user_course.is_active
            return (
                request.user.is_superuser or request.user.is_staff or course.price == 0 or request.user.Profile.is_vip
            )

class QuizPermission(BasePermission):
    message = "لقد ساهمت بالرد علي هذا النموذج من قبل"

    def has_permission(self, request, view):
        quiz_id = view.kwargs["pk"]
        user = request.user
        if user.is_authenticated:
            quiz = get_object_or_404(SubLectureQuiz, id=quiz_id)

            try:
                quiz_result = QuizResult.objects.get(user=user, quiz=quiz)
                if quiz_result:
                    if quiz_result.done == False:
                        return True
                    else:
                        return False
            except:
                return True

            return True
        else:
            return False

class QuizResultPermissions(BasePermission):
    message = "لم يتم الإعلان عن النتيحة بعد..."
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.is_authenticated:
            if obj.see_results == True:
                return True
        
    

# #############################################
# userdata
class UserProfile(generics.RetrieveAPIView):
    permission_classes = [UserProfileCustomPermissions]
    serializer_class = UserProfileSerializer
    queryset = NewUser

class AllDataProfile(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserProfileAllDataSerializer
    queryset = NewUser


# grades
class GradesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GradesSerializer
    queryset = Grade.objects.all()


# course API
class CoursesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer
    queryset = Course.active_objects.all()

class CoursesFilterWithGradeView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer

    def get_queryset(self):
        item = self.kwargs["pk"]
        try:
            grade_id = int(item)
            grade = Grade.objects.get(id=grade_id)
            courses = Course.active_objects.filter(grade=grade)
        except:
            courses = Course.active_objects.filter(grade__name=item)

        return courses
    
class GetGradeInfo(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = GradesSerializer
    queryset = Grade.objects.all()

class RetrieveCourseAllFields(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializerWithExtraFields
    queryset = Course.active_objects.all()

class LecturesView(generics.ListAPIView):
    permission_classes = [SubLecturePermissions]
    serializer_class = LectureSerializer

    def get_queryset(self):
        course_id = self.kwargs.get("pk")
        course = get_object_or_404(Course, id=course_id)
        Lectures = course.CourseLecture.filter(active=True)
        return Lectures

class SessionDone(generics.UpdateAPIView):
    permission_classes = [UserIsAuthenticated]

    def post(self, request):
        data = request.data
        type = data["type"]
        result = data["result"]
        session_id = data["id"]
        user_id = data["user"]
        course_id = data["course"]
        done = False

        user = get_object_or_404(NewUser, id=user_id)
        course = get_object_or_404(Course, id=int(course_id))
        # userCourse = get_object_or_404(UserCourse ,user=user, course=course, is_active=True)

        quiz, create = UserCourseProgress.objects.get_or_create(
            user=user, user_course=course, type=type, session_id=session_id
        )

        if quiz:
            quiz.done = result
            quiz.save()
            done = True

        if done:
            return Response(status=status.HTTP_201_CREATED)

        return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)

class getSessionsProgress(generics.ListAPIView):
    permission_classes = [UserIsAuthenticated]
    serializer_class = getSessionsProgressSerializer

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs["pk"]
        course = get_object_or_404(Course, pk=course_id)

        userCourseProgress = UserCourseProgress.objects.filter(
            user=user, user_course=course
        )

        return userCourseProgress


class GetVideoLikes(generics.RetrieveAPIView):
    permission_classes = [UserIsAuthenticated]
    serializer_class = VideoLikesSerializer

    def get_object(self):
        user = self.request.user
        video_id = self.kwargs["pk"]

        video = get_object_or_404(SubLectureVideo, id=video_id)
        try:
            video_like = VideoLikes.objects.get(user=user, video=video)
            return video_like
        except:
            video_like = VideoLikes.objects.create(user=user, video=video, like=False)
            return video_like

class UpdateVideoLikes(generics.RetrieveUpdateAPIView):
    permission_classes = [UserIsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        video_id = data["id"]
        updated_likes = data["like"]

        video = get_object_or_404(SubLectureVideo, id=video_id)

        if video:
            try:
                user_like = VideoLikes.objects.get(user=user, video=video)
                if updated_likes == True:
                    user_like.like = True
                    user_like.save()
                    video.likes = video.likes + 1
                    video.save()
                else:
                    user_like.like = False
                    user_like.save()
                    if video.likes > 0:
                        video.likes = video.likes - 1
                        video.save()
            except:
                if updated_likes == True:
                    user_like = VideoLikes.objects.create(
                        user=user, video=video, like=True
                    )
                    video.likes = video.likes + 1
                    video.save()
                else:
                    user_like = VideoLikes.objects.create(
                        user=user, video=video, like=False
                    )
                    if video.likes > 0:
                        video.likes = video.likes - 1
                        video.save()

            return Response({"likes": video.likes}, status=status.HTTP_201_CREATED)

        return Response(video.errors, status=status.HTTP_400_BAD_REQUEST)

# Quiz
class QuizView(generics.RetrieveAPIView):
    permission_classes = [QuizPermission]
    serializer_class = QuizSerializer
    queryset = SubLectureQuiz

class QuizViewRevision(generics.RetrieveAPIView):
    permission_classes = [QuizResultPermissions]
    serializer_class = QuizSerializerRevision
    queryset = SubLectureQuiz

class PaymentProcessOne(generics.CreateAPIView):
    permission_classes = [UserIsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        course = get_object_or_404(Course, pk=int(data["course"]))

        user_course, create = UserCourse.objects.get_or_create(
            user=user,
            course=course,
            price= "{:.2f}".format(Decimal(data['price'])),
            course_price= course.price,
            phone=data["phone"],
            transaction=data["transaction_number"],
        )

        if user_course:
            return Response(user_course.transaction, status=status.HTTP_201_CREATED)

        return Response(user_course.errors, status=status.HTTP_400_BAD_REQUEST)

class getTransactionNumber(generics.RetrieveAPIView):
    permission_classes = [UserIsAuthenticated]
    serializer_class = getTransactionNumberSerializer
    queryset = UserCourse

    def get_object(self):
        course_id = self.kwargs["pk"]
        user = self.request.user
        course = get_object_or_404(Course, pk=course_id)

        userCourse = get_object_or_404(UserCourse, user=user, course=course)

        return userCourse
    
class DeleteTransaction(generics.DestroyAPIView):
    permission_classes = [UserIsAuthenticated]
    queryset = UserCourse
    
    def destroy(self, request, *args, **kwargs):
        print('self: ',self, '\n')
        print('request: ',request, '\n')
        print('args: ', args, '\n')
        print('kwargs: ',kwargs, '\n')
        user = self.request.user
        try:
            course = get_object_or_404(Course, pk=kwargs['course_id'])
            instance = get_object_or_404(UserCourse, user=user, course=course)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    

class sendQuizResults(generics.CreateAPIView):
    permission_classes = [UserIsAuthenticated]

    def post(self, request):
        degree = 0
        user_answers = []
        data = request.data
        quiz = get_object_or_404(SubLectureQuiz, id=data["quiz"])
        questions_number = quiz.question.all().count()
        quiz_questions = quiz.question.all().values()
        user = request.user
        counter = -1

        for question in quiz_questions:
            if len(data["results"]) != 0:
                counter = -1
                for key, value in data["results"].items():
                    counter = counter + 1
                    if int(question["id"]) == int(key):
                        question_value = value
                        check_answer = False

                        try:
                            check_choice = QuizChoice.objects.get(id=question_value)
                            if check_choice.is_true == True:
                                check_answer = True
                        except:
                            check_answer = False

                        user_answers.append({"value": value, "is_true": check_answer})

                        try:
                            choice = QuizChoice.objects.get(id=question_value)
                            if choice.is_true:
                                degree = degree + 1
                        except:
                            choice = 0

                        break
                    else:
                        if len(data["results"]) == counter + 1:
                            user_answers.append({"value": 0, "is_true": False})
                            break
            else:
                user_answers.append({"value": 0, "is_true": False})

        try:
            result = QuizResult.objects.get(user=user, quiz=quiz)
            result.number_of_questions = questions_number
            result.answers = user_answers
            result.degree = degree
            result.done = True
            result.start = False
            result.timer = data["timer"]
            result.save()
        except:
            if QuizResult.objects.filter(user=user, quiz=quiz).count() == 0:
                result = QuizResult.objects.create(
                    user=user,
                    quiz=quiz,
                    number_of_questions=questions_number,
                    answers=user_answers,
                    timer=data["timer"],
                    degree=degree,
                    done=True,
                    start=False,
                )

        if result:
            return Response(status=status.HTTP_201_CREATED)

        return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)

class GetQuizResults(generics.RetrieveAPIView):
    permission_classes = [QuizResultPermissions]
    serializer_class = QuizResultsSerializer

    def get_object(self):
        quiz_id = self.kwargs["pk"]
        quiz = get_object_or_404(SubLectureQuiz, id=quiz_id)
        user = self.request.user
        quiz_result_obj = get_object_or_404(QuizResult, quiz=quiz, user=user)

        return quiz_result_obj

class GetQuizTimer(generics.RetrieveAPIView):
    permission_classes = [UserIsAuthenticated]
    serializer_class = QuizTimerSerializer

    def get_object(self):
        quiz_id = self.kwargs["pk"]
        quiz = get_object_or_404(SubLectureQuiz, id=quiz_id)
        user = self.request.user
        quiz_result_obj = get_object_or_404(QuizResult, quiz=quiz, user=user)

        return quiz_result_obj

class QuizTimer(generics.CreateAPIView):
    permission_classes = [UserIsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        quiz_id = data["quiz"]
        quiz = get_object_or_404(SubLectureQuiz, id=quiz_id)
        try:
            quiz_result = QuizResult.objects.get(user=user, quiz=quiz)
            quiz_result.timer = data["timer"]
            quiz_result.start = data["start"]
            quiz_result.save()
        except:
            QuizResult.objects.create(
                user=user, quiz=quiz, timer=data["timer"], start=data["start"]
            )

        return Response(status=status.HTTP_201_CREATED)

    
# notifications
class UnreadNotifications(generics.RetrieveAPIView):
    permission_classes = [UserProfileCustomPermissions]
    serializer_class = GetNotificationsUnReadCountSerializer
    queryset = NewUser
    
class RetrieveUserNotifications(generics.ListAPIView):
    permission_classes = [UserCustomPermissions]
    serializer_class = NotificationsSerializer
    
    def get_queryset(self):
        user = self.request.user
        notifications = UserNotificationInfo.objects.filter(user=user).order_by('-created_dt')
        return notifications
    
class RetrieveAndSeenNotification(generics.RetrieveUpdateAPIView):
    permission_classes = [UserCustomPermissions]
    serializer_class = NotificationsSerializer
    queryset = UserNotificationInfo.objects.all()
    
class RemoveUserNotifications(generics.ListAPIView):
    permission_classes = [UserCustomPermissions]
    serializer_class = NotificationsSerializer
    
    def get_queryset(self):
        user = self.request.user
        notifications = UserNotificationInfo.objects.filter(user=user)
        for notification in notifications:
            notification.delete()
        
        return []
    
class RemoveNotification(generics.DestroyAPIView):
    permission_classes = [UserCustomPermissions]
    serializer_class = NotificationsSerializer
    queryset = UserNotificationInfo.objects.all()

# course API for staff
class CoursesViewManager(generics.ListCreateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = GradeWithCoursesSerializer
    queryset = Grade.objects.all()

class SearchCoursesView(generics.ListAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = CourseSerializer
    # queryset = Course.objects.all()

    def get_queryset(self):
        item = self.kwargs["search_item"]
        # try:
        if item == "null":
            queryset = Course.objects.all()
        else:
            queryset = Course.objects.filter(
                Q(title__contains=item)
                | Q(description__contains=item)
                | Q(grade__name__contains=item)
                | Q(upload_date__contains=item)
                | Q(price__contains=item)
                | Q(price_off__contains=item)
            )

        return queryset

class GetCourseViewManager(generics.RetrieveAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = CourseSerializer
    queryset = Course

class AddCourse(generics.CreateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = AddCourseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            grade_id = request.data['grade']
            course_title = request.data['title']
            grade = get_object_or_404(Grade, pk=int(grade_id))
            send_notification_for_added_course(course_title, grade)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditCourse(generics.UpdateAPIView):
    permission_classes = [AdminAndStaffCustomExtraPermissions]
    queryset = Course.objects.all()
    # serializer_class = AddCourseSerializer
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, format=None, pk=None):
        data = request.data
        course = get_object_or_404(Course, pk=pk)
        serializer = AddCourseSerializer(data=data)
        if serializer.is_valid():
            active, new = False, False
            grade = get_object_or_404(Grade, pk=int(data["grade"]))
            course.title = data["title"]
            course.description = data["description"]
            course.grade = grade
            course.price_off = data["price_off"]
            course.price = data["price"]

            if data["is_active"] == "true":
                active = True
            else:
                active = False

            if data["new"] == "true":
                new = True
            else:
                new = False

            course.is_active = active
            course.new = new

            if data["image"] == "":
                print(None)
            else:
                course.image = data["image"]
            # course.image = data['image']
            course.update_date = datetime.now()
            course.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteCourse(generics.DestroyAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

class GetProfiles(generics.ListAPIView):
    permission_classes = [AdminPermissions]
    serializer_class = ProfileSerializerForAdmin
    queryset = Profile.objects.filter(is_private=False)

class DeleteUser(generics.DestroyAPIView):
    permission_classes = [AdminPermissions]
    serializer_class = UserProfileSerializer
    queryset = NewUser.objects.all()

class SearchProfile(generics.ListAPIView):
    permission_classes = [AdminPermissions]
    serializer_class = ProfileSerializerForAdmin

    def get_queryset(self):
        item = self.kwargs["search_item"]

        if item == "null":
            queryset = Profile.objects.filter(is_private=False)
        else:
            queryset = Profile.objects.annotate(
                full_name=Concat("user__first_name", Value(" "), "user__last_name")
            ).filter(
                Q(full_name__contains=item)
                | Q(state__contains=item)
                | Q(gender__contains=item)
                | Q(grade__contains=item)
                | Q(parent_phone__contains=item)
                | Q(user__phone__contains=item)
                | Q(user__email__contains=item)
            )

        return queryset

class UsersBasicInfoList(generics.ListAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = UsersBasicInfoSerializer
    queryset = NewUser.objects.filter(is_superuser=False)
    # queryset = NewUser.objects.all()

# payments for admin
class PaymentsList(generics.ListAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = PaymentSerializer
    queryset = UserCourse.objects.all()

class SearchPayments(generics.ListAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        item = self.kwargs["search_item"]

        if item == "null":
            queryset = UserCourse.objects.all()
        else:
            queryset = UserCourse.objects.filter(transaction__contains=item)

        return queryset

class ActivePayment(generics.UpdateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    queryset = UserCourse.objects.all()
    
    def put(self, request, **kwargs):
        transaction = kwargs['transaction_num']
        user_request = get_object_or_404(UserCourse, transaction=transaction)
        
        if user_request:
            if user_request.is_active == True:
                user_request.is_active = False
            else:
                user_request.is_active = True
                
            user_request.save()
            send_activation_message(user_request.user,user_request.course, user_request.is_active)
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_404_NOT_FOUND)

# course info -> edit
class RetrieveCourseAllFieldsAdmin(generics.RetrieveAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = CourseSerializerWithExtraFieldsAdmin
    queryset = Course.objects.all()

class GetLecture(generics.RetrieveAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = CreateLectureSerializer
    queryset = Lecture.objects.all()

                            
class AddLecture(generics.CreateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    
    def post(self, request, *args, **kwargs):
        data = request.data
        data['course'] = kwargs['pk']
        notification = data['notification']
        serializer = CreateLectureSerializer(data=data)
        if serializer.is_valid():
            course = get_object_or_404(Course, pk=data['course'])
            course.update_date = datetime.now()
            serializer.save()
            
            send_notification_for_subscribers(
                course=course,
                notification=notification,
                title='جديد 🆕',
                context=f'''
                     لكل المشتركين في كورس "<span style="color:var(--text-cyan-500)">{course.title}</span>"
                    تم إضافة محاضرة جديدة في الكورس
                    يمكنك الأن مشاهدتها
                    .
                    .
                    تابع المحاضرة من خلال الرابط التالي
                    .
                    > <a href="{front_url}/courses/{course.grade.id}/course/{course.id}">{front_url}/courses/{course.grade.id}/course/{course.id}</a>
                    .
                    بالتوفيق ياصديقي❤️
                    .
                    .
                    مع تحيات : الدعم الفني
                '''
            )
                
                            
            return Response(data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)  

class UpdateLecture(generics.UpdateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = CreateLectureSerializer
    queryset = Lecture.objects.all()

class GetSession(generics.RetrieveAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    
    def get_object(self):
        id = self.kwargs['pk']
        type = self.kwargs['type']
        if type == "document":
            self.serializer_class = CreateSessionDocumentSerializer
            object = get_object_or_404(SubLectureDocument, id=id)
        elif type == "video":
            object = get_object_or_404(SubLectureVideo, id=id)
            self.serializer_class = CreateSessionVideoSerializer
        elif type == "quiz":
            object = get_object_or_404(SubLectureQuiz, id=id)
            self.serializer_class = GetSessionQuizSerializer
        else:
            object = None
        
        return object
            
class AddSession(generics.CreateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    parser_classes = [MultiPartParser,FileUploadParser, FormParser]

    def post(self, request, format=None):
        data = request.data
        lecture = get_object_or_404(Lecture, pk=int(data['lecture']))
        course = lecture.course
        if data['type'] == 'document':
            serializer = CreateSessionDocumentSerializer(data=data)

            if serializer.is_valid():
                course.update_date = datetime.now()
                course.save()
                serializer.save()
                send_notification_sessions_for_subscribers(course, data['notification'], lecture, data['title'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif data['type'] == 'video':
            serializer = CreateSessionVideoSerializer(data=data)

            if serializer.is_valid():
                course.update_date = datetime.now()
                course.save()
                serializer.save()
                send_notification_sessions_for_subscribers(course, data['notification'], lecture, data['title'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif data['type'] == 'quiz':
            quiz_serializer = CreateSessionQuizSerializer(data=data)
            if quiz_serializer.is_valid():
                course.update_date = datetime.now()
                course.save()
                new_quiz = quiz_serializer.save()
                if new_quiz:
                    questions_list = json.loads(data['quiz'])
                    for question in questions_list:
                        q_id = question['id']
                        q_image = None if data[f'question_{q_id}_image'] == 'null' else data[f'question_{q_id}_image']
                        question_data = {'title': question['title'], 'image': q_image, 'quiz':new_quiz.pk}
                        quiz_question_serializer = CreateQuizQuestionSerializer(
                            data=question_data
                        )
                        if quiz_question_serializer.is_valid():
                            new_question = quiz_question_serializer.save()
                            if new_question:
                                choices_list = question['choices']
                                for choice in choices_list:
                                    ch_id = choice['id']
                                    ch_image = None if data[f'question_{q_id}_choice_{ch_id}_image'] == 'null' else data[f'question_{q_id}_choice_{ch_id}_image']
                                    
                                    choice_data = {'choice': choice['title'], 'image': ch_image,'question':new_question.pk,'is_true':choice['is_true']}
                                    question_choice_serializer = CreateQuestionChoiceSerializer(
                                        data=choice_data
                                    )
                                    if question_choice_serializer.is_valid():
                                        question_choice_serializer.save()
                        else:
                            return Response(quiz_question_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                send_notification_sessions_for_subscribers(course, data['notification'], lecture, data['title'])
                return Response(status=status.HTTP_201_CREATED)
            
class DeleteLecture(generics.DestroyAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    queryset = Lecture.objects.all()
    
class DeleteSession(generics.DestroyAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    
    def get_queryset(self):
        type = self.kwargs['type']
        id = self.kwargs['pk']
        if type == 'document':
            queryset = SubLectureDocument.objects.filter(id=id)
        elif type == 'video':
            queryset = SubLectureVideo.objects.filter(id=id)
        elif type == 'quiz':
            queryset = SubLectureQuiz.objects.filter(id=id)
        else:
           raise ValueError("session not found -_-")
        
        return queryset
    
class UpdateSession(generics.UpdateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    parser_classes = [MultiPartParser,FileUploadParser, FormParser]
    
    def put(self, request,format=None, **kwargs):
        data = request.data
        type = request.data['type']
        lecture = get_object_or_404(Lecture, id=data['lecture'])
        course = lecture.course
        
        if type == 'document':
            document = get_object_or_404(SubLectureDocument, id=kwargs['pk'])
            if data["document"] != "":
                document.document = data['document']
            document.title = data['title']
            document.description = data['description']
            document.lecture = lecture
            document.priority = data['priority']
            if data['active'] == 'true':
                document.active = True
            else:
                document.active = False
                
            document.save()
            course.update_date = datetime.now()
            course.save()
            return Response(status=status.HTTP_200_OK)
            
        elif type == 'video':
            serializer = CreateSessionVideoSerializer(data=data)
            if serializer.is_valid():
                video = get_object_or_404(SubLectureVideo, id=kwargs['pk'])
                video.video_embed = data['video_embed']
                video.title = data['title']
                video.description = data['description']
                video.lecture = lecture
                video.priority = data['priority']
                if data['active'] == 'true':
                    video.active = True
                else:
                    video.active = False
                video.save()
                course.update_date = datetime.now()
                course.save()
                return Response(status=status.HTTP_200_OK)
        
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        elif type == 'quiz':
            serializer = CreateSessionQuizSerializer(data=data)
            if serializer.is_valid():
                quiz = get_object_or_404(SubLectureQuiz, id=kwargs['pk'])
                quiz.title = data['title']
                quiz.description = data['description']
                quiz.lecture = lecture
                quiz.priority = data['priority']
                quiz.time = data['time']
                quiz.points = data['points']
                if data["notes"] != "":
                    quiz.notes = data['notes']
                if data['active'] == 'true':
                    quiz.active = True
                else:
                    quiz.active = False
                if data['see_results'] == 'true':
                    quiz.see_results = True
                else:
                    quiz.see_results = False
                quiz.save()
                course.update_date = datetime.now()
                course.save()
                
                # removed questions => O(n^2) => complexity -_-
                for i in json.loads(data['removed']):
                    quiz_questions = QuizQuestion.objects.all()
                    for q in quiz_questions:
                        if q.id == i:
                            q.delete()
                
                if quiz:
                    questions_list = json.loads(data['quiz'])
                    for question in questions_list:
                        q_id = question['id']
                        # q = get_object_or_404(QuizQuestion, id=q_id)
                        q, create_q = QuizQuestion.objects.get_or_create(id=q_id, quiz=quiz)
                        
                        if data[f'question_{q_id}_image'] != 'undefined' and data[f'question_{q_id}_image'] != 'null':
                            q.image = data[f'question_{q_id}_image']
                        q.title = question['title']
                        q.quiz = quiz
                        q.save()
                        
                        if q:
                            choices_list = question['choices']
                            for choice in choices_list:
                                ch_id = choice['id']
                                # ch = get_object_or_404(QuizChoice, id=ch_id)
                                ch, create_ch = QuizChoice.objects.get_or_create(id=ch_id, question=q)
                                if data[f'question_{q_id}_choice_{ch_id}_image'] != 'undefined' and data[f'question_{q_id}_choice_{ch_id}_image'] != 'null':
                                    ch.image = data[f'question_{q_id}_choice_{ch_id}_image']
                                ch.choice = choice['choice']
                                ch.is_true = choice['is_true']
                                ch.question = q
                                ch.save()
                        else:
                            return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
class GivePermissions(generics.UpdateAPIView):
    permission_classes = [AdminPermissions]
    
    def put(self, request, **kwargs):
        data = request.data
        user = get_object_or_404(NewUser, pk = kwargs['pk'])
        profile = get_object_or_404(Profile, user = user)
        
        profile.is_vip = data['is_vip']
        user.is_superuser = data['is_superuser']
        user.is_staff = data['is_staff']
        profile.save()
        user.save()
        
        if profile and user:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# notifications for staff
class NotificationsList(generics.ListAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = NotificationsSerializerForStaff
    
    def get_queryset(self):
        user = self.request.user
        counter = 0
        notifications_list = []
        notifications = Notification.objects.all().order_by('-created_dt')
        for notification in notifications:
            if notification.from_user != None:
                if notification.from_user.Profile.is_private == False or (notification.from_user.Profile.is_private == True and notification.from_user == user):
                    notifications_list.append(notification)
                    if user.is_superuser == False:
                        if notifications_list[counter].from_user.is_superuser:
                            notifications_list[counter].title = 'إشعار مشفر (مسؤل)'
                            notifications_list[counter].context = '###########'
                
            counter+=1
                
        return notifications_list
    
class AddNotification(generics.CreateAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    
    def post(self, request):
        data = request.data
        from_user = request.user
        try:
            to_user = get_object_or_404(NewUser, id=int(data['to']))
        except:
            to_user = None
        title = data['title']
        context = data['context']
        
        notification = Notification.objects.create(
            to_user=to_user,
            from_user=from_user,
            title=title,
            context=context
        )
        
        if to_user == None:
            students = NewUser.objects.filter(is_staff=False, is_superuser=False)
            if notification:
                for student in students:
                    UserNotificationInfo.objects.create(
                        notification=notification,
                        user=student
                    )
                return Response(status=status.HTTP_201_CREATED)
        else:
            if notification:
                UserNotificationInfo.objects.create(
                    notification=notification,
                    user=to_user
                )
                return Response(status=status.HTTP_201_CREATED)
        
        notification.delete()
        Response(status=status.HTTP_400_BAD_REQUEST)

class RetrieveUpdateNotification(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = BasicNotificationSerializer
    queryset = Notification.objects.all()

class DeleteNotification(generics.DestroyAPIView):
    permission_classes = [AdminAndStaffCustomPermissions] 
    queryset = Notification.objects.all()


# Quiz Subscribers
class QuizSubscribersList(generics.ListAPIView):
    permission_classes = [AdminAndStaffCustomPermissions]
    serializer_class = QuizSubscribersSerializer
    
    def get_queryset(self):
        quiz = get_object_or_404(SubLectureQuiz, id=self.kwargs['pk'])
        subscribers = QuizResult.objects.filter(quiz=quiz).order_by('timer').order_by('-degree').order_by('-done')
        
        return subscribers
    