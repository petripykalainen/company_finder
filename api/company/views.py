from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from dateutil.parser import parse
from django.core import serializers
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime

import logging
import requests
import datetime
import pytz

from .models import Company


def index(request):

    result = []

    # Check for date query parameter
    try:
        year, month, day = request.GET.get('date').split("-")
        date_query = datetime.datetime(int(year), int(month), int(day))
        date_start = date_query + datetime.timedelta(days=-1)
        date_end = date_query + datetime.timedelta(days=1)
    except AttributeError:
        result = "Missing correct query parameter 'date'"
        return JsonResponse({"error": result})
    except ValueError:
        result = "Wrong date format, use yyyy-mm-dd"
        return JsonResponse({"error": result})

    # Check DB for company info
    # datetime.date(
        # date_query.year,
        # date_query.month,
        # date_query.day)

    date_str = request.GET.get('date')
    date_format = '%Y-%m-%d'
    query_date = pytz.utc.localize(datetime.datetime.strptime(
        date_str, date_format))

    result = list(Company.objects.filter(
        registrationDate=query_date).values(
            'businessId',
            'registrationDate',
            'companyForm',
            'detailsUri',
            'name',
        ))

    # # Query api for total count and then requery for all data
    if len(result) == 0:

        date_real = "{}-{}-{}".format(
            '%02d' % date_query.year,
            '%02d' % date_query.month,
            '%02d' % date_query.day)
        date_from = "{}-{}-{}".format(
            '%02d' % date_start.year,
            '%02d' % date_start.month,
            '%02d' % date_start.day)
        date_to = "{}-{}-{}".format(
            '%02d' % date_end.year,
            '%02d' % date_end.month,
            '%02d' % date_end.day)

        url = ('http://avoindata.prh.fi/bis/v1?'
               'totalResults=true'
               '&maxResults=1000'
               '&companyRegistrationFrom={}'
               '&companyRegistrationTo={}').format(date_from, date_to)

        response = requests.get(url)
        query_result = response.json()["results"]

        for company in query_result:
            validdate = date_real == company["registrationDate"]
            if validdate:
                result.append(company)

        # Insert data to DB and result object
        for company in query_result:
            companyid = company["businessId"]
            companyindb = Company.objects.filter(businessId=companyid)

            if len(companyindb) == 0:
                try:
                    new_company = Company()
                    new_company.businessId = company["businessId"]
                    new_c_date = pytz.utc.localize(
                        datetime.datetime.strptime(
                            company["registrationDate"], date_format))
                    new_company.registrationDate = new_c_date
                    new_company.companyForm = company["companyForm"]
                    new_company.detailsUri = company["detailsUri"]
                    new_company.name = company["name"]
                    new_company.save()
                except IntegrityError:
                    continue

    # Return Json
    return JsonResponse(result, safe=False)
