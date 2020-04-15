from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from dateutil.parser import parse
from django.core import serializers

import datetime
import logging
import requests

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
    result = list(Company.objects.filter(
        registrationDate=datetime.date(
            date_query.year,
            date_query.month,
            date_query.day)).values(
                'businessId',
                'registrationDate',
                'companyForm',
                'detailsUri',
                'name',
            ))

    # Query api for total count and then requery for all data
    if len(result) == 0:
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
        result = response.json()["results"]

        # Insert data to DB and result object
        for company in result:
            companyid = company["businessId"]
            companyindb = Company.objects.filter(businessId=companyid)

            if len(companyindb) == 0:
                logger.error("Saving to DB!")
                logger.error(company['name'])
                logger.error(company['registrationDate'])
                try:
                    new_company = Company()
                    new_company.businessId = company["businessId"]
                    new_company.registrationDate = datetime.datetime.strptime(
                        company["registrationDate"], '%Y-%m-%d').date()
                    new_company.companyForm = company["companyForm"]
                    new_company.detailsUri = company["detailsUri"]
                    new_company.name = company["name"]
                    new_company.save()
                except IntegrityError:
                    continue

    # Return Json
    return JsonResponse(result, safe=False)
