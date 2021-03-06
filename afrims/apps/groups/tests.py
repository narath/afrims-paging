from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
import re

from rapidsms.models import Contact, Backend, Connection
from rapidsms.tests.harness import MockRouter
from rapidsms.messages.incoming import IncomingMessage

from afrims.tests.testcases import CreateDataTest, patch_settings, \
                                   TabPermissionsTest

from afrims.apps.groups.models import Group
from afrims.apps.groups import forms as group_forms
from afrims.apps.groups.validators import validate_phone
from afrims.apps.groups.app import GroupsApp


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
                'first_name': self.random_string(8),
                'last_name': self.random_string(8),
                'email': 'test@abc.com',
                'phone': '+31112223333',
                'title' : 'Resident',
                'department' : 'Medicine',
            }
        data.update(initial_data)
        return data


class GroupTabsTest(TabPermissionsTest):
    """ Test people and group tab permissions"""

    def test_group_view_no_permissions(self):
        """ Test group view tab without permission redirects """
        self.check_without_perms(reverse('list-groups'), 'can_use_groups_tab')

    def test_people_tab_with_perms(self):
        """ Test people view tab with permission works """
        self.check_with_perms(reverse('list-contacts'), 'can_use_people_tab')

    def test_people_tab_without_perms(self):
        """ Test people view tab without permission redirects """
        self.check_without_perms(reverse('list-contacts'), 'can_use_people_tab')

class GroupFormTest(GroupCreateDataTest):

    def test_create_contact(self):
        """ Test contact creation functionality with form """
        group1 = self.create_group()
        self.assertFalse(group1.is_personal_group)
        group2 = self.create_group()
        data = self._data({'groups': [group1.pk]})
        form = group_forms.ContactForm(data)
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.first_name, data['first_name'])
        self.assertEqual(contact.groups.count(), 2) # remember user always has a personal group
        self.assertTrue(contact.groups.filter(pk=group1.pk).exists())
        self.assertFalse(contact.groups.filter(pk=group2.pk).exists())

        # make sure the personal group has been created
        self.assertTrue(contact.groups.filter(name=contact.personal_group_name()).exists())

        # cannot create contact with same personal group
        dup_contact_data = {
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'email': 'test@abc.com',
                'phone': '+31112223333',
                'title' : 'Resident',
                'department' : 'Medicine',
        }
        contact2 = Contact(**dup_contact_data)
        try:
            contact2.clean()
            self.assertFalse(True,"Expected ValidationError for contact with same personal group name")
        except ValidationError:
            # expected
            print "expected this error"
        
    def test_edit_contact(self):

        """ Test contact edit functionality with form """
        group1 = self.create_group()
        group2 = self.create_group()
        contact = self.create_contact()
        pg_name_orig = contact.personal_group().name
        contact.groups.add(group1)
        data = self._data({'groups': [group2.pk], 'first_name':'Roger'}, instance=contact)
        form = group_forms.ContactForm(data, instance=contact)
        self.assertTrue(form.is_valid(), dict(form.errors))
        contact = form.save()
        self.assertEqual(contact.groups.count(), 2) # remember always has a personal group as well
        self.assertFalse(contact.groups.filter(pk=group1.pk).exists())
        self.assertTrue(contact.groups.filter(pk=group2.pk).exists())
        self.assertEqual(contact.personal_group().name,contact.personal_group_name())
        self.assertNotEqual(contact.personal_group().name,pg_name_orig)


    def test_no_subjects(self):
        """New contacts cannot be added to the subjects group"""

        subjects_group, _ = Group.objects.get_or_create(name=settings.DEFAULT_SUBJECT_GROUP_NAME)
        data = self._data({'groups': [subjects_group.pk]})
        form = group_forms.ContactForm(data)
        self.assertFalse(form.is_valid())

    def test_delete_personal_group(self):
        """When a contact is deleted the personal group should be deleted as well"""
        contact = self.create_contact()
        pg = contact.personal_group()
        self.assertTrue(Group.objects.filter(pk=pg.pk).exists())
        contact.delete()
        self.assertFalse(Contact.objects.filter(pk=contact.pk).exists())
        self.assertFalse(Group.objects.filter(pk=pg.pk).exists())

    def test_cleaner_personal_group_name(self):
        PERSONAL_GROUP_WITH_TITLE_AND_DEPT = r'\w+\s\w+\s\(\w+,\w+\)'
        PERSONAL_GROUP_WITH_TITLE = r'\w+\s\w+\s\(\w+\)'
        PERSONAL_GROUP_WITH_DEPT = r'\w+\s\w+\s\(\w+\)'
        PERSONAL_GROUP_NO_TITLE_OR_DEPT = r'\w+\s\w+'

        contact = self.create_contact()
        self.assertNotEqual(contact.title,'')
        self.assertNotEqual(contact.department,'')
        self.assertTrue(re.match(PERSONAL_GROUP_WITH_TITLE_AND_DEPT,contact.personal_group_name()))

        save_title = contact.title
        contact.title = ''
        self.assertEqual(contact.title,'')
        self.assertNotEqual(contact.department,'')
        self.assertTrue(re.match(PERSONAL_GROUP_WITH_TITLE,contact.personal_group_name()))

        contact.title = save_title
        contact.department = ''
        self.assertNotEqual(contact.title,'')
        self.assertEqual(contact.department,'')
        self.assertTrue(re.match(PERSONAL_GROUP_WITH_DEPT,contact.personal_group_name()))

        contact.title = ''
        self.assertEqual(contact.title,'')
        self.assertEqual(contact.department,'')
        self.assertTrue(re.match(PERSONAL_GROUP_NO_TITLE_OR_DEPT,contact.personal_group_name()))
        


class GroupViewTest(CreateDataTest):

    def setUp(self):
        self.user = User.objects.create_user('test', 'a@b.com', 'abc')
        perm = Permission.objects.get(codename='can_use_groups_tab')
        self.user.user_permissions.add(perm)
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
        self.router = MockRouter()
        self.app = GroupsApp(router=self.router)

    def test_valid_phone(self):
        valid_numbers = ('12223334444', '112223334444', '1112223334444')
        for number in valid_numbers:
            self.assertEqual(None, validate_phone(number))       

    def test_invalid_phone(self):
        invalid_numbers = ('2223334444', '11112223334444')
        for number in invalid_numbers:
            self.assertRaises(ValidationError, validate_phone, number)

    def _send(self, conn, text):
        msg = IncomingMessage(conn, text)
        self.app.filter(msg)
        return msg

    def test_normalize_number(self):
        """
        All numbers should be stripped of non-numeric characters and, if
        defined, should be prepended with the COUNTRY_CODE
        """
        normalized = '+12223334444'
        number = '1-222-333-4444'
        self.assertEqual(self.app._normalize_number(number), normalized)
        number = '1 (222) 333-4444'
        self.assertEqual(self.app._normalize_number(number), normalized)
        with patch_settings(COUNTRY_CODE='66', INTERNATIONAL_DIALLING_CODE='+'):
            normalized = '+662223334444'
            number = '22-23334444'
            self.assertEqual(self.app._normalize_number(number), normalized)
        with patch_settings(COUNTRY_CODE=None):
            normalized = '2223334444'
            number = '22-23334444'
            self.assertEqual(self.app._normalize_number(number), normalized)

    def test_contact_association(self):
        number = '1112223334444'
        contact = self.create_contact({'phone': number})
        other_contact = self.create_contact()
        connection = self.create_connection({'backend': self.backend,
                                             'identity': '+111-222-333-4444'})
        msg = self._send(connection, 'test')
        self.assertEqual(msg.connection.contact_id, contact.id)
        self.assertNotEqual(msg.connection.contact_id, other_contact.id)
