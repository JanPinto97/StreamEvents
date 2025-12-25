from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from events.models import Event
from .models import ChatMessage
from .forms import ChatMessageForm


def _serialize_message(msg, request_user):
    """
    Converteix un ChatMessage a dict (format requerit a l'enunciat).
    """
    return {
        "id": str(msg.id),
        "user": msg.user.username,
        "display_name": msg.get_user_display_name(),
        "message": msg.message,
        "created_at": msg.get_time_since(),
        "can_delete": msg.can_delete(request_user),
        "is_highlighted": msg.is_highlighted,
    }


@login_required
@require_POST
def chat_send_message(request, event_pk):
    """
    Enviar missatge (JSON).
    - Event ha d'existir
    - Només si event.status == 'live'
    - Validar amb ChatMessageForm
    """
    event = get_object_or_404(Event, pk=event_pk)

    if event.status != 'live':
        return JsonResponse({
            "success": False,
            "errors": {"__all__": ["El xat només està disponible durant l'esdeveniment en directe."]}
        }, status=403)

    form = ChatMessageForm(request.POST)

    if form.is_valid():
        msg = form.save(commit=False)
        msg.user = request.user
        msg.event = event
        msg.save()

        return JsonResponse({
            "success": True,
            "message": _serialize_message(msg, request.user)
        })

    # Errors del form en format senzill
    errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
    return JsonResponse({
        "success": False,
        "errors": errors
    }, status=400)


def chat_load_messages(request, event_pk):
    """
    Carregar missatges (JSON).
    - Event ha d'existir
    - Filtra: event, is_deleted=False (per Djongo fem exclude(True))
    - Ordena per created_at
    - Limita a 50
    """
    event = get_object_or_404(Event, pk=event_pk)

    # Djongo 1.3.6 peta amb NOT is_deleted -> filtrem a Python
    qs = ChatMessage.objects.filter(event=event).order_by('created_at')
    msgs = [m for m in list(qs) if not m.is_deleted]
    msgs = msgs[-50:]

    messages = [_serialize_message(m, request.user) for m in msgs]
    return JsonResponse({"messages": messages})



@login_required
@require_POST
def chat_delete_message(request, message_pk):
    """
    Soft delete (JSON).
    - Només si can_delete(request.user)
    """
    msg = get_object_or_404(ChatMessage, pk=message_pk)

    if not msg.can_delete(request.user):
        return JsonResponse({
            "success": False,
            "error": "No tens permís per eliminar aquest missatge."
        }, status=403)

    msg.is_deleted = True
    msg.save(update_fields=['is_deleted'])

    return JsonResponse({"success": True})


@login_required
@require_POST
def chat_highlight_message(request, message_pk):
    """
    BONUS: destacar missatge (toggle).
    - Només el creador de l'esdeveniment pot destacar
    """
    msg = get_object_or_404(ChatMessage, pk=message_pk)

    if request.user != msg.event.creator and not request.user.is_staff:
        return JsonResponse({
            "success": False,
            "error": "Només el creador de l'esdeveniment pot destacar missatges."
        }, status=403)

    msg.is_highlighted = not msg.is_highlighted
    msg.save(update_fields=['is_highlighted'])

    return JsonResponse({
        "success": True,
        "is_highlighted": msg.is_highlighted
    })
