from django.db import models
from django_countries.fields import CountryField
from oscar.apps.customer.abstract_models import AbstractUser


# Extensiones a Users definidos en Oscar
class User(AbstractUser):
    pass
