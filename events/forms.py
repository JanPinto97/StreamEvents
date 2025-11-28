from django import forms
from django.utils import timezone
from .models import Event
from urllib.parse import urlparse

class EventCreationForm(forms.ModelForm):
    """Formulari per crear un nou esdeveniment."""

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Text d'ajuda per al camp stream_url
        self.fields['stream_url'].help_text = (
            "Introdueix una URL de streaming (YouTube, Twitch, Vimeo o altra plataforma embeddable). "
            "Exemples: https://youtu.be/..., https://www.youtube.com/watch?v=..., "
            "https://www.twitch.tv/elmeucanal, https://vimeo.com/123456789"
        )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'category',
            'scheduled_date',
            'thumbnail',
            'max_viewers',
            'tags',
            'stream_url',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple: música, gaming, educació'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'max_viewers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000
            }),
            'stream_url': forms.URLInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        user = self.request_user

        if user is not None and title:
            exists = Event.objects.filter(
                creator=user,
                title__iexact=title
            ).exists()
            if exists:
                raise forms.ValidationError(
                    "Ja tens un esdeveniment amb aquest títol. Tria un altre nom."
                )
        return title

    def clean_scheduled_date(self):
        scheduled = self.cleaned_data['scheduled_date']

        # Fem la data aware si cal
        if timezone.is_naive(scheduled):
            scheduled = timezone.make_aware(scheduled, timezone.get_current_timezone())

        if scheduled < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")
        return scheduled

    def clean_max_viewers(self):
        maxv = self.cleaned_data['max_viewers']
        if maxv < 1 or maxv > 1000:
            raise forms.ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        return maxv

    def clean_stream_url(self):
        url = self.cleaned_data.get('stream_url', '').strip()
        if not url:
            return url  # opcional, no és obligatori

        parsed = urlparse(url)

        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise forms.ValidationError(
                "Introdueix una URL vàlida que comenci per http:// o https://."
            )

        # Valorem que com a mínim sigui un domini raonable
        host = parsed.netloc.lower()
        allowed_keywords = ['youtube.', 'youtu.be', 'twitch.tv', 'vimeo.com']

        if not any(k in host for k in allowed_keywords):
            # No la bloquegem, però avisem de forma suau
            # (podries fer un warning via messages, però aquí fem un error lleu).
            raise forms.ValidationError(
                "Aquesta URL no sembla ser de YouTube, Twitch o Vimeo. "
                "Assegura't que la plataforma permet inserció en iframe."
            )

        return url


class EventUpdateForm(forms.ModelForm):
    """Formulari per editar un esdeveniment existent."""

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['stream_url'].help_text = (
            "Introdueix una URL de streaming (YouTube, Twitch, Vimeo o altra plataforma embeddable)."
        )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'category',
            'scheduled_date',
            'thumbnail',
            'max_viewers',
            'tags',
            'status',
            'stream_url',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_status(self):
        status = self.cleaned_data['status']
        event = self.instance

        if self.request_user != event.creator:
            raise forms.ValidationError("Només el creador pot canviar l'estat de l'esdeveniment.")

        return status

    def clean_scheduled_date(self):
        new_date = self.cleaned_data['scheduled_date']
        event = self.instance

        if event.status == 'live':
            raise forms.ValidationError("No es pot canviar la data d'un esdeveniment que està en directe.")

        return new_date

    def clean_stream_url(self):
        url = self.cleaned_data.get('stream_url', '').strip()
        if not url:
            return url

        parsed = urlparse(url)

        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            raise forms.ValidationError(
                "Introdueix una URL vàlida que comenci per http:// o https://."
            )

        host = parsed.netloc.lower()
        allowed_keywords = ['youtube.', 'youtu.be', 'twitch.tv', 'vimeo.com']

        if not any(k in host for k in allowed_keywords):
            raise forms.ValidationError(
                "Aquesta URL no sembla ser de YouTube, Twitch o Vimeo. "
                "Assegura't que la plataforma permet inserció en iframe."
            )

        return url


class EventSearchForm(forms.Form):
    """Formulari per buscar i filtrar esdeveniments."""

    search = forms.CharField(
        required=False,
        label='Buscar',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cerca per títol...'})
    )

    category = forms.ChoiceField(
        required=False,
        choices=[('', 'Totes')] + Event.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tots')] + Event.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
