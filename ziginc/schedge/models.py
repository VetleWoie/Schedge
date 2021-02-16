from django.db import models
import hashlib
# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=25)
    password = models.IntegerField() # DONT USE REAL PASSOWRD YET
     
    def __str__(self):
        return ("User: " + str(self.username))
        # return ("User: " + str(self.username) + ", PWHash: " + str(self.password))