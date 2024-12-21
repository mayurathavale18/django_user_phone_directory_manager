from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)  # Add this if missing
    contacts = models.ManyToManyField('self', blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Custom related name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Custom related name
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
