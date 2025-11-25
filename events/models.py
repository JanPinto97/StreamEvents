from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.db import models
from django.urls import reverse

CATEGORY_CHOICES = [
    ('gaming', 'Gaming'),
    ('music', 'Música'),
    ('talk', 'Xerrades'),
    ('education', 'Educació'),
    ('sports', 'Esports'),
    ('entertainment', 'Entreteniment'),
    ('technology', 'Tecnologia'),
    ('art', 'Art i Creativitat'),
    ('other', 'Altres'),
]

STATUS_CHOICES = [
    ('scheduled', 'Programat'),
    ('live', 'En Directe'),
    ('finished', 'Finalitzat'),
    ('cancelled', 'Cancel·lat'),
]


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True)
    max_viewers = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True)
    stream_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.pk])

    @property
    def is_live(self):
        return self.status == 'live'

    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date > datetime.now(self.scheduled_date.tzinfo)

    def get_duration(self):
        category_durations = {
            'gaming': 180,
            'music': 90,
            'talk': 60,
            'education': 120,
            'sports': 150,
            'entertainment': 120,
            'technology': 90,
            'art': 120,
            'other': 90,
        }
        if self.status != 'finished':
            return None
        minutes = category_durations.get(self.category)
        return timedelta(minutes=minutes) if minutes else None

    def get_tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def get_stream_embed_url(self):
        if not self.stream_url:
            return ''
        parsed = urlparse(self.stream_url)
        hostname = parsed.hostname or ''
        if 'youtube' in hostname or 'youtu.be' in hostname:
            video_id = ''
            if parsed.path == '/watch':
                video_id = parse_qs(parsed.query).get('v', [''])[0]
            elif parsed.hostname == 'youtu.be':
                video_id = parsed.path.lstrip('/')
            elif 'youtube' in hostname and parsed.path.startswith('/embed/'):
                video_id = parsed.path.split('/')[-1]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        if 'twitch.tv' in hostname:
            channel = parsed.path.lstrip('/')
            if channel:
                return f"https://player.twitch.tv/?channel={channel}&parent=localhost"
        return self.stream_url
