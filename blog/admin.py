from django.contrib import admin
from .models import *

admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(SubLectureVideo)
admin.site.register(SubLectureDocument)
admin.site.register(SubLectureQuiz)
admin.site.register(QuizQuestion)
admin.site.register(CoursesCart)
admin.site.register(UserCourse)
admin.site.register(QuizResult)
admin.site.register(QuizChoice)
admin.site.register(VideoLikes)
admin.site.register(UserCourseProgress)
admin.site.register(Grade)
admin.site.register(Notification)
admin.site.register(UserNotificationInfo)