from django.db import models


class MegaChoiceNames(models.Model):
    name = models.CharField(max_length=20)
    order = models.IntegerField(default=0)
    memo = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class MegaChoices(models.Model):
    name = models.ForeignKey(MegaChoiceNames, on_delete=models.CASCADE)
    c0 = models.CharField(max_length=20)
    c1 = models.CharField(max_length=20)
    c2 = models.CharField(max_length=20, null=True, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class MegaMenu(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200, null=True, blank=True)
    int_field = models.IntegerField(default=0)
    char_field = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class MegaMenuSub(models.Model):
    name = models.ForeignKey(MegaMenu, on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=20)
    url = models.CharField(max_length=100, null=True, blank=True)
    int_field = models.IntegerField(default=0)
    char_field = models.CharField(max_length=20, null=True, blank=True)
    orderx = models.IntegerField(default=0)
    ordery = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    css_class = models.CharField(max_length=40, null=True, blank=True)
    ajax_attr0 = models.CharField(max_length=20, null=True, blank=True)
    ajax_attr1 = models.CharField(max_length=20, null=True, blank=True)
    ajax_attr2 = models.CharField(max_length=20, null=True, blank=True)
    ajax_attr4 = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.sub_name
