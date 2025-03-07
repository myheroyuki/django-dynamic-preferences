from datetime import timezone
from decimal import Decimal

from datetime import date, timedelta, datetime, time
from django.test import TestCase, override_settings
from django.template import defaultfilters

from dynamic_preferences import serializers
from .test_app.models import BlogEntry


class TestSerializers(TestCase):

    def test_boolean_serialization(self):
        s = serializers.BooleanSerializer

        self.assertEqual(s.serialize(True), "True")
        self.assertEqual(s.serialize(False), "False")
        with self.assertRaises(s.exception):
            s.serialize('yolo')

    def test_boolean_deserialization(self):

        s = serializers.BooleanSerializer

        for v in s.true:
            self.assertEqual(s.deserialize(v), True)

        for v in s.false:
            self.assertEqual(s.deserialize(v), False)

        with self.assertRaises(s.exception):
            s.deserialize("I'm a true value")

    def test_int_serialization(self):

        s = serializers.IntSerializer

        self.assertEqual(s.serialize(1), "1")
        self.assertEqual(s.serialize(666), "666")
        self.assertEqual(s.serialize(-144), "-144")
        self.assertEqual(s.serialize(0), "0")
        self.assertEqual(s.serialize(123456), "123456")

        with self.assertRaises(s.exception):
            s.serialize("I'm an integer")

    def test_decimal_serialization(self):

        s = serializers.DecimalSerializer

        self.assertEqual(s.serialize(Decimal("1")), "1")
        self.assertEqual(s.serialize(Decimal("-1")), "-1")
        self.assertEqual(s.serialize(Decimal("-666.6")), "-666.6")
        self.assertEqual(s.serialize(Decimal("666.6")), "666.6")

        with self.assertRaises(s.exception):
            s.serialize("I'm a decimal")

    def test_float_serialization(self):

        s = serializers.FloatSerializer

        self.assertEqual(s.serialize(1.0), "1.0")
        self.assertEqual(s.serialize(-1.0), "-1.0")
        self.assertEqual(s.serialize(1), "1.0")
        self.assertEqual(s.serialize(-1), "-1.0")
        self.assertEqual(s.serialize(-666.6), "-666.6")
        self.assertEqual(s.serialize(666.6), "666.6")

        with self.assertRaises(s.exception):
            s.serialize("I'm a float")

    def test_float_deserialization(self):

        s = serializers.FloatSerializer

        self.assertEqual(s.deserialize("1.0"), float("1.0"))
        self.assertEqual(s.deserialize("-1.0"), float("-1.0"))
        self.assertEqual(s.deserialize("-666.6"), float("-666.6"))
        self.assertEqual(s.deserialize("666.6"), float("666.6"))

        with self.assertRaises(s.exception):
            s.serialize("I'm a float")

    def test_int_deserialization(self):

        s = serializers.DecimalSerializer

        self.assertEqual(s.deserialize("1"), Decimal("1"))
        self.assertEqual(s.deserialize("-1"), Decimal("-1"))
        self.assertEqual(s.deserialize("-666.6"), Decimal("-666.6"))
        self.assertEqual(s.deserialize("666.6"), Decimal("666.6"))

        with self.assertRaises(s.exception):
            s.serialize("I'm a decimal!")

    def test_string_serialization(self):

        s = serializers.StringSerializer

        self.assertEqual(s.serialize("Bonjour"), "Bonjour")
        self.assertEqual(s.serialize("12"), "12")
        self.assertEqual(s.serialize(
            "I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        # check for HTML escaping
        kwargs = {"escape_html": True, }
        self.assertEqual(
            s.serialize(
                "<span>Please, I don't wanna disappear</span>", **kwargs),
            defaultfilters.force_escape(
                "<span>Please, I don't wanna disappear</span>")
        )

        with self.assertRaises(s.exception):
            s.serialize(('I', 'Want', 'To', 'Be', 'A', 'String'))

    def test_string_deserialization(self):

        s = serializers.StringSerializer
        self.assertEqual(s.deserialize("Bonjour"), "Bonjour")
        self.assertEqual(s.deserialize("12"), "12")
        self.assertEqual(s.deserialize(
            "I'm a long sentence, but I rock"), "I'm a long sentence, but I rock")

        # check case where empty string (value can be None)
        self.assertEqual(s.deserialize(None), '')
        self.assertEqual(s.deserialize(''), '')

        kwargs = {"escape_html": True, }
        self.assertEqual(
            s.deserialize(
                s.serialize("<span>Please, I don't wanna disappear</span>", **kwargs)),
            defaultfilters.force_escape(
                "<span>Please, I don't wanna disappear</span>")
        )

    def test_duration_serialization(self):
        s = serializers.DurationSerializer

        self.assertEqual(s.serialize(timedelta(minutes=1)), '00:01:00')
        self.assertEqual(s.serialize(timedelta(milliseconds=1)), '00:00:00.001000')
        self.assertEqual(s.serialize(timedelta(weeks=1)), '7 00:00:00')

        with self.assertRaises(s.exception):
            s.serialize('Not a timedelta')

    def test_duration_deserialization(self):
        s = serializers.DurationSerializer

        self.assertEqual(s.deserialize('7 00:00:00'), timedelta(weeks=1))

        with self.assertRaises(s.exception):
            s.deserialize('Invalid duration string')

    def test_date_serialization(self):
        s = serializers.DateSerializer

        self.assertEqual(s.serialize(date(2017, 10, 5)), '2017-10-05')

        with self.assertRaises(s.exception):
            s.serialize('Not a date')

    def test_date_deserialization(self):
        s = serializers.DateSerializer

        self.assertEqual(s.deserialize('1900-01-01'), date(1900, 1, 1))

        with self.assertRaises(s.exception):
            s.deserialize('Invalid date string')
            
    def test_datetime_serialization(self):
        s = serializers.DateTimeSerializer

        # If TZ is enabled default timezone is America/Chicago
        # https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-TIME_ZONE
        self.assertEqual(s.serialize(datetime(2017, 10, 5, 23, 45, 1, 792346)), '2017-10-05T23:45:01.792346-05:00')

        with override_settings(USE_TZ=False):
            self.assertEqual(s.serialize(datetime(2017, 10, 5, 23, 45, 1, 792346)), '2017-10-05T23:45:01.792346')

        with self.assertRaises(s.exception) as ex:
            s.serialize('a string')
            self.assertEqual(ex.exception.args, ("Cannot serialize, value 'a string' is not a datetime object",))

    def test_datetime_deserialization(self):
        s = serializers.DateTimeSerializer

        self.assertEqual(s.deserialize('2017-10-05T23:45:01.792346'), datetime(2017, 10, 5, 23, 45, 1, 792346))
        self.assertEqual(s.deserialize('2017-10-05T23:45:01.792346+00:00'), datetime(2017, 10, 5, 23, 45, 1, 792346, tzinfo=timezone.utc))

        with self.assertRaises(s.exception) as ex:
            s.deserialize('abcd')
            self.assertEqual(ex.exception.args, ('Value abcd cannot be converted to a datetime object',))


    def test_time_serialization(self):
        s = serializers.TimeSerializer

        self.assertEqual(s.serialize(time(hour=5)), '05:00:00')
        self.assertEqual(s.serialize(time(minute=30)), '00:30:00')
        self.assertEqual(s.serialize(time(23, 59, 59, 999999)), '23:59:59.999999')

        with self.assertRaises(s.exception):
            s.serialize('Not a time')

    def test_time_deserialization(self):
        s = serializers.TimeSerializer

        self.assertEqual(s.deserialize('23:00:00'), time(hour=23))

        with self.assertRaises(s.exception):
            s.deserialize('Invalid time string')

    def test_multiple_serialization(self):
        s = serializers.MultipleSerializer

        self.assertEqual(s.serialize(['a', 'b', 'c']), 'a,b,c')
        self.assertEqual(s.serialize(['key,with,comma', 'b', 'another,key,with,comma']),
            'another,,key,,with,,comma,b,key,,with,,comma')

        with self.assertRaises(s.exception):
            s.serialize(['a', '', 'c'])

    def test_multiple_deserialization(self):
        s = serializers.MultipleSerializer

        self.assertEqual(s.deserialize('a,b,c'), ['a', 'b', 'c'])
        self.assertEqual(s.deserialize('key,,with,,comma,b,another,,key,,with,,comma'),
            ['key,with,comma', 'b', 'another,key,with,comma'])


class TestModelSerializers(TestCase):

    def setUp(self):
        super(TestModelSerializers, self).setUp()
        BlogEntry.objects.bulk_create([
            BlogEntry(title='This is a test', content='Hello World'),
            BlogEntry(title='This is only a test', content='Hello World'),
        ])

    def test_model_multiple_serialization(self):
        s = serializers.ModelMultipleSerializer(BlogEntry)
        blog_entries = BlogEntry.objects.all()

        self.assertEqual(s.serialize(blog_entries), s.separator.join(map(str, sorted(list(blog_entries.values_list('pk', flat=True))))))

    def test_model_multiple_deserialization(self):
        s = serializers.ModelMultipleSerializer(BlogEntry)
        blog_entries = BlogEntry.objects.all()
        pks = s.separator.join(map(str, sorted(list(blog_entries.values_list('pk', flat=True)))))

        self.assertEqual(list(s.deserialize(pks)), list(blog_entries))

    def test_model_multiple_single_serialization(self):
        s = serializers.ModelMultipleSerializer(BlogEntry)
        blog_entry = BlogEntry.objects.all().first()

        self.assertEqual(s.serialize(blog_entry), s.separator.join(map(str, [blog_entry.pk])))
