import logging

from django import forms

from rapidsms.models import Contact
from rapidsms.router import send

from groups.models import Group
from groups.models import GroupMessage


__all__ = ('GroupForm', 'ContactForm', 'ForwardingRuleFormset',)


logger = logging.getLogger('groups.forms')

contacts_queryset = Contact.objects.all().order_by('name')


class GroupForm(forms.ModelForm):
    objects = forms.ModelMultipleChoiceField(queryset=contacts_queryset,
                                             label='contacts', required=False)

    class Meta:
        model = Group
        exclude = ('is_editable', 'contacts')

    def save(self, commit=True):
        self.instance._pending = self.cleaned_data.get('objects')
        return super(GroupForm, self).save(commit=commit)


class ContactForm(forms.ModelForm):
    """ Form for managing contacts """
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.none())

    class Meta:
        model = Contact
        exclude = ('language', 'primary_backend', 'pin')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.pk:
            pks = instance.groups.values_list('pk', flat=True)
            kwargs['initial'] = {'groups': list(pks)}
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget = forms.CheckboxSelectMultiple()
        self.fields['groups'].queryset = Group.objects.order_by('name')
        self.fields['groups'].required = False
        self.fields['name'].required = True

    def save(self, commit=True):
        instance = super(ContactForm, self).save()
        instance.groups = self.cleaned_data['groups']
        return instance


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['message'].widget.attrs['placeholder'] = 'Message'

    def send(self, sender=None, group=None):
        message = self.cleaned_data['message']
        text = "{0}: {1}".format(sender, message)
        recipients = set([contact.default_connection
                         for contact in group.contacts.all()])
        sent = send(text, list(recipients))
        GroupMessage.objects.create(group=group,
                                    message=sent.logger_msg,
                                    num_recipients=len(recipients))
        return sent
