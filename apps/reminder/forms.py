from django import forms
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import RadioSelect, HiddenInput

class ReminderForm(forms.Form):
    repeat_frequencies = (
                            ('hourly','hourly'),
                            ('daily','daily'),
                            ('weekly','weekly'),
                            ('monthly','monthly'),
                            ('yearly','yearly'),
                        )

    days_of_week = (
                    ('0','Monday'),
                    ('1','Tuesday'),
                    ('2','Wednesday'),
                    ('3','Thursday'),
                    ('4','Friday'),
                    ('5','Saturday'),
                    ('6','Sunday'),
                    )

    months_of_year = (
        ('*', 'Every month'),
        ('0', 'January'),
        ('1', 'February'),
        ('2', 'March'),
        ('3', 'April'),
        ('4', 'May'),
        ('5', 'June'),
        ('6', 'July'),
        ('7', 'August'),
        ('8', 'September'),
        ('9', 'October'),
        ('10', 'November'),
        ('11', 'December'),
    )

    reminder_event_type = (
        ('broadcast','Broadcast'),
        ('custom_broadcast','Custom Broadcast Message'),
    )

    description = forms.CharField(max_length=255, required=True)
    repeat_frequency = forms.ChoiceField(choices=repeat_frequencies, required=True)
    start_date = forms.DateTimeField(required = True, initial='Click to select...')
    end_date = forms.DateTimeField(required=False, initial='Click to select...')
    has_end_date = forms.BooleanField(label='No End Date')
    weekly_days = forms.MultipleChoiceField(choices=days_of_week, required=False)
    yearly_months = forms.MultipleChoiceField(choices=months_of_year, required=False,widget=forms.SelectMultiple(attrs={'multiple':'multiple'}))
    minutes = forms.CharField(max_length=255,widget=HiddenInput)
    hours = forms.CharField(max_length=255,widget=HiddenInput)
    days = forms.CharField(max_length=255,widget=HiddenInput)
    months = forms.CharField(max_length=255,widget=HiddenInput)
    event_type = forms.MultipleChoiceField(widget=RadioSelect, choices=reminder_event_type, label='Select Event Type')
