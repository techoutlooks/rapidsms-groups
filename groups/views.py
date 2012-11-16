from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from rapidsms.models import Contact

from .models import Group
from .forms import GroupForm, ContactForm


@login_required
def list_groups(request):
    groups = Group.objects.annotate(count=Count('contacts'))
    context = {
        'groups': groups.order_by('name'),
    }
    return render(request, 'groups/groups/list.html', context)


@login_required
@transaction.commit_on_success
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
            messages.info(request, "Group saved successfully")
            return HttpResponseRedirect(reverse('list-groups'))
    else:
        form = GroupForm(instance=group)
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'groups/groups/create_edit.html', context)


@login_required
@transaction.commit_on_success
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not group.is_editable:
        return HttpResponseForbidden('Access denied')
    if request.method == 'POST':
        group.delete()
        messages.info(request, 'Group successfully deleted')
        return HttpResponseRedirect(reverse('list-groups'))
    context = {'group': group}
    return render(request, 'groups/groups/delete.html', context)


@login_required
def list_contacts(request):
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts.order_by('name'),
    }
    return render(request, 'groups/contacts/list.html', context)


@login_required
@transaction.commit_on_success
def create_edit_contact(request, contact_id=None):
    contact = None
    if contact_id:
        contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.info(request, "Contact saved successfully")
            return HttpResponseRedirect(reverse('list-contacts'))
    else:
        form = ContactForm(instance=contact)
    context = {
        'form': form,
        'contact': contact,
    }
    return render(request, 'groups/contacts/create_edit.html', context)


@login_required
@transaction.commit_on_success
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id)
    if request.method == 'POST':
        contact.delete()
        messages.info(request, 'Contact successfully deleted')
        return HttpResponseRedirect(reverse('list-contacts'))
    context = {'contact': contact}
    return render(request, 'groups/contacts/delete.html', context)
