from django.db import models


# Create your models here.

class Subject(models.Model):
    WEEK_OF_DAY = (
        ('Mon', '月'),
        ('Tue', '火'),
        ('Wed', '水'),
        ('Thu', '木'),
        ('Fri', '金'),
        ('Sat', '土'),
        ('Sun', '日')
    )
    subject_name = models.CharField('科目名', max_length=50)
    period = models.IntegerField('時限')
    day = models.CharField('曜日', max_length=3, choices=WEEK_OF_DAY)
    absence = models.IntegerField('欠席回数', default=0)

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
    date = models.DateField('日付')
    number_of_times = models.IntegerField('授業回数')
    attendance = models.CharField('出席状況', max_length=7, choices=ATTENDANCE_STATUS)

    def __str__(self):
        return str(self.subject.subject_name) + "(第" + str(self.number_of_times) + "回)"
