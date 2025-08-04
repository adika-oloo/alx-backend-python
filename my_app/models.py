from django.db import models
class Book(models.models):
    tittle = models.Charfield(max_length = 200)
    author = models.CharField(max_length = 100)
    published_date = models.DateField()



