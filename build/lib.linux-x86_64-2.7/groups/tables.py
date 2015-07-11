
from rapidsms.models import Contact
from .models import Group
from .models import GroupMessage
import django_tables2 as tables


class GroupTable(tables.Table):
    name = tables.LinkColumn('edit-group',
                             args=[tables.utils.A('pk')])
    id = tables.LinkColumn('edit-group',
                           args=[tables.utils.A('pk')])
    members = tables.LinkColumn('list-group-members',
                                args=[tables.utils.A('pk')])
    message_count = tables.LinkColumn('list-group-messages',
                                      verbose_name='messages',
                                      args=[tables.utils.A('pk')])

    class Meta:
        model = Group
        order_by = ('name')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }


class ContactTable(tables.Table):
    identities = tables.Column(empty_values=(), orderable=False)
    id = tables.LinkColumn('registration_contact_edit',
                           args=[tables.utils.A('pk')])

    class Meta:
        model = Contact
        order_by = ('id')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }

    def render_identities(self, value, record):
        return ', '.join([x.identity for x in record.connection_set.all()])


class GroupMessageTable(tables.Table):
    sender = tables.Column(accessor=tables.utils.A('message.who'),
                           verbose_name='sender')

    date = tables.DateTimeColumn(accessor=tables.utils.A('message.date'),
                                 verbose_name='date')

    message = tables.Column(accessor=tables.utils.A('message.text'))

    class Meta:
        model = GroupMessage
        order_by = ('date')
        exclude = ('id', 'group')
        sequence = ('date', 'sender', 'message', 'num_recipients')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }
