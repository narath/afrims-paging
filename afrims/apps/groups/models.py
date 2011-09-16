from django.db import models

from rapidsms.models import Contact

import logging
logger = logging.getLogger('afrims.apps.groups.models')


class Group(models.Model):
    """ Organize RapidSMS contacts into groups """

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    is_editable = models.BooleanField(default=True)
    is_personal_group = models.BooleanField(default=False)

    contacts = models.ManyToManyField(Contact, related_name='groups',
                                      blank=True)

    class Meta:
        permissions = (
            ("can_use_dashboard_tab", "Can use Dashboard tab"),
            ("can_use_send_a_message_tab", "Can use Send a Message tab"),
            ("can_use_appointment_reminders_tab", "Can use Appointment Reminders tab"),
            ("can_use_forwarding_tab", "Can use Forwarding tab"),
            ("can_use_groups_tab", "Can use Groups tab"),
            ("can_use_people_tab", "Can use People tab"),
            ("can_use_settings_tab", "Can use Settings tab"), # not implemented
        )

    def __unicode__(self):
        return self.name



from django.db.models.signals import post_save, post_delete

def contact_post_save(sender, **kwargs):
    c = kwargs['instance']
    logger.debug("post_save for contact %s\n" % c.name)
    g_name = c.personal_group_name()
    # does this personal group exist already
    p_groups = c.groups.filter(is_personal_group=True)
    if p_groups.count()==1:
        pg = p_groups[0]
        if pg.name != g_name:
            logger.debug("Updating personal group name from %s to %s \n" % (pg.name,g_name))
            pg.name = g_name
            pg.save()
    else:
        # group does not exist
        g = c.groups.create(name=g_name, is_personal_group=True)
        g.save()
        logger.debug("Created personal group %s \n" % g)
post_save.connect(contact_post_save, sender=Contact)

def contact_post_delete(sender, **kwargs):
    c = kwargs['instance']
    logger.debug("post_delete for contact %s \n" % c.name)
    # the record has been deleted already, so the m2m join records have been deleted
    # so we just remove the personal group by searching the groups
    p_groups = Group.objects.filter(name=c.personal_group_name(),is_personal_group=True)
    if p_groups.count()!=1:
        logger.warning("Unexpected error: %d personal groups when deleting contact personal group %s" % (p_groups.count(),c.personal_group_name()))
    p_groups.delete()
post_delete.connect(contact_post_delete, sender=Contact)

    