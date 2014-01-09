#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.utils.text import slugify

from rapidsms.models import Contact
from rapidsms.contrib.messagelog.models import Message
from rapidsms import router

from objectset.models import ObjectSet


class Group(ObjectSet):
    """ Organize RapidSMS contacts into groups """
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    is_editable = models.BooleanField(default=True)

    contacts = models.ManyToManyField(Contact, related_name='groups',
                                      blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)

    @property
    def members(self):
        return len(self)


class GroupMessage(models.Model):
    group = models.ForeignKey(Group)
    message = models.ForeignKey(Message)
