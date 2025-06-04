from django.db import models

# Create your models here.
class Manufacturer(models.Model):
    title = models.CharField(max_length=25)
    member_count = models.IntegerField()
    ticket_count = models.IntegerField()
    tasks_to_do_count = models.IntegerField()
    tasks_high_prio_count = models.IntegerField()
    owner_id = models.IntegerField()

    def __str__(self):
        return self.name