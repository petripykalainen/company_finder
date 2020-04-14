from django.db import models

class Company(models.Model):
    businessId = models.CharField(max_length=200)
    registrationDate = models.DateTimeField('registration date')
    companyForm = models.CharField(max_length=200)
    detailsUri = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
