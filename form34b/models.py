from django.db import models


class Candidate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keyword = models.CharField(max_length=10, unique=True)
    party = models.CharField(max_length=100, unique=True)
    votes = models.IntegerField(null=True)
    votes_percentage = models.FloatField(null=True)

    def __str__(self):
        return self.name


class FormDetails(models.Model):
    county = models.CharField(max_length=100, unique=True)
    registered_voters = models.IntegerField()
    valid_votes = models.IntegerField()
    spoilt_votes = models.IntegerField()
    voter_turnout = models.FloatField(default=0.0,)
    odinga = models.IntegerField(default=0)
    ruto = models.IntegerField(default=0)
    wajackoyah = models.IntegerField(default=0)
    mweure = models.IntegerField(default=0)

    def __str__(self):
        return self.county

    def save(self, *args, **kwargs):
        self.voter_turnout = round(self.voter_turnout, 3)
        super(FormDetails, self).save(*args, **kwargs)


class TallyResults(models.Model):
    id = models.AutoField(primary_key=True)
    county = models.CharField(max_length=100, unique=True)
    odinga = models.IntegerField(default=0)
    ruto = models.IntegerField(default=0)
    wajackoyah = models.IntegerField(default=0)
    mweure = models.IntegerField(default=0)

    def __str__(self):
        return self.county
