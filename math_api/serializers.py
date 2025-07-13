from rest_framework import serializers
from users.models import NewUser, Profile
from blog.models import *
import operator
import ast
from django.shortcuts import get_object_or_404


# custom token override
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id
        token['phone'] = user.phone
        # ...

        return token
# ##############################################

class ProfileSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        profile = Profile.objects.get(user=instance)
        subscribe_courses = UserCourse.objects.filter(user=instance).values('course','is_active')
        return {
            "id": profile.id,
            "parent_phone": profile.parent_phone,
            "state": profile.state,
            "gender": profile.gender,
            "grade": profile.grade,
            'subscribe_courses':subscribe_courses,
            'is_superuser': profile.user.is_superuser,
            'is_staff': profile.user.is_staff,
            'is_vip': profile.is_vip,
            'extra_permissions': profile.extra_permissions
        }


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source="*")
    notifications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NewUser
        fields = ("id", "phone", "first_name", "last_name", "profile", "email", "notifications_count")
        
    def get_notifications_count(self,obj):
        user = NewUser.objects.get(id=obj.id)
        user_notifications_count = UserNotificationInfo.objects.filter(user=user, seen=False).count()
            
        return user_notifications_count

class AllDataCourseSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        user_courses = UserCourse.objects.filter(user=instance, is_active=True)
        courses_list = []
        for course in user_courses:
            data_course = course.course
            lectures = data_course.CourseLecture.filter(active=True)
            course_sessions_count = 0
            progress = 0
            for lec in lectures:
                course_sessions_count += lec.LectureVideo.filter(active=True).count() + lec.LectureDocument.filter(active=True).count() + lec.LectureQuiz.filter(active=True).count()
                
            course_progress = UserCourseProgress.objects.filter(user=instance, user_course=data_course, done=True).count()
            if course_progress != 0:
                progress = (course_progress/course_sessions_count) * 100
            course_serializer = {
                'id': data_course.id,
                'title': data_course.title,
                'description': data_course.description,
                'grade': data_course.grade.name,
                'image': data_course.image.url,
                'sessions': course_sessions_count,
                'sessions_isDone': course_progress,
                'progress': progress
            }
            courses_list.append(course_serializer)
        return courses_list

class UserStatistics(serializers.BaseSerializer):
    def to_representation(self, instance):
        user_courses = UserCourse.objects.filter(user=instance)
        course_progress_count = 0
        total_courses_progress = 0
        course_sessions_count = 0
        user_quiz_results = QuizResult.objects.filter(user=instance, done=True)
        course_quizzes_count = QuizResult.objects.filter(user=instance).count()
        course_quizzes_ended_count = user_quiz_results.count()
        course_quizzes_ended_progress = 0
        course_quizzes_passed_count = 0
        course_quizzes_passed_progress = 0
        statistics_list = []

        for course in user_courses:
            data_course = course.course
            lectures = data_course.CourseLecture.filter(active=True)
            course_progress = UserCourseProgress.objects.filter(user=instance, user_course=data_course, done=True)
            course_progress_count += course_progress.count()
            for lec in lectures:
                course_sessions_count += lec.LectureVideo.filter(active=True).count() + lec.LectureDocument.filter(active=True).count() + lec.LectureQuiz.filter(active=True).count()
                    
        # total_courses_progress
        if course_sessions_count != 0:
            total_courses_progress = (course_progress_count/course_sessions_count)*100
        statistics_list.append({'title':'مستوي التقدم بالنسبة لإجمالي الكورسات المشترك فيها','value': total_courses_progress, 'count':None})
        
        # number of quizzes finished to all quizzes in my courses
        if course_quizzes_count != 0:
            course_quizzes_ended_progress = (course_quizzes_ended_count/course_quizzes_count)*100
        statistics_list.append({'title':'عدد الإختبارات الي بدأت فيها وخلصتها','value': course_quizzes_ended_progress, 'count':{'end':course_quizzes_ended_count, 'from':course_quizzes_count}})
        
        # number of quizzes finished and student is -> success
        for quiz_result in user_quiz_results:
            if int(quiz_result.degree) >= (quiz_result.number_of_questions/2):
                course_quizzes_passed_count += 1
        if course_quizzes_ended_count > 0:
            course_quizzes_passed_progress = (course_quizzes_passed_count/course_quizzes_ended_count)*100
        statistics_list.append({'title':'عدد الإختبارات الي نجحت فيها','value': course_quizzes_passed_progress, 'count':{'end':course_quizzes_passed_count, 'from':course_quizzes_ended_count}})
        
        
        return statistics_list

class UserInvoices(serializers.BaseSerializer):
    def to_representation(self, instance):
        invoices = UserCourse.objects.filter(user=instance)
        return invoices.values('transaction','course__title','course_price','is_active','request_dt','price')
        
        
class UserProfileAllDataSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source="*")
    courses = AllDataCourseSerializer(source="*")
    statistics = UserStatistics(source="*")
    invoices = UserInvoices(source="*")
    class Meta:
        model = NewUser
        fields = ("id", "phone","start_date","last_login", "first_name", "last_name", "email", "profile","courses","statistics", "invoices")


# course Serializers
# 1 - main course serializer
class getUser(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.get_count()
    
class GradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('id', 'name', 'description')
        
class CourseGradeInfo(serializers.BaseSerializer):
    def to_representation(self, instance):
        grade = get_object_or_404(Grade, pk=instance.grade.id)
        
        info = {
            'id': grade.id,
            'name': grade.name,
            'description': grade.description
        }
        return info
    
class CourseSerializer(serializers.ModelSerializer):
    grade_info = CourseGradeInfo(source="*")
    is_paid=serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ('id','title', 'description','image','grade_info', 'price', 'price_off','new', 'is_active','upload_date', 'update_date','is_paid')
    
    def get_is_paid(self,obj):
        user_subscribed = False
        
        try:
            user_id = self.context['request'].user.id
            user = NewUser.objects.get(id=user_id)
        except:
            user_subscribed = False
        try:
            user_course = UserCourse.objects.get(
                user=user,
                course=obj
            )
            if user_course:
                if user_course.is_active == True:
                    user_subscribed = True
        except:
            user_subscribed = False
            
        return user_subscribed

class CoursesSerializerMainData(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'price', 'price_off', 'is_active', 'new']
        
class GradeWithCoursesSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(source='Grade', many=True)

    class Meta:
        model = Grade
        fields = ['id', 'name', 'description', 'courses']

        
class CourseSerializerFields(serializers.BaseSerializer):
    def to_representation(self, instance):
        lectures = instance.CourseLecture.filter(active=True)
        course_list = []
        
        for lecture in lectures:
            # videos
            sub_lecture_videos = lecture.LectureVideo.filter(active=True).values('id', 'title','description', 'type','priority','done')
            
            # documents (pdf)
            sub_lecture_documents = lecture.LectureDocument.filter(active=True).values('id', 'title','description', 'type','priority','done')
            
            # quizzes
            sub_lecture_quizzes = lecture.LectureQuiz.filter(active=True).values('id', 'title','description', 'type','priority','done')
            
            # concat lists
            list = []
            list.extend(sub_lecture_videos)
            list.extend(sub_lecture_documents)
            list.extend(sub_lecture_quizzes)
            
            sub_lectures_list = sorted(list, key=operator.itemgetter('priority'))
            # course_list.__setitem__(lecture.title, sub_lectures_list)
            lecture_obj = {
                'id': lecture.id,
                'title': lecture.title,
                'description': lecture.description,
                'content': sub_lectures_list
            }
            course_list.append(lecture_obj)
        
        return course_list
        
class CourseSerializerWithExtraFields(serializers.ModelSerializer):
    grade_info = CourseGradeInfo(source="*")
    lectures = CourseSerializerFields(source="*")
    is_paid = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ('id','title', 'description','image','grade_info', 'price_off','price', 'is_active','new', 'lectures','upload_date', 'update_date', 'is_paid')
        
    def get_is_paid(self,obj):
        user_subscribed = False
        
        try:
            user_id = self.context['request'].user.id
            user = NewUser.objects.get(id=user_id)
        except:
            user_subscribed = False
        try:
            user_course = UserCourse.objects.get(
                user=user,
                course=obj
            )
            if user_course:
                if user_course.is_active == True:
                    user_subscribed = True
        except:
            user_subscribed = False
            
        return user_subscribed
        
# 2 - Lectures serializer
class LectureSerializerChildren(serializers.BaseSerializer):
    def to_representation(self, instance):   
        lec= Lecture.objects.get(pk=instance.id)   
        # videos
        sub_lecture_videos = instance.LectureVideo.filter(active=True).values()
        
        
        # documents (pdf)
        sub_lecture_documents = instance.LectureDocument.filter(active=True).values()
        
        # quizzes
        sub_lecture_quizzes = instance.LectureQuiz.filter(active=True).values()
        
        # concat lists
        list = []
        list.extend(sub_lecture_videos)
        list.extend(sub_lecture_documents)
        list.extend(sub_lecture_quizzes)
        
        sub_lectures_list = sorted(list, key=operator.itemgetter('priority'))
        
        # remove id from objects
        # for i in sub_lectures_list:
        #     del i['id']
        
        return sub_lectures_list
        
        
class LectureSerializer(serializers.ModelSerializer):
    content = LectureSerializerChildren(source="*")
    class Meta:
        model = Lecture
        fields = ('id', 'title', 'description','content','active')
        
class GetVideoLikesSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.video.likes
        
class VideoLikesSerializer(serializers.ModelSerializer):
    likes = GetVideoLikesSerializer(source='*')
    class Meta:
        model = VideoLikes
        fields = ('id','user','like', 'likes')
        
class getSessionsProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseProgress
        fields = ('id','type','session_id', 'done')
        
# 3 - SubLecture serializer
# |-> 1 - Quiz
class QuizQuestionsSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):  
        questions = instance.question.all()
        questions_list = []
        
        for question in questions:
            question_choices = question.choice.all()
            choices_list = []
            for choice in question_choices:
                choices_list.append({
                    'id': choice.id,
                    'choice': choice.choice,
                    'img': choice.img
                })
            questions_list.append({
                'id': question.id,
                'title': question.title,
                'img': question.img,
                'choices': choices_list
            })
        
        return questions_list
               
class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionsSerializer(source="*")
    class Meta:
        model = SubLectureQuiz
        fields = ('id', 'title', 'description','points','time', 'questions')     
        
class QuizQuestionsSerializerRevision(serializers.BaseSerializer):
    def to_representation(self, instance):  
        questions = instance.question.all()
        questions_list = []
        
        for question in questions:
            question_choices = question.choice.all()
            choices_list = []
            for choice in question_choices:
                choices_list.append({
                    'id': choice.id,
                    'choice': choice.choice,
                    'img': choice.img,
                    'is_true': choice.is_true,
                })
            questions_list.append({
                'id': question.id,
                'title': question.title,
                'img': question.img,
                'choices': choices_list
            })
        
        return questions_list
           
class QuizSerializerRevision(serializers.ModelSerializer):
    questions = QuizQuestionsSerializerRevision(source="*")
    class Meta:
        model = SubLectureQuiz
        fields = ('id', 'title','notes', 'description','points','time', 'questions')
        
class AllQuizResults(serializers.BaseSerializer):
    def to_representation(self, instance):
        num_of_ques = instance.number_of_questions
        points = 0
        degree_percentage = 0
        gpa = 0
        
        if num_of_ques > 0:
            points = float(instance.quiz.points/instance.number_of_questions)*float(instance.degree)
            degree_percentage = (instance.degree/instance.number_of_questions)*100
            
            if points > 0:
                gpa = (points / instance.quiz.points) * 100
                
            
        
        data = {
            'title': instance.quiz.title,
            'number_of_questions': instance.number_of_questions,
            'full_time': instance.quiz.time,
            'time_taken': instance.timer,
            'full_points': instance.quiz.points,
            'points': float('{0:.2f}'.format(points)),
            'gpa': float('{0:.2f}'.format(gpa)),
            'degree': instance.degree,
            'degree_percentage': float('{0:.2f}'.format(degree_percentage)),
            'answers': ast.literal_eval(instance.answers)
        }
        
        return data
        
class QuizResultsSerializer(serializers.ModelSerializer):
    results = AllQuizResults(source="*")
    class Meta:
        model = QuizResult
        fields = ('user', 'quiz','results')
        
class QuizTimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ('user', 'quiz', 'timer','start')

class QuizSubscribersUserInfo(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.user.id,
            'name': instance.user.first_name + ' ' + instance.user.last_name,
            'phone': instance.user.phone
        }

class QuizSubscribersSerializer(serializers.ModelSerializer):
    user_info = QuizSubscribersUserInfo(source='*')
    quiz_info = AllQuizResults(source='*')
    points = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizResult     
        fields = ('id', 'start',  'done', 'user_info','quiz_info','points','time') 
        
    def get_points(self, obj):
        return obj.quiz.points
    
    def get_time(self, obj):
        return obj.quiz.time
        
# payment
class getTransactionNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        fields = ('user', 'course', 'is_active', 'transaction')

# notifications
class GetNotificationsUnReadCountSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    
    class Meta:
        model = NewUser
        fields = ('count',)
        
    def get_count(self,obj):
        user_notifications_count = UserNotificationInfo.objects.filter(user=obj,seen=False).count()
            
        return user_notifications_count
           
class NotificationsInfoSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        notification = instance.notification
        data = {
            'title': notification.title,
            'context': notification.context,
            'from': f'{notification.from_user.first_name} {notification.from_user.last_name}' if notification.from_user else None,
            'to': notification.to_user.first_name if notification.to_user else None,
            'is_superuser': notification.from_user.is_superuser if notification.from_user else None,
            'is_staff': notification.from_user.is_staff if notification.from_user else None,
            'created_dt': notification.created_dt
        }
        return data

class NotificationsSerializer(serializers.ModelSerializer):
    notification_data = NotificationsInfoSerializer(source='*', required=False)
    class Meta:
        model = UserNotificationInfo
        fields = ('id', 'seen', 'notification_data')

class NotificationsExtraFieldsForStaff(serializers.BaseSerializer):
    def to_representation(self, instance):
        data = {
            'from_user': {
                'id': instance.from_user.id if instance.from_user else None,
                'name': instance.from_user.first_name if instance.from_user else None,
            },
            'to_user': {
                'id': instance.to_user.id if instance.to_user else None,
                'name': instance.to_user.first_name if instance.to_user else None,
            }
        }
        
        return data
    
        

class NotificationsSerializerForStaff(serializers.ModelSerializer):
    transmission = NotificationsExtraFieldsForStaff(source='*', required=False)
    sended_count = serializers.SerializerMethodField(required=False)
    class Meta:
        model = Notification
        fields = ('id','title', 'context','transmission', 'created_dt', 'sended_count')
        
    def get_sended_count(self,obj):
        sended_to = UserNotificationInfo.objects.filter(notification=obj)
        return sended_to.count()
    
class BasicNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id','title', 'context')
    
class UsersBasicInfoSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = NewUser
        fields = ('id', 'name',)
    
    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name} - {obj.id}'

        
    

# admin and staff
class UserFromItsProfile(serializers.BaseSerializer):
    def to_representation(self, instance):
        user = get_object_or_404(NewUser, pk=instance.user.id)
        info = {
            "id": user.id,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            'data_join': user.start_date,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        return info
    
class ProfileSerializerForAdmin(serializers.ModelSerializer):
    userInfo = UserFromItsProfile(source="*")
    class Meta:
        model = Profile
        fields = ('id','user', 'parent_phone', 'state', 'gender', 'grade','is_private','extra_permissions','is_vip','userInfo')

# class UserByGradeSerializer(serializers.ModelSerializer):
#     users = ProfileSerializerForAdmin(source='Grade', many=True)

class AddCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'description','image','grade','price_off', 'price','new', 'is_active')
        
    

# payments from admin view 
class getUserFromItsRequest(serializers.BaseSerializer):
    def to_representation(self, instance):
        user = get_object_or_404(NewUser, pk=instance.user.id)
        info = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone
        }
        return info
    
class getCourseFromItsRequest(serializers.BaseSerializer):
    def to_representation(self, instance):
        course = get_object_or_404(Course, pk=instance.course.id)
        info = {
            'id': course.id,
            'title': course.title,
        }
        return info

class PaymentSerializer(serializers.ModelSerializer):
    user_info = getUserFromItsRequest(source="*")
    course_info = getCourseFromItsRequest(source="*")
    class Meta:
        model = UserCourse
        fields = ('id','course_price','phone','price', 'request_dt', 'transaction', 'is_active', 'user_info', 'course_info')

class CourseSubscribers(serializers.BaseSerializer):
    def to_representation(self, instance):
        subscribers_list = []
        subscribers = UserCourse.objects.filter(course=instance, is_active=True).order_by('-request_dt')
        for subscriber in subscribers:
            data = {
                'subscriber_id': subscriber.id,
                'user_id': subscriber.user.id,
                'username': subscriber.user.first_name +' '+ subscriber.user.last_name,
                'phone': subscriber.user.phone,
                'request_dt': subscriber.request_dt,
                'price': subscriber.price
            }
            subscribers_list.append(data)
        return subscribers_list
        
class CourseSerializerFieldsAdmin(serializers.BaseSerializer):
    def to_representation(self, instance):
        lectures = instance.CourseLecture.all()
        course_list = []
        
        for lecture in lectures:
            # videos
            sub_lecture_videos = lecture.LectureVideo.all().values('id', 'title','description', 'type','priority','done', 'active', 'created_dt', 'updated_dt')
            
            # documents (pdf)
            sub_lecture_documents = lecture.LectureDocument.all().values('id', 'title','description', 'type','priority','done', 'active', 'created_dt', 'updated_dt')
            
            # quizzes
            sub_lecture_quizzes = lecture.LectureQuiz.all().values('id', 'title','description', 'type','priority','done', 'active', 'created_dt', 'updated_dt')
            
            # concat lists
            list = []
            list.extend(sub_lecture_videos)
            list.extend(sub_lecture_documents)
            list.extend(sub_lecture_quizzes)
            
            sub_lectures_list = sorted(list, key=operator.itemgetter('priority'))
            # course_list.__setitem__(lecture.title, sub_lectures_list)
            lecture_obj = {
                'id': lecture.id,
                'title': lecture.title,
                'description': lecture.description,
                'content': sub_lectures_list,
                'active': lecture.active,
                'created_dt': lecture.created_dt,
                'updated_dt': lecture.updated_dt,
            }
            course_list.append(lecture_obj)
        
        return course_list
        
class CourseSerializerWithExtraFieldsAdmin(serializers.ModelSerializer):
    subscribers = CourseSubscribers(source="*")
    grade_info = CourseGradeInfo(source="*")
    lectures = CourseSerializerFieldsAdmin(source="*")
    is_paid = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ('id','title', 'description','image','grade_info', 'price_off','price', 'is_active','new', 'lectures','upload_date', 'update_date', 'is_paid', 'subscribers')
        
    def get_is_paid(self,obj):
        user_subscribed = False
        
        try:
            user_id = self.context['request'].user.id
            user = NewUser.objects.get(id=user_id)
        except:
            user_subscribed = False
        try:
            user_course = UserCourse.objects.get(
                user=user,
                course=obj
            )
            if user_course:
                if user_course.is_active == True:
                    user_subscribed = True
        except:
            user_subscribed = False
            
        return user_subscribed
    
    
class CreateLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ('title', 'description', 'course', 'active')
        
class CreateSessionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubLectureVideo
        fields = ('title', 'description', 'lecture','type','priority', 'active','video_embed')

class CreateSessionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubLectureDocument
        fields = ('title', 'description', 'lecture','type','priority','document', 'active')


class GetSessionQuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionsSerializerRevision(source="*")
    class Meta:
        model = SubLectureQuiz
        fields = ('title', 'description','see_results','notes', 'lecture','type','priority','points','time', 'active','questions')
    
class CreateSessionQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubLectureQuiz
        fields = ('title', 'description', 'lecture','type','priority','points','time', 'active')
        
class CreateQuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ('title', 'image', 'quiz')

class CreateQuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ('choice', 'image', 'question', 'is_true')

