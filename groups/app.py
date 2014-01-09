from rapidsms.apps.base import AppBase
from rapidsms.models import Contact
from rapidsms.contrib.messagelog.models import Message

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
        if msg.contact and msg.contact.name:
            sender = msg.contact.name
        else:
            sender = msg.connection.identity
        text = "{0}: {1}".format(sender, msg.text)
        recipients = set([contact.default_connection
                         for contact in group.contacts.all()])
        recipients.discard(msg.connection)
        # respond to sender
        sender_text = "sent to {0} members of {1}".format(len(recipients),
                                                          "#" + group.slug)
        msg.respond(sender_text)
        # 'respond' to group members
        message = msg.respond(text, connections=list(recipients))
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
                # TODO this is very error-prone. need to have a `slug`
                # or `username` unique to each contact
                matches = Contact.objects.filter(name__istartswith=name)
                if len(matches) > 0:
                    contacts.append(matches[0])
            if set(contacts):
                recipients = [contact.default_connection
                              for contact in set(contacts)]
                if msg.contact and msg.contact.name:
                    sender = msg.contact.name
                else:
                    sender = msg.connection.identity
                text = "{0}: {1}".format(sender, msg.text)
                # 'respond' to recipients
                message = msg.respond(text, connections=list(recipients))
        if len(msg.responses) > 0:
            return True
