from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from rapidsms.models import Backend

from afrims.apps.groups.utils import format_number

class ContactExtra(models.Model):
    """ Abstract model to extend the RapidSMS Contact model """

    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=64, blank=True)
    department = models.CharField(max_length=32, blank=True)

    #personal_group = models.ForeignKey("Groups",blank=False,null=False)
    # hoping in django 1.2 on_delete = CASCADE

    # personal_group
    # automatically created group : name (title, dept)
    def personal_group_name(self):
        # todo.low: generic create param str for array seems reasonable, remove all blank, if none, return blank
        # note: use str.format here based on recommendation from http://docs.python.org/release/2.6.7/tutorial/inputoutput.html#fancier-output-formatting
        # todo.low: update all str % to use str.format
        if self.title=='' and self.department=='':
            return '{0} {1}'.format(self.first_name,self.last_name)
        elif self.title!='' and self.department=='':
            return '{0} {1} ({2})'.format(self.first_name,self.last_name,self.title)
        elif self.title=='' and self.department!='':
            return '{0} {1} ({2})'.format(self.first_name,self.last_name,self.department)
        else:
            return '{0} {1} ({2},{3})'.format(self.first_name,self.last_name,self.title,self.department)

    def personal_group(self):
        pgroups = self.groups.filter(is_personal_group=True)
        if pgroups.count()==0:
            raise Exception("No personal group defined for contact %s" % self)
        if pgroups.count()>1:
            raise Exception("Unexpected error, %d personal groups for contact %s" % (pgroups.count(),self))
        return pgroups[0]

    def save(self, **kwargs):
        self.name = "%s %s" % (self.first_name, self.last_name)
        super(ContactExtra, self).save(**kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        from afrims.apps.groups.models import Group
            
        # super(ContactExtra,self).clean()
        # not clear if this is needed
        groups = Group.objects.filter(name=self.personal_group_name())
        if groups.count()>0:
            if groups.count()!=1:
                raise ValidationError("There are %d groups with the name %s. Please notify the administrator!" % groups.count(), self.personal_group_name())
            else:
                if groups[0].contacts.filter(id=self.id).count()==0:
                    # this belongs to someone else
                    raise ValidationError('Personal group name is not unique. Please add additional info to the firstname, lastname, title or department to uniquely identify this person!')

    class Meta:
        abstract = True

    @property
    def formatted_phone(self):
        return format_number(self.phone)

