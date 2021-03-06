from django.db import models
from django.db.models import Count, Max
from django.contrib.auth.models import User


class Subject(models.Model):
    DAY_OF_WEEK = (
        ('Mon', '月'),
        ('Tue', '火'),
        ('Wed', '水'),
        ('Thu', '木'),
        ('Fri', '金'),
        ('Sat', '土')
    )
    name = models.CharField('科目名', max_length=50)
    period = models.IntegerField('時限')
    day = models.CharField('曜日', max_length=3, choices=DAY_OF_WEEK)
    user = models.ForeignKey(User, verbose_name='ユーザー', related_name='subject', null=True, blank=True)

    def sum_of_classes(self):
        """

        :return: 総授業回数
        """
        return Subject.objects.filter(id=self.id) \
            .aggregate(count=Count('attendance'))['count']

    def sum_of_attend(self):
        """

        :return: 総出席数
        """
        return self.sum_of_late() + Subject.objects.filter(id=self.id) \
            .filter(attendance__absence='attend') \
            .aggregate(count=Count('attendance'))['count']

    def sum_of_absence(self):
        """

        :return: 総欠席数
        """
        return Subject.objects.filter(id=self.id) \
            .filter(attendance__absence='absent') \
            .aggregate(count=Count('attendance'))['count']

    def sum_of_late(self):
        """

        :return: 総遅刻回数
        """
        return Subject.objects.filter(id=self.id) \
            .filter(attendance__absence='late') \
            .aggregate(count=Count('attendance'))['count']

    def get_latest_attendance(self):
        return Attendance.objects.filter(subject=self).aggregate(Max('times'))['times__max']

    def __str__(self):
        return self.name

ATTENDANCE_STATUS = (
    ('attend', '出席'),
    ('absent', '欠席'),
    ('late', '遅刻'),
    ('unknown', '不明'),
    ('cancel', '休講')
)

class Attendance(models.Model):

    subject = models.ForeignKey(Subject, verbose_name='科目', related_name='attendance')
    times = models.IntegerField('授業回数')
    absence = models.CharField('出席状況', max_length=7, choices=ATTENDANCE_STATUS)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.subject.name) + "(第" + str(self.times) + "回)"
