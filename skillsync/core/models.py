from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username
    
# Create your models here.
class Project(models.Model):
    description = models.TextField()
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class Bid(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    freelancer = models.CharField(max_length=100)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer} - {self.amount}"