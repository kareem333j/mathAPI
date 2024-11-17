from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # tokens
    path('token/', MyTokenObtainPairSerializerView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('profile/<int:pk>', UserProfile.as_view(), name="user_profile"),
    path('profile/<int:pk>/all', AllDataProfile.as_view(), name="all_data_profile"),
    
    # course API URL
    path('grades',GradesView.as_view(), name='grades'),
    path('grades/grade/<int:pk>',GetGradeInfo.as_view(), name='grade'),
    path('courses',CoursesView.as_view(), name='courses'),
    path('courses/grade/<str:pk>',CoursesFilterWithGradeView.as_view(), name='courses_get'),
    path('courses/course/<int:pk>', RetrieveCourseAllFields.as_view(), name='course'),
    path('courses/<int:pk>/lectures', LecturesView.as_view(), name='course_lectures'),
    path('courses/payment/process1', PaymentProcessOne.as_view(), name='course_payment_process_one'),
    path('courses/payment/get_transaction/<int:pk>', getTransactionNumber.as_view(), name='get_transaction_number'),
    path('session/done', SessionDone.as_view(), name='update_session_progress'),
    path('course/<int:pk>/sessions', getSessionsProgress.as_view(), name='get_sessions_progress'),
    path('quizzes/<int:pk>', QuizView.as_view(), name='quiz'),
    path('quizzes/send', sendQuizResults.as_view(), name='get_quiz'),
    path('quizzes/<int:pk>/results', GetQuizResults.as_view(), name='get_quiz_results'),
    path('quizzes/<int:pk>/revision', QuizViewRevision.as_view(), name='quiz_revision'),
    path('quizzes/<int:pk>/get_timer', GetQuizTimer.as_view(), name='get_quiz_timer'),
    path('quizzes/timer', QuizTimer.as_view(), name='quiz_timer'),
    path('quizzes/update/video/likes', UpdateVideoLikes.as_view(), name='update_video_likes'),
    path('quizzes/get/video/likes/<int:pk>', GetVideoLikes.as_view(), name='get_video_likes'),
    
    # notifications
    path('users/<int:pk>/notifications/unread', UnreadNotifications.as_view(), name='unread_notifications'),
    path('notifications', RetrieveUserNotifications.as_view(), name='retrieve_notifications'),
    path('notifications/<int:pk>', RetrieveAndSeenNotification.as_view(), name='retrieve_notification'),
    path('notifications/<int:pk>/seen', RetrieveAndSeenNotification.as_view(), name='seen_notification'),
    path('notifications/<int:pk>/delete', RemoveNotification.as_view(), name='delete_notification'),
    path('notifications/delete/all', RemoveUserNotifications.as_view(), name='delete_all_notifications'),    
    
    # course API URLs for admin and staff
    path('admin/users',GetProfiles.as_view(),name='profiles'),
    path('admin/users/basic',UsersBasicInfoList.as_view(),name='user_basic_info'),
    path('admin/users/<int:pk>/delete',DeleteUser.as_view(),name='delete_user'),
    path('admin/users/<int:pk>/give',GivePermissions.as_view(),name='give_permissions'),
    path('admin/users/search/<str:search_item>',SearchProfile.as_view(),name='search_profile'),
    path('admin/courses',CoursesViewManager.as_view(),name='courses_staff'),
    path('admin/courses/course/<int:pk>',RetrieveCourseAllFieldsAdmin.as_view(),name='course_info_admin'),
    path('admin/courses/search/<str:search_item>',SearchCoursesView.as_view(), name='courses_search'),
    path('admin/courses/course/<int:pk>',GetCourseViewManager.as_view(),name='course_staff'),
    path('admin/courses/add', AddCourse.as_view(), name='add_course'),
    path('admin/courses/lectures/<int:pk>', GetLecture.as_view(), name='get_lecture'),
    path('admin/courses/<int:pk>/lectures/add', AddLecture.as_view(), name='add_lecture'),
    path('admin/courses/lectures/<int:pk>/update', UpdateLecture.as_view(), name='update_lecture'),
    path('admin/courses/lectures/<int:pk>/delete', DeleteLecture.as_view(), name='delete_lecture'),
    path('admin/courses/lectures/sessions/<str:type>/<int:pk>', GetSession.as_view(), name='get_session'),
    path('admin/courses/lectures/sessions/add', AddSession.as_view(), name='add_session'),
    path('admin/courses/lectures/sessions/<int:pk>/update', UpdateSession.as_view(), name='update_session'),
    path('admin/courses/lectures/sessions/<str:type>/<int:pk>/delete', DeleteSession.as_view(), name='delete_session'),
    path('admin/courses/course/<int:pk>/edit', EditCourse.as_view(), name='edit_course'),
    path('admin/courses/course/<int:pk>/delete', DeleteCourse.as_view(), name='delete_course'),
    path('admin/courses/payments/requests',PaymentsList.as_view(),name='course_payment_requests'),
    path('admin/courses/payments/search/<str:search_item>',SearchPayments.as_view(),name='search_payment_requests'),
    path('admin/courses/payments/<str:transaction_num>/activate',ActivePayment.as_view(),name='activate_payment'),
    path('admin/quizzes/<int:pk>/subscribers',QuizSubscribersList.as_view() ,name='quiz_subscribers'),
    
    # notifications for staff
    path('admin/notifications',NotificationsList.as_view(),name='notifications'),
    path('admin/notifications/<int:pk>',RetrieveUpdateNotification.as_view(),name='notifications.get'),
    path('admin/notifications/add',AddNotification.as_view(),name='notifications.add'),
    path('admin/notifications/<int:pk>/delete',DeleteNotification.as_view(),name='notifications.delete'),
    path('admin/notifications/<int:pk>/update',RetrieveUpdateNotification.as_view(),name='notifications.update'),
]