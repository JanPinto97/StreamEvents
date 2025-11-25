from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EventCreationForm, EventSearchForm, EventUpdateForm
from .models import Event, CATEGORY_CHOICES


def event_list_view(request):
    events = Event.objects.all().order_by('-is_featured', '-created_at')
    form = EventSearchForm(request.GET or None)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            events = events.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__icontains=search)
            )
        if category and category != 'all':
            events = events.filter(category=category)
        if status and status != 'all':
            events = events.filter(status=status)
        if date_from:
            events = events.filter(scheduled_date__date__gte=date_from)
        if date_to:
            events = events.filter(scheduled_date__date__lte=date_to)

    featured_events = events.filter(is_featured=True)[:4]

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'events/event_list.html',
        {
            'page_obj': page_obj,
            'form': form,
            'featured_events': featured_events,
        },
    )


def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            messages.success(request, 'Esdeveniment creat correctament!')
            return redirect(event.get_absolute_url())
    else:
        form = EventCreationForm(user=request.user)
    return render(request, 'events/event_form.html', {'form': form, 'is_create': True})


@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.creator != request.user:
        return HttpResponseForbidden('No tens permís per editar aquest esdeveniment.')
    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Esdeveniment actualitzat!')
            return redirect(event.get_absolute_url())
    else:
        form = EventUpdateForm(instance=event, user=request.user)
    return render(request, 'events/event_form.html', {'form': form, 'event': event, 'is_create': False})


@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.creator != request.user:
        return HttpResponseForbidden('No tens permís per eliminar aquest esdeveniment.')
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Esdeveniment eliminat correctament.')
        return redirect('events:event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def my_events_view(request):
    events = Event.objects.filter(creator=request.user).order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        events = events.filter(status=status_filter)
    return render(request, 'events/my_events.html', {'events': events, 'status_filter': status_filter})


def events_by_category_view(request, category):
    valid_categories = [choice[0] for choice in CATEGORY_CHOICES]
    if category not in valid_categories:
        raise Http404('Categoria no vàlida')
    events = Event.objects.filter(category=category)
    paginator = Paginator(events.order_by('-is_featured', '-created_at'), 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'events/event_list.html',
        {
            'page_obj': page_obj,
            'form': EventSearchForm(),
            'category_filter': category,
            'featured_events': events.filter(is_featured=True)[:4],
        },
    )
