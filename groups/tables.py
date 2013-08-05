
from rapidsms.models import Contact
from .models import Group
import django_tables2 as tables


class GroupTable(tables.Table):
    name = tables.LinkColumn('edit-group',
                             args=[tables.utils.A('pk')])
    id = tables.LinkColumn('edit-group',
                           args=[tables.utils.A('pk')])
    members = tables.LinkColumn('list-group-members',
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
