# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out


def add_key_ring_to_session(sender, request, user, **kwargs):
    print "#################request", request
    print "#################request.POST", request.POST
    print "#################request.GET", request.GET
    

def remove_key_ring_from_session(sender, request, user, **kwargs):
    pass


user_logged_in.connect(add_key_ring_to_session)
user_logged_out.connect(remove_key_ring_from_session)



class UserProfile(models.Model):
    """
    Benutzerdaten.
    """
    
    user = models.ForeignKey(User, unique=True, related_name="user_profile", verbose_name="User")
    #user = models.OneToOneField(User)
    rest_id = models.BigIntegerField("REST ID", unique=True)
    
    #company = models.CharField("Firmenname", max_length=50, blank=True, null=True)
    #address = models.CharField("Adresse", max_length=50, blank=True, null=True)
    #zip_code = models.CharField("PLZ", max_length=10, blank=True, null=True)
    #location = models.CharField("Ort", max_length=50, blank=True, null=True)
    #country = models.ForeignKey(Country, blank=True, null=True, verbose_name="Land")
    #date_of_birth = models.DateField("Geburtsdatum", blank=True, null=True)
    #phone_number = models.CharField("Telefonnummer", max_length=20, blank=True, null=True)
    #newsletter = models.NullBooleanField("Newsletter", blank=True)
    #password_raw = models.CharField("Passwort", max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = u"User Profile"
        verbose_name_plural = u"User Profiles"
        ordering = ('user', )
    
    def __unicode__(self):
        return u"%s" % self.user.username


#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        UserProfile.objects.create(user=instance)
#
#
#post_save.connect(create_user_profile, sender=User)