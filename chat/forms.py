from django import forms
from .models import ChatMessage


class ChatMessageForm(forms.ModelForm):
    # Llista bàsica (pots ampliar-la). Millor en minúscules.
    PROHIBITED_WORDS = [
        "idiota",
        "imbecil",
        "gilipollas",
        "puta",
        "mierda",
        "cabron",
    ]

    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': "Escriu un missatge...",
            })
        }

    def clean_message(self):
        msg = self.cleaned_data.get('message', '')

        # 1) No buit després de strip
        msg_stripped = msg.strip()
        if not msg_stripped:
            raise forms.ValidationError("El missatge no pot estar buit.")

        # 2) Longitud màxima
        if len(msg_stripped) > 500:
            raise forms.ValidationError("El missatge no pot superar els 500 caràcters.")

        # 3) Paraules prohibides (detecció simple)
        lower = msg_stripped.lower()
        for bad in self.PROHIBITED_WORDS:
            if bad in lower:
                raise forms.ValidationError("El missatge conté paraules no permeses.")
        return msg_stripped
