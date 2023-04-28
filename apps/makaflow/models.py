# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

# from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.html import format_html

from common.models import BaseModel
from common.util.storage import UUIDFileName
