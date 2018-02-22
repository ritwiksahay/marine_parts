"""Extensiones a Users definidos en Oscar."""

from django.db import models
from django_countries.fields import CountryField
from oscar.apps.customer.abstract_models import AbstractUser


class User(AbstractUser):
    pass