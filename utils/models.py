from django.db import models


# Create your models here.
class ChoiceMaster(models.Model):
    choice_name = models.CharField(max_length=20)
    choice_key = models.CharField(max_length=20)
    choice_value = models.CharField(max_length=20)
    choice_order = models.IntegerField()

    def __str__(self):
        return self.choice_name

    class Meta:
        db_table = "choicemaster"
        managed = True
        verbose_name = "choicemaster"
        verbose_name_plural = "choicemasters"
