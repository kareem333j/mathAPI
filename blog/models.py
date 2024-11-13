from django.db import models
from users.models import NewUser
from django.utils.crypto import get_random_string
import random

# generate transaction symbol to payment action
get_random_string(10).lower()


def course_upload_to(instance, filename):
    return f"courses/{instance.title}/image/{filename}".format(filename=filename)


def lecture_video_upload_to(instance, filename):
    return f"courses/{instance.lecture.course.title}/{instance.lecture.title}/videos/{filename}".format(
        filename=filename
    )


def lecture_document_upload_to(instance, filename):
    return f"courses/{instance.lecture.course.title}/{instance.lecture.title}/documents/{filename}".format(
        filename=filename
    )


def lecture_quiz_upload_to(instance, filename):
    return f"courses/{instance.quiz.lecture.course.title}/{instance.quiz.lecture.title}/quizzes/{instance.quiz.title}/{filename}".format(
        filename=filename
    )

def lecture_quiz_results_upload_to(instance, filename):
    return f"courses/{instance.lecture.course.title}/{instance.lecture.title}/quizzes/{instance.title}/{filename}".format(
        filename=filename
    )


def question_quiz_upload_to(instance, filename):
    return f"courses/{instance.question.quiz.lecture.course.title}/{instance.question.quiz.lecture.title}/quizzes/{instance.question.quiz.title}/choices/{filename}".format(
        filename=filename
    )

class Grade(models.Model):
    name = models.CharField(max_length=300, blank=True, null=False)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

# admin only
class Course(models.Model):
    class CourseActive(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_active=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=False, default=0, upload_to=course_upload_to)
    grade = models.ForeignKey(Grade, related_name='Grade', on_delete=models.CASCADE)
    price_off = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    # get courses
    objects = models.Manager()  # default manager
    active_objects = CourseActive()  # custom manager

    class Meta:
        ordering = ("-upload_date",)

    def __str__(self):
        return self.title


class Lecture(models.Model):
    class Active(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(active=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(
        Course, related_name="CourseLecture", on_delete=models.CASCADE
    )
    active = models.BooleanField(default=False)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    objects = models.Manager()  # default manager
    active_objects = Active()  # custom manager

    def __str__(self):
        return f"{self.title} - {self.course.title}"


subLectureDataType = (
    ("video", "video"),
    ("document", "document"),
    ("quiz", "quiz"),
)


class SubLectureVideo(models.Model):
    class Active(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(active=True)

    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    lecture = models.ForeignKey(
        Lecture, related_name="LectureVideo", on_delete=models.CASCADE
    )
    video = models.FileField(upload_to=lecture_video_upload_to, blank=True, null=True)
    video_embed = models.TextField(null=True)
    video_time = models.CharField(max_length=150, null=True, blank=True)
    type = models.CharField(max_length=150, choices=subLectureDataType, blank=True)
    likes = models.IntegerField(default=0, null=True, blank=True)
    priority = models.IntegerField(null=False, blank=False, default=0)
    done = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    objects = models.Manager()  # default manager
    active_objects = Active()  # custom manager

    def __str__(self):
        return f"{self.title} - {self.lecture.title} - {self.lecture.course.title}"


class VideoLikes(models.Model):
    user = models.ForeignKey(
        NewUser, related_name="user_video_likes", on_delete=models.CASCADE
    )
    video = models.ForeignKey(
        SubLectureVideo, related_name="video_likes", on_delete=models.CASCADE
    )
    like = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} like to {self.video.title}"


class SubLectureDocument(models.Model):
    class Active(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(active=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    lecture = models.ForeignKey(
        Lecture, related_name="LectureDocument", on_delete=models.CASCADE
    )
    document = models.FileField(
        upload_to=lecture_document_upload_to, blank=False
    )
    number_of_pages = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=150, choices=subLectureDataType, blank=True)
    priority = models.IntegerField(null=False, blank=False, default=0)
    done = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    objects = models.Manager()  # default manager
    active_objects = Active()  # custom manager

    def __str__(self):
        return f"{self.title} - {self.lecture.title} - {self.lecture.course.title}"


class SubLectureQuiz(models.Model):
    class Active(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(active=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    lecture = models.ForeignKey(
        Lecture, related_name="LectureQuiz", on_delete=models.CASCADE
    )
    points = models.IntegerField(null=False, blank=False, default=0)
    time = models.IntegerField(default=0)
    type = models.CharField(max_length=150, choices=subLectureDataType, blank=True)
    priority = models.IntegerField(null=False, blank=False, default=0)
    done = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    see_results = models.BooleanField(default=True)
    notes = models.FileField(
        upload_to=lecture_quiz_results_upload_to, blank=True, null=True
    )


    objects = models.Manager()  # default manager
    active_objects = Active()  # custom manager

    def __str__(self):
        return f"{self.title} - {self.lecture.title} - {self.lecture.course.title}"


class QuizQuestion(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True, upload_to=lecture_quiz_upload_to)
    quiz = models.ForeignKey(
        SubLectureQuiz, related_name="question", on_delete=models.CASCADE
    )

    @property
    def img(self):
        if not self.image:
            return None
        else:
            return self.image.url

    def __str__(self):
        return f"{self.title} - {self.quiz.title} - {self.quiz.lecture.title} - {self.quiz.lecture.course.title}"


class QuizChoice(models.Model):
    choice = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=question_quiz_upload_to)
    question = models.ForeignKey(
        QuizQuestion, related_name="choice", on_delete=models.CASCADE
    )
    is_true = models.BooleanField(default=False)

    @property
    def img(self):
        if not self.image:
            return None
        else:
            return self.image.url

    def __str__(self):
        return f"{self.choice} - {self.question}"


class QuizResult(models.Model):
    user = models.ForeignKey(
        NewUser, related_name="UserResults", on_delete=models.CASCADE
    )
    quiz = models.ForeignKey(
        SubLectureQuiz, related_name="QuizResults", on_delete=models.CASCADE
    )

    number_of_questions = models.IntegerField(default=0)
    answers = models.TextField(default="[]")
    right_answers = models.TextField(default="[]")
    degree = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    timer = models.IntegerField(default=0)

    start = models.BooleanField(default=False)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quiz.title} - {self.user.first_name} {self.user.last_name}"


# user courses
class CoursesCart(models.Model):
    user = models.OneToOneField(
        NewUser, related_name="CoursesCart", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

def create_new_ref_number():
    return str(random.randint(1000000000, 9999999999))


# user course
class UserCourse(models.Model):
    user = models.ForeignKey(
        NewUser, related_name="UserCourse", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="Course", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    request_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    transaction = models.CharField(unique=True ,max_length=10,blank=True,default=create_new_ref_number)
    # editable=False => to hide field from admin page and can't edit on it
    
    # generate transaction number to user to payment process
    def create_new_ref_number():
        not_unique = True
        while not_unique:
            unique_ref = random.randint(1000000000, 9999999999)
            if not UserCourseProgress.objects.filter(transaction=unique_ref):
                not_unique = False
        return str(unique_ref)
    
    # def save(self,*args, **kwargs):
    #     self.transaction = get_random_string(10).lower()
    #     super(UserCourseProgress, self).save(*args, **kwargs)
    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.course.title}"




class UserCourseProgress(models.Model):
    user = models.ForeignKey(NewUser, related_name="user", on_delete=models.CASCADE)
    user_course = models.ForeignKey(
        Course, related_name="user_course_progress", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=200, choices=subLectureDataType, blank=True)
    session_id = models.IntegerField(default=0)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} - {self.type} - {self.session_id} - {self.user_course.title}"
    
class Notification(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    context = models.TextField()
    from_user = models.ForeignKey(NewUser, related_name="FromUser", on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(NewUser, related_name="ToUser", on_delete=models.CASCADE, null=True, blank=True)
    created_dt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f'{self.title} - {self.context}'
    
class UserNotificationInfo(models.Model):
    notification = models.ForeignKey(Notification, related_name='Notification', on_delete=models.CASCADE)
    user = models.ForeignKey(NewUser, related_name='UserNotification', on_delete=models.CASCADE, null=True)
    seen = models.BooleanField(default=False)
    created_dt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return f'{self.notification.title}'
