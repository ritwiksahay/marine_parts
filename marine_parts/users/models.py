from django.db import models
from django_countries.fields import CountryField
from oscar.apps.customer.abstract_models import AbstractUser

# Extensiones a Users definidos en Oscar
class User(AbstractUser):

    def get_full_name(self):
        full_name = '%s %s' % (self.last_name.upper(), self.first_name)
        return full_name.strip()


class Customer(models.Model):

    GENDER = (
        ('F', 'Female'),
        ('M', 'Male'),
    )

    birthday = models.DateField()
    # Oscar define clases abtractas para esto
    #billing_address = models.CharField(max_length=255)
    #shipping_address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    gender = models.CharField(max_length=2, choices=GENDER)
    #user = models.ForeignKey(User)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Store(models.Model):
    name = models.CharField(max_length=100)
    country = CountryField()
