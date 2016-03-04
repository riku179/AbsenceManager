import csv
from io import TextIOWrapper

from table.cfg import Config as Cfg
from table.models import Subject


class TimeTable:
    def __init__(self):
        self.day_of_week = [x[0] for x in Subject.DAY_OF_WEEK]
        self.periods = tuple(range(Cfg.MIN_PERIOD - 1, Cfg.MAX_PERIOD))
        self.table = self._create

    def _create(self):
        """

        :rtype: TimeTable
        """

        timetable = []
        for i in self.periods:
            timetable.append([])
            for j in self.day_of_week:
                if Subject.objects.filter(period=i).filter(day=j):
                    timetable[i].append(Subject.objects.filter(period=i).filter(day=j)[0])
                else:
                    timetable[i].append('')
        return timetable


def update_table(file):
    for (period, row) in enumerate(_csv_parser(file)):
        for (day, subject) in enumerate(row):
            if not subject == '':
                Subject(name=subject, period=period, day=Subject.DAY_OF_WEEK[day][0]).save()


def _csv_parser(requested_file):
    reader = csv.reader(TextIOWrapper(requested_file, encoding='shift-jis'))
    sliced = _slice_header([row for row in reader])
    return [row[1:] for row in [sliced[i] for i in [x * 3 for x in range(7)]]]
    #   csvファイルの行を要素としたリストを_cut_headerに渡し、不要な先頭の行をスライス
    #   時間割の月曜１限のコマを基準として、0,3,6,9,12・・・行ごとに科目名のある行があるので、その行のみを抽出し、かつ各行の先頭１コマにある余計な空要素をスライス
    #   科目名のみの行を要素としたリストを返す


def _slice_header(list):
    for (row_num, row) in enumerate(list):
        for egg in row:
            if egg == '1限':
                return list[row_num + 1:]
