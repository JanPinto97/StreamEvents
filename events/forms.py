from datetime import datetime

from django import forms

from .models import Event, CATEGORY_CHOICES, STATUS_CHOICES


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'stream_url']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'gaming, chill, retro'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data['scheduled_date']
        if scheduled_date < datetime.now(scheduled_date.tzinfo):
            raise forms.ValidationError('La data programada no pot ser en el passat.')
        return scheduled_date

    def clean_title(self):
        title = self.cleaned_data['title']
        if self.user and Event.objects.filter(title=title, creator=self.user).exists():
            raise forms.ValidationError('Ja tens un esdeveniment amb aquest títol.')
        return title

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data['max_viewers']
        if max_viewers < 1 or max_viewers > 1000:
            raise forms.ValidationError("Els espectadors han d'estar entre 1 i 1000.")
        return max_viewers


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'status', 'stream_url']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.initial_status = self.instance.status if self.instance else None

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data['scheduled_date']
        if self.instance and self.instance.status == 'live' and scheduled_date != self.instance.scheduled_date:
            raise forms.ValidationError("No es pot canviar la data mentre l'esdeveniment està en directe.")
        if scheduled_date < datetime.now(scheduled_date.tzinfo):
            raise forms.ValidationError('La data programada no pot ser en el passat.')
        return scheduled_date

    def clean_status(self):
        status = self.cleaned_data['status']
        if self.instance and self.user and self.instance.creator != self.user:
            if status != self.instance.status:
                raise forms.ValidationError("Només el creador pot canviar l'estat.")
        return status

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data['max_viewers']
        if max_viewers < 1 or max_viewers > 1000:
            raise forms.ValidationError("Els espectadors han d'estar entre 1 i 1000.")
        return max_viewers


class EventSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Cerca')
    category = forms.ChoiceField(required=False, choices=[('all', 'Totes')] + CATEGORY_CHOICES)
    status = forms.ChoiceField(required=False, choices=[('all', 'Tots')] + STATUS_CHOICES)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
