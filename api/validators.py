import datetime as dt

from rest_framework import serializers


def year_validator(value):
    if value > dt.datetime.now().year:
        raise serializers.ValidationError(
            'It is not a correcrt year.'
        )
