from django.db import models
from users.models import CustomUser

class Spam(models.Model):
    phone_number = models.CharField(max_length=15)
    marked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='spam_marked')

    def __str__(self):
        return f"{self.phone_number} marked as spam by {self.marked_by}"
