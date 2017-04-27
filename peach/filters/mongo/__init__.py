from peach.filters import BaseFilter
from datetime import datetime


class DateFilter(BaseFilter):

    name = 'date'
    value_type = datetime
    allow_multiple = False

    @classmethod
    def condition(cls, date_value, **kwargs):
        return {'date': date_value}


class DateRangeFilter(BaseFilter):

    name = 'date_range'
    value_type = datetime
    allow_multiple = True

    @classmethod
    def condition(cls, from_date, to_date, **kwargs):
        return {'date': {"$gte": from_date, "$lte": to_date}}


class NameFilter(BaseFilter):

    name = 'name'
    value_type = str
    allow_multiple = True

    @classmethod
    def condition(cls, *names):
        return {
            'name': {
                "$regex": ".*?{}.*?".format('|'.join(names)),
                "$options": 'si'
            }
        }
