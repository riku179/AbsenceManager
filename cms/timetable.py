from django.db.models import Count
from cms.models import Subject, Attendance
from cms.cfg import Config as Cfg


class CreateTimeTable:
    def __init__(self):
        self.day_of_week = [x[1] for x in Subject.DAY_OF_WEEK]
        self.periods = tuple(range(Cfg.MIN_PERIOD - 1, Cfg.MAX_PERIOD))
        self.table = self._create

    def _create(self):
        """

        :rtype: TimeTable
        """

        timetable = []
        for i in self.periods:
            timetable.append([])
            for j in range(len(self.day_of_week)):
                if Subject.objects.filter(period=i + 1).filter(day=j):
                    timetable[i].append(Subject.objects.filter(period=i + 1).filter(day=j)[0])
                else:
                    timetable[i].append('')
        return timetable
