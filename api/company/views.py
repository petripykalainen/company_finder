from django.http import JsonResponse, HttpResponse
from django.core import serializers
from dateutil.parser import parse

import datetime
import logging
import requests

from .models import Company



def index(request):

    url = "http://avoindata.prh.fi/bis/v1?totalResults=true&companyRegistrationFrom={}&companyRegistrationTo={}"

    logger = logging.getLogger(__name__)

    # Check for date
    result = ""
    if request.method == 'GET' and 'date' in request.GET:
        date_string = request.GET['date']
        try:
            date_start = parse(request.GET['date'])
            date_end = date_start + datetime.timedelta(days=1)
        except ValueError:
            result = "Missing date parameter"
            return JsonResponse(result, safe=False)

    # Check DB for company info
    result = list(Company.objects.values().filter(
        registrationDate=datetime.date(
            date_start.year,
            date_start.month,
            date_start.day)))
    if len(result) == 0:
        # Query api for total count and then requery for all data
        date_from = "{}-{}-{}".format(
            '%02d' % date_start.year,
            '%02d' % date_start.month,
            '%02d' % date_start.day)
        date_to = "{}-{}-{}".format(
            '%02d' % date_end.year,
            '%02d' % date_end.month,
            '%02d' % date_end.day)
        url = "http://avoindata.prh.fi/bis/v1?totalResults=true&companyRegistrationFrom={}&companyRegistrationTo={}".format(date_from, date_to)
        response = requests.get(url)
        result = response.json()['results']
        for company in result:
            logger.error(company['name'])
        return JsonResponse(result, safe=False)
        # result = "No companies found"

    # Insert data to DB

    # Return Json
    return JsonResponse(result, safe=False)
