from __future__ import print_function

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict

from rapidsms.models import Contact
from rapidsms.tests.harness.router import TestRouterMixin
from rapidsms.messages.incoming import IncomingMessage

from groups import forms as group_forms
from groups.app import GroupsApp
from groups.tests.base import CreateDataTest
from groups.utils import normalize_number


class GroupCreateDataTest(CreateDataTest):

    def create_contact(self, data={}):
        """ Override super's create_contact to include extension fields """
        defaults = self._data()
        defaults.update(data)
        return Contact.objects.create(**defaults)

    def _data(self, initial_data={}, instance=None):
        """ Helper function to generate form-like POST data """
        if instance:
            data = model_to_dict(instance)
        else:
            data = {
                'name': self.random_string(8),
            }
        data.update(initial_data)
        return data


class GroupFormTest(GroupCreateDataTest):

    def test_create_contact(self):
        """ Test contact creation functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        data = self._data({'groups': [group1.pk], 'name': 'alice'})
        form = group_forms.ContactForm(data)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.name, data['name'])
        self.assertEqual(contact.groups.count(), 1)
        self.assertTrue(contact.groups.filter(pk=group1.pk).exists())
        self.assertFalse(contact.groups.filter(pk=group2.pk).exists())

    def test_edit_contact(self):
        """ Test contact edit functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        contact = self.create_contact()
        contact.groups.add(group1)
        data = self._data({'groups': [group2.pk]}, instance=contact)
        form = group_forms.ContactForm(data, instance=contact)
        self.assertTrue(form.is_valid(), dict(form.errors))
        contact = form.save()
        self.assertEqual(contact.groups.count(), 1)
        self.assertFalse(contact.groups.filter(pk=group1.pk).exists())
        self.assertTrue(contact.groups.filter(pk=group2.pk).exists())


class GroupViewTest(CreateDataTest):

    def setUp(self):
        self.user = User.objects.create_user('test', 'a@b.com', 'abc')
        self.client.login(username='test', password='abc')

    def test_editable_views(self):
        group = self.create_group({'is_editable': False})
        edit_url = reverse('edit-group', args=[group.pk])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 403)
        delete_url = reverse('delete-group', args=[group.pk])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 403)


class PhoneTest(GroupCreateDataTest):

    def setUp(self):
        self.backend = self.create_backend(data={'name': 'test-backend'})
        self.router = TestRouterMixin()
        self.app = GroupsApp(router=self.router)

    def _send(self, conn, text):
        msg = IncomingMessage(conn, text)
        self.app.filter(msg)
        return msg

    def test_contact_association(self):
        number = normalize_number('13364130840', 'US')
        connection = self.create_connection({'backend': self.backend,
                                             'identity': number})
        contact = self.create_contact()
        connection.contact = contact
        connection.save()

        other_contact = self.create_contact()
        another_connection = self.create_connection({'backend': self.backend,
                                                     'identity': '3364130840'})
        msg = self._send([another_connection], 'test')
        self.assertEqual(msg.connections[0].contact, contact)
        self.assertNotEqual(msg.connections[0].contact, other_contact)
