from django.db import models
from django.db.models import Count


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

    def sum_of_classes(self):
        return Subject.objects.filter(id=self.id) \
            .aggregate(count=Count('attendance'))['count']

    def sum_of_absence(self):
        return Subject.objects.filter(id=self.id) \
            .filter(attendance__absence='absent') \
            .aggregate(count=Count('attendance'))['count']

    def sum_of_late(self):
        return Subject.objects.filter(id=self.id) \
            .filter(attendance__absence='late') \
            .aggregate(count=Count('attendance'))['count']

    def __str__(self):
        return self.subject_name


class Attendance(models.Model):
    ATTENDANCE_STATUS = (
        ('attend', '出席'),
        ('absent', '欠席'),
        ('late', '遅刻'),
        ('unknown', '不明')
    )
    subject = models.ForeignKey(Subject, verbose_name='科目', related_name='attendance')
    times = models.IntegerField('授業回数')
    absence = models.CharField('出席状況', max_length=7, choices=ATTENDANCE_STATUS)

    def __str__(self):
        return str(self.subject.subject_name) + "(第" + str(self.number_of_times) + "回)"
