from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django_tables2 import RequestConfig

from rapidsms.models import Contact
from rapidsms import settings

from groups.models import Group
from groups.forms import GroupForm
from groups.forms import ContactForm
from groups.forms import MessageForm
from .tables import GroupTable
from .tables import GroupMessageTable
from .tables import ContactTable


@login_required
def list_groups(request):
    groups_table = GroupTable(
        Group.objects.all(),
        template="django_tables2/bootstrap-tables.html")

    paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
    RequestConfig(request, paginate=paginate).configure(groups_table)

    return render(request, "groups/groups/list.html", {
        "groups_table": groups_table,
    })


@login_required
def list_group_members(request, group_id=None):
    if group_id:
        group = get_object_or_404(Group, pk=group_id)
        contacts_table = ContactTable(
            group.contacts,
            template="django_tables2/bootstrap-tables.html")

        paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
        RequestConfig(request, paginate=paginate).configure(contacts_table)

        return render(request, "groups/groups/list_members.html", {
            "contacts_table": contacts_table,
            "group": group,
        })


@login_required
def list_group_messages(request, group_id=None):
    if group_id:
        group = get_object_or_404(Group, pk=group_id)
        groups_messages = GroupMessageTable(
            group.messages,
            template="django_tables2/bootstrap-tables.html")

        paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
        RequestConfig(request, paginate=paginate).configure(groups_messages)

        return render(request, "groups/groups/list_messages.html", {
            "groups_messages": groups_messages,
            "group": group,
            "form": MessageForm(),
        })


@login_required
@require_POST
def send_group_message(request, group_id=None):
    try:
        if group_id:
            group = get_object_or_404(Group, pk=group_id)
            user = request.user.username

            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.send(sender=user, group=group)
                if len(message.connections) == 1:
                    return HttpResponse('Your message was sent'
                                        ' to 1 recipient.')
                else:
                    msg = 'Your message was sent to {0} ' \
                        'recipients.'.format(len(message.connections))
                    return HttpResponse(msg)
        else:
            return HttpResponseBadRequest(unicode(form.errors))
    except:
        return HttpResponse("Unable to send message.", status=500)


@login_required
@transaction.atomic
def create_edit_group(request, group_id=None):
    group = None
    if group_id:
        group = get_object_or_404(Group, pk=group_id)
        if not group.is_editable:
            return HttpResponseForbidden('Access denied')
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.info(request, 'Group saved successfully')
            return HttpResponseRedirect(reverse('list-groups'))
    else:
        if group:
            form = GroupForm(
                instance=group,
                initial={
                    'objects': group.contacts.all(),
                    'name': group.name,
                    'slug': group.slug,
                    'description': group.description})
        else:
            form = GroupForm()
    return render(request, 'groups/groups/create_edit.html', {
        'form': form,
        'group': group,
    })


@login_required
@transaction.atomic
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not group.is_editable:
        return HttpResponseForbidden('Access denied')
    if request.method == 'POST':
        group.delete()
        messages.info(request, 'Group successfully deleted')
        return HttpResponseRedirect(reverse('list-groups'))
    return render(request, 'groups/groups/delete.html', {
        'group': group,
    })


@login_required
def list_contacts(request):
    contacts = Contact.objects.all().order_by('name')
    return render(request, 'groups/contacts/list.html', {
        'contacts': contacts,
    })


@login_required
@transaction.atomic
def create_edit_contact(request, contact_id=None):
    contact = None
    if contact_id:
        contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.info(request, 'Contact saved successfully')
            return HttpResponseRedirect(reverse('list-contacts'))
    else:
        form = ContactForm(instance=contact)
    return render(request, 'groups/contacts/create_edit.html', {
        'form': form,
        'contact': contact,
    })


@login_required
@transaction.atomic
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        contact.delete()
        messages.info(request, 'Contact successfully deleted')
        return HttpResponseRedirect(reverse('list-contacts'))
    return render(request, 'groups/contacts/delete.html', {
        'contact': contact,
    })
