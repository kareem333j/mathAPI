from blog.models import *
from users.models import Profile

front_url = 'http://localhost:3000'

def send_notification_for_subscribers(course, notification, title, context):
    if notification == True or notification == 'true':
        notification = Notification.objects.create(
            title= title,
            context= context
        )
        course_subscribers = UserCourse.objects.filter(course=course)
        for subscriber in course_subscribers:
            if notification:
                UserNotificationInfo.objects.create(
                    notification=notification,
                    user = subscriber.user
                )
                
def send_notification_sessions_for_subscribers(course, notification,lecture, session):
    send_notification_for_subscribers(
        course=course,
        notification=notification,
        title='جديد 🆕',
        context=f'''
             لكل المشتركين في كورس "<span style="color:var(--text-cyan-500)">{course.title}</span>"
            تم إضافة حصة جديدة الي "<span style="color:var(--text-cyan-500)">{lecture.title}</span>" في الكورس
            بإسم "<span style="color:var(--text-cyan-500)">{session}</span>"
            يمكنك الأن مشاهدتها
            .
            .
            تابع الحصة من خلال الرابط التالي
            .
            > <a href="{front_url}/courses/{course.grade.id}/course/{course.id}">{front_url}/courses/{course.grade.id}/course/{course.id}</a>
            .
            بالتوفيق ياصديقي❤️
            .
            .
            مع تحيات : الدعم الفني
        '''
    )
    
def send_activation_message(user,course,notification):
    if notification == True:
        notification = Notification.objects.create(
            to_user=user,
            title= 'مبروك 🎉',
            context= f'''
                لقد تم تفعيل إشتراكك في "{course.title}" 
                الأن بإمكانك مشاهدة ومتابعة كل الحصص والمحاضرات 
                الخاصة بالكورس من بيتك بكل سهولة😎
                نتمني لك التوفيق والتميز
                .
                تابع الكورس من خلال الرابط التالي
                .
                > <a href="{front_url}/courses/{course.grade.id}/course/{course.id}">{front_url}/courses/{course.grade.id}/course/{course.id}</a>
                .
                بالتوفيق ياصديقي❤️
                .
                .
                مع تحيات : الدعم الفني
            '''
        )
        if notification:
            UserNotificationInfo.objects.create(
                notification=notification,
                user = user
            )
        
def send_notification_for_added_course(course_title,grade):
    notification = Notification.objects.create(
        title= 'جديد 🆕',
        context= f'''
            كورس جديد الي {grade.name}
            تمت إضافة كورس جديد بعنوان "<span style="color:var(--text-cyan-500)">{course_title}</span>"
            يمكنك الأن متابعة الكورس إذا كان يهمك الأمر
            نتمني لك النجاح والتوفيق
            .
            .
            يمكنك رؤية الكورس وجميع كورسات {grade.name}
            من خلال الرابط التالي
            .
            > <a href="{front_url}/courses/{grade.id}">{front_url}/courses/{grade.id}</a>
            .
            بالتوفيق ياصديقي❤️
            .
            .
            مع تحيات : الدعم الفني
        '''
    )
    print(grade)
    print(grade.name)
    course_subscribers = Profile.objects.filter(grade=grade.name)
    print(course_subscribers)
    for subscriber in course_subscribers:
        if notification:
            UserNotificationInfo.objects.create(
                notification=notification,
                user = subscriber.user
            )
    