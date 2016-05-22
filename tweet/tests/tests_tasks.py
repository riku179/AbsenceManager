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
    def prepare(self):
        self.test_user = User.objects.create(username='TestUser')
        self.test_user.save()
        UserProfile.objects.create(user=self.test_user, watch_tl=True).save()
        self.UID = 114514
        SocialAccount.objects.create(user=self.test_user, uid=self.UID, provider='twitter').save()


    def prepare_subjects(self):
        self.sub1 = Subject(user=self.test_user, period=1, day='Mon', name='spam')
        self.sub2 = Subject(user=self.test_user, period=2, day='Mon', name='egg')
        self.sub3 = Subject(user=self.test_user, period=4, day='Mon', name='spam egg')
        self.sub4 = Subject(user=self.test_user, period=6, day='Mon', name='spam spam egg')
        self.sub5 = Subject(user=self.test_user, period=2, day='Tue', name='spam spam egg spam')
        self.sub6 = Subject(user=self.test_user, period=3, day='Tue', name='egg spam spam egg spam')
        self.sub7 = Subject(user=self.test_user, period=4, day='Thu', name='egg spam egg spam spam spam')
        self.sub8 = Subject(user=self.test_user, period=1, day='Fri', name='egg egg spam egg spam spam spam')
        self.sub9 = Subject(user=self.test_user, period=5, day='Fri', name='spam egg egg spam egg spam spam spam')
        self.sub1.save(); self.sub2.save(); self.sub3.save(); self.sub4.save(); self.sub5.save(); self.sub6.save(); self.sub7.save(); self.sub8.save(); self.sub9.save()


    def test_ok_usr_ok_pattern(self):
        """
        正常系(月曜日)
        """
        self.prepare()
        self.prepare_subjects()
        update_attendance(user_id=self.UID, attendance_pattern='oxlc', today=0)
        self.assertEqual(Attendance.objects.get(subject=self.sub1, times=1).absence, 'attend')
        self.assertEqual(Attendance.objects.get(subject=self.sub2, times=1).absence, 'absent')
        self.assertEqual(Attendance.objects.get(subject=self.sub3, times=1).absence, 'late')
        with self.assertRaises(ObjectDoesNotExist):
            Attendance.objects.get(subject=self.sub4, times=1).absence


    def test_ng_user_ok_pattern(self):
        self.prepare()
        self.prepare_subjects()
        update_attendance(user_id=1919, attendance_pattern='oxlc', today=0)
        with self.assertRaises(ObjectDoesNotExist):
            Attendance.objects.get(subject=self.sub1, times=1).absence

