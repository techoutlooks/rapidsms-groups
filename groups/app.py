from rapidsms.apps.base import AppBase
from rapidsms.models import Contact
from rapidsms.contrib.messagelog.models import Message
from rapidsms import router

from groups.utils import normalize_number
from .models import Group
from .models import GroupMessage


class GroupsApp(AppBase):

    def _associate_contact(self, connection):
        normalized_number = normalize_number(connection.identity)
        self.debug('Normalized number: {0}'.format(normalized_number))
        try:
            contact = Contact.objects.get(connection=normalized_number)
        except Contact.DoesNotExist:
            self.debug('Failed to find matching contact')
            contact = None
        if contact:
            self.debug('Associating connection to {0}'.format(contact))
            connection.contact = contact
            connection.save()

    def filter(self, msg):
        if not msg.connection.contact:
            self.debug('Found {0} without contact'.format(msg.connection))
            self._associate_contact(msg.connection)

    def _send_to_group(self, group, msg):
        if msg.contact is None:
            msg.respond('sorry you must be registered to message groups')
        if msg.contact not in group:
            msg.respond('sorry you must be a member of the group')
        sender = msg.contact.name or msg.contact.default_connection.identity
        text = "{0}: {1}".format(sender, msg.text)
        recipients = set([contact.default_connection
                         for contact in group.contacts.all()])
        recipients.discard(msg.contact.default_connection)
        # respond to sender
        sender_text = "sent to {0} members of {1}".format(len(recipients),
                                                          "#" + group.slug)
        msg.respond(sender_text)
        # 'respond' to group members
        message = msg.respond(text, connections=recipients)
        if message is not None:
            if msg.logger_msg is not None and\
               msg.logger_msg.direction == Message.INCOMING:
                GroupMessage.objects.create(group=group,
                                            message=msg.logger_msg)

    def handle(self, msg):
        groups = []
        mentions = []
        for token in msg.text.split():
            if token.startswith("#"):
                groups.append(token[1:])
            if token.startswith("@"):
                mentions.append(token[1:])
        if set(groups):
            for slug in set(groups):
                group = Group.objects.get(slug=slug)
                self._send_to_group(group, msg)
        if set(mentions):
            contacts = []
            for name in set(mentions):
                contact = Contact.objects.get(name=name)
                if contact:
                    contacts.append(contact)
            if set(contacts):
                recipients = [contact.default_connection
                              for contact in set(contacts)]
                text = "{0}: {1}".format(msg.contact.name, msg.text)

                router.send(text, recipients)
        if len(msg.responses) > 0:
            return True
