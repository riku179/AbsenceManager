from django.test import TestCase

from table.models import Subject, Attendance


class TestSubjectModel(TestCase):
    def test_is_empty(self):
        self.assertEqual(Subject.objects.count(), 0)

    def test_can_create(self):
        new_model = Subject(name='Test', period=1, day='Mon')
        new_model.save()
        filtered_model = Subject.objects.get(name__exact='Test')
        self.assertEqual(filtered_model.period, 1)
