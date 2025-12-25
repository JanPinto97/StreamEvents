from djongo import models
from django.conf import settings
from django.utils.timesince import timesince

from events.models import Event


class ChatMessage(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_highlighted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']  # Més antic primer
        verbose_name = 'Missatge de Xat'
        verbose_name_plural = 'Missatges de Xat'

    def __str__(self):
        preview = (self.message or '')[:50]
        return f"{self.user.username}: {preview}"

    def can_delete(self, user):
        """
        Pot eliminar:
        - creador del missatge
        - creador de l'esdeveniment
        - staff
        """
        if not user or not getattr(user, 'is_authenticated', False):
            return False

        if getattr(user, 'is_staff', False):
            return True

        if user == self.user:
            return True

        if user == self.event.creator:
            return True

        return False

    def get_user_display_name(self):
        """
        Retorna display_name si existeix, sinó username.
        """
        display_name = getattr(self.user, 'display_name', None)
        if display_name:
            return display_name
        return self.user.username

    def get_time_since(self):
        """
        Retorna el temps transcorregut des de la creació.
        Ex: "fa 2 minuts", "fa 1 hora"
        """
        return f"fa {timesince(self.created_at)}"
