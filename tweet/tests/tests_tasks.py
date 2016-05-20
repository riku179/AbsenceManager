from django.test import TestCase
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

from tweet.tasks import update_attendance
from authentication.models import UserProfile
from table.models import Attendance, Subject


class TestUpdateAttendance(TestCase):
    '''
    test update_attendance()
    '''
    test_user = User(username='TestUser')
    test_user.save()
    UserProfile(user=test_user, watch_tl=False).save()
    UID = 114514
    SocialAccount(user=test_user, uid=UID, provider='twitter').save()

    def attend_mondey(self):
        sub1 = Subject(user=test_user, period=1, day='Mon', name='spam')
        sub2 = Subject(user=test_user, period=2, day='Mon', name='egg')
        sub3 = Subject(user=test_user, period=4, day='Mon', name='spam egg')
        sub4 = Subject(user=test_user, period=6, day='Mon', name='spam spam egg')
        sub5 = Subject(user=test_user, period=2, day='Tue', name='spam spam egg spam')
        sub6 = Subject(user=test_user, period=3, day='Tue', name='egg spam spam egg spam')
        sub7 = Subject(user=test_user, period=4, day='Thu', name='egg spam egg spam spam spam')
        sub8 = Subject(user=test_user, period=1, day='Fri', name='egg egg spam egg spam spam spam')
        sub9 = Subject(user=test_user, period=5, day='Fri', name='spam egg egg spam egg spam spam spam')
        sub1.save(); sub2.save(); sub3.save(); sub4.save(); sub5.save(); sub6.save(); sub7.save(); sub8.save(); sub9.save()

    def test_ng_user_ok_pattern(self):
        self.attend_mondey()
        update_attendance(user_id=1919, attendance_pattern='oxlu', today=0)
        self.assertEqual(Attendance.objects.get(subject=self.sub1, times=1).absence, ObjectDoesNotExist)

    def test_ok_usr_ok_pattern(self):
        """
        正常系(月曜日)
        """
        self.attend_mondey()
        update_attendance(user_id=self.UID, attendance_pattern='oxlu', today=0)
        self.assertEqual(Attendance.objects.get(subject=self.sub1, times=1).absence, 'attend')
        self.assertEqual(Attendance.objects.get(subject=self.sub2, times=1).absence, 'absent')
        self.assertEqual(Attendance.objects.get(subject=self.sub3, times=1).absence, 'late')
        self.assertEqual(Attendance.objects.get(subject=self.sub4, times=1).absence, ObjectDoesNotExist)


