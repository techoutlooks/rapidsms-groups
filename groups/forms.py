import logging
import re

from django import forms

from rapidsms.models import Contact

from groups.models import Group
from groups.utils import format_number
from groups.validators import validate_phone


__all__ = ('GroupForm', 'ContactForm', 'ForwardingRuleFormset',)


logger = logging.getLogger('groups.forms')


class FancyPhoneInput(forms.TextInput):

    def render(self, name, value, attrs=None):
        if value:
            value = format_number(value)
        return super(FancyPhoneInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        value = super(FancyPhoneInput, self).value_from_datadict(data,
                                                                 files, name)
        if value:
            value = re.sub(r'\D', '', value)
        return value

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
    phone = forms.CharField(validators=[validate_phone],
                            widget=FancyPhoneInput)

    class Meta:
        model = Contact
        exclude = ('language', 'name', 'primary_backend', 'pin')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and instance.pk:
            pks = instance.groups.values_list('pk', flat=True)
            kwargs['initial'] = {'groups': list(pks)}
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget = forms.CheckboxSelectMultiple()
        self.fields['groups'].queryset = Group.objects.order_by('name')
        self.fields['groups'].required = False
        for name in ('name',):
            self.fields[name].required = True

    def save(self, commit=True):
        instance = super(ContactForm, self).save()
        instance.groups = self.cleaned_data['groups']
        return instance
