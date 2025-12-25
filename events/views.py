from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, JsonResponse
from urllib.parse import unquote
from chat.forms import ChatMessageForm



from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm


def event_list_view(request):
    """
    Llistat d'esdeveniments amb:
    - paginació (12 per pàgina)
    - cerca i filtres amb EventSearchForm
    - destacats al principi
    """
    events = Event.objects.all()

    form = EventSearchForm(request.GET or None)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            events = events.filter(title__icontains=search)

        if category:
            events = events.filter(category=category)

        if status:
            events = events.filter(status=status)

        if date_from:
            events = events.filter(scheduled_date__date__gte=date_from)

        if date_to:
            events = events.filter(scheduled_date__date__lte=date_to)

    # Destacats primer, després per created_at (ja ve de Meta)
    events = events.order_by('-is_featured', '-created_at')

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'events': page_obj.object_list,
    }
    return render(request, 'events/event_list.html', context)


def event_detail_view(request, pk):
    """
    Vista de detall d'un esdeveniment.
    """
    event = get_object_or_404(Event, pk=pk)
    is_creator = request.user.is_authenticated and (request.user == event.creator)

    context = {
        'event': event,
        'is_creator': is_creator,
        'chat_form': ChatMessageForm(),
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            messages.success(request, "Esdeveniment creat correctament.")
            return redirect(event.get_absolute_url())
        else:
            messages.error(request, "Hi ha errors en el formulari. Revisa els camps.")
    else:
        form = EventCreationForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_update_view(request, pk):
    """
    Editar un esdeveniment existent.
    Només el creador pot editar.
    """
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.creator:
        messages.error(request, "No tens permís per editar aquest esdeveniment.")
        return redirect(event.get_absolute_url())

    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Esdeveniment actualitzat correctament.")
            return redirect(event.get_absolute_url())
        else:
            messages.error(request, "Hi ha errors en el formulari. Revisa els camps.")
    else:
        # Per al DateTimeInput amb type=datetime-local, pot ser que més endavant
        # vulguis adaptar el format, però de moment fem servir el valor per defecte.
        form = EventUpdateForm(instance=event, user=request.user)

    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_delete_view(request, pk):
    """
    Eliminar un esdeveniment.
    Només el creador pot eliminar.
    """
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.creator:
        messages.error(request, "No tens permís per eliminar aquest esdeveniment.")
        return redirect(event.get_absolute_url())

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Esdeveniment eliminat correctament.")
        return redirect('events:event_list')

    context = {
        'event': event,
    }
    return render(request, 'events/event_confirm_delete.html', context)


@login_required
def my_events_view(request):
    """
    Mostra només els esdeveniments creats per l'usuari actual.
    Filtres per estat via querystring (?status=live, etc.).
    """
    events = Event.objects.filter(creator=request.user)
    status_filter = request.GET.get('status')

    if status_filter:
        events = events.filter(status=status_filter)

    events = events.order_by('-created_at')

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'events': page_obj.object_list,
        'status_filter': status_filter,
    }
    return render(request, 'events/my_events.html', context)


def events_by_category_view(request, category):
    """
    Filtrar esdeveniments per categoria concreta.
    Si la categoria no existeix, 404.
    """
    valid_categories = dict(Event.CATEGORY_CHOICES).keys()
    if category not in valid_categories:
        raise Http404("Categoria no vàlida.")

    events = Event.objects.filter(category=category).order_by('-created_at')

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'events': page_obj.object_list,
    }
    return render(request, 'events/events_by_category.html', context)


def tag_cloud_view(request):
    """
    Mostra un 'núvol' d'etiquetes populars.
    """
    popular_tags = Event.get_popular_tags()  # [(tag, count), ...]

    if popular_tags:
        max_count = popular_tags[0][1]
    else:
        max_count = 0

    # Preparem pesos per la mida visual (1, 2, 3)
    tag_cloud = []
    for tag, count in popular_tags:
        if max_count <= 1:
            weight = 1
        else:
            ratio = count / max_count
            if ratio > 0.66:
                weight = 3
            elif ratio > 0.33:
                weight = 2
            else:
                weight = 1

        tag_cloud.append({
            'name': tag,
            'count': count,
            'weight': weight,
        })

    context = {
        'tag_cloud': tag_cloud,
    }
    return render(request, 'events/tag_cloud.html', context)


def events_by_tag_view(request, tag):
    """
    Mostra esdeveniments que contenen una etiqueta concreta.
    Coincidència exacta per etiqueta (case-insensitive).
    """
    # Descodifiquem per si hi ha espais, accents, etc.
    raw_tag = unquote(tag).lower().strip()

    if not raw_tag:
        raise Http404("Etiqueta no vàlida.")

    all_events = Event.objects.exclude(tags__isnull=True).exclude(tags__exact='')
    filtered_events = []

    for event in all_events:
        tags_lower = [t.lower() for t in event.get_tags_list()]
        if raw_tag in tags_lower:
            filtered_events.append(event)

    # Ordenar per data de creació (ja ve per Meta, però ho remarquem)
    filtered_events.sort(key=lambda e: e.created_at, reverse=True)

    paginator = Paginator(filtered_events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': raw_tag,
        'page_obj': page_obj,
        'events': page_obj.object_list,
    }
    return render(request, 'events/events_by_tag.html', context)


def tags_autocomplete_view(request):
    """
    Endpoint senzill per autocompletar etiquetes existents.
    Retorna JSON: { "results": ["tag1", "tag2", ...] }
    Pot ser consumit via fetch()/AJAX des del front.
    """
    query = request.GET.get('q', '').lower().strip()
    all_tags = Event.get_all_tags()

    if query:
        tags = [t for t in all_tags if query in t]
    else:
        tags = all_tags

    return JsonResponse({'results': tags})