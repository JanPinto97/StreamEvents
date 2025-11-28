from djongo import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from PIL import Image
from collections import Counter




class Event(models.Model):
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

    # Durades estimades per categoria (en minuts)
    category_durations = {
        'gaming': 180,        # 3 hores
        'music': 90,          # 1.5 hores
        'talk': 60,           # 1 hora
        'education': 120,     # 2 hores
        'sports': 150,        # 2.5 hores
        'entertainment': 120, # 2 hores
        'technology': 90,     # 1.5 hores
        'art': 120,           # 2 hores
        'other': 90,          # 1.5 hores
    }

    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
    )
    scheduled_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
    )
    thumbnail = models.ImageField(
        upload_to='events/thumbnails/',
        blank=True,
        null=True,
    )
    max_viewers = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    stream_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
    )
    
    @classmethod
    def update_statuses(cls):
        """
        Actualitza automàticament els estats dels esdeveniments.
        - scheduled -> live quan arriba l'hora programada
        - live -> finished quan ha passat la durada estimada
        """
        now = timezone.now()

        # 1) Programats que ja haurien d'estar en directe
        scheduled_qs = cls.objects.filter(
            status='scheduled',
            scheduled_date__lte=now,
        )
        scheduled_updated = scheduled_qs.update(status='live')

        # 2) En directe que ja haurien d'haver acabat (opcional però útil)
        live_events = cls.objects.filter(status='live')

        finished_count = 0
        for event in live_events:
            duration_minutes = cls.category_durations.get(event.category, 90)
            end_time = event.scheduled_date + timezone.timedelta(minutes=duration_minutes)
            if end_time <= now:
                event.status = 'finished'
                event.save(update_fields=['status'])
                finished_count += 1

        return scheduled_updated, finished_count
    
    @classmethod
    def get_all_tags(cls):
        """
        Retorna una llista d'etiquetes úniques (en minúscules) existents a tots els esdeveniments.
        """
        all_tags = []

        qs = cls.objects.exclude(tags__isnull=True).exclude(tags__exact='')
        for event in qs:
            all_tags.extend([t.lower() for t in event.get_tags_list()])

        # Úniques, ordenades alfabèticament
        return sorted(set(all_tags))

    @classmethod
    def get_popular_tags(cls):
        """
        Retorna una llista de (tag, count) ordenada per ús descendent.
        Serveix per al núvol d'etiquetes.
        """
        all_tags = []

        qs = cls.objects.exclude(tags__isnull=True).exclude(tags__exact='')
        for event in qs:
            all_tags.extend([t.lower() for t in event.get_tags_list()])

        counter = Counter(all_tags)
        # Llista de tuples (tag, count), més freqüents primer
        return counter.most_common()
    
    def save(self, *args, **kwargs):
        """Guarda l'esdeveniment i redimensiona el thumbnail si cal."""
        super().save(*args, **kwargs)

        if self.thumbnail:
            try:
                img = Image.open(self.thumbnail.path)
            except (FileNotFoundError, ValueError, OSError):
                return  # Si hi ha algun problema obrint la imatge, no fem res

            # Mida màxima (ample, alt) en píxels
            max_size = (800, 800)
            img.thumbnail(max_size)

            # Si és amb canal alfa, la passem a RGB
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Guardem optimitzant una mica la qualitat
            img.save(self.thumbnail.path, quality=85, optimize=True)
    
    class Meta:
        ordering = ['-created_at']  # Més recents primer
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # URL per veure el detall de l'esdeveniment
        return reverse('events:event_detail', args=[str(self.pk)])

    @property
    def is_live(self):
        # True si està en directe
        return self.status == 'live'

    @property
    def is_upcoming(self):
        # True si està programat per al futur
        return (
            self.status == 'scheduled'
            and self.scheduled_date is not None
            and self.scheduled_date > timezone.now()
        )

    def get_duration(self):
        """
        Retorna la durada estimada en minuts
        si l'esdeveniment està finalitzat.
        """
        if self.status != 'finished':
            return None
        return self.category_durations.get(self.category, 90)

    def get_tags_list(self):
        """
        Retorna les etiquetes com a llista.
        Exemple: "rock, indie, directes" -> ["rock", "indie", "directes"]
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def get_stream_embed_url(self):
        """
        Converteix URLs de YouTube/Twitch/Vimeo a format embed per la plantilla.
        Si no es reconeix la plataforma, retorna la URL original.
        """
        if not self.stream_url:
            return None

        url = self.stream_url.strip()
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        # --------- YOUTUBE ----------
        if 'youtube.' in host or 'youtu.be' in host:
            video_id = None

            # Format curt: https://youtu.be/<id>
            if 'youtu.be' in host:
                video_id = parsed.path.strip('/')

            # Formats típics: https://www.youtube.com/watch?v=<id>
            #                https://www.youtube.com/live/<id>
            #                https://www.youtube.com/shorts/<id>
            else:
                if parsed.path.startswith('/watch'):
                    query = parse_qs(parsed.query)
                    video_id = query.get('v', [None])[0]
                elif parsed.path.startswith('/live/'):
                    # /live/<id>
                    parts = parsed.path.split('/')
                    if len(parts) >= 3:
                        video_id = parts[2]
                elif parsed.path.startswith('/shorts/'):
                    # /shorts/<id>
                    parts = parsed.path.split('/')
                    if len(parts) >= 3:
                        video_id = parts[2]

            if video_id:
                return f'https://www.youtube.com/embed/{video_id}'
            return url

        # --------- TWITCH ----------
        if 'twitch.tv' in host:
            path_parts = parsed.path.strip('/').split('/')
            # Canal: https://www.twitch.tv/<canal>
            if path_parts and path_parts[0] and path_parts[0] != 'videos' and path_parts[0] != 'clip':
                channel = path_parts[0]
                # Nota: el paràmetre "parent" és obligatori en producció, aquí fem servir "localhost" per demo.
                return f'https://player.twitch.tv/?channel={channel}&parent=localhost'

            # Vídeo: https://www.twitch.tv/videos/<id>
            if len(path_parts) >= 2 and path_parts[0] == 'videos':
                video_id = path_parts[1]
                return f'https://player.twitch.tv/?video=v{video_id}&parent=localhost'

            # Clip (simplificat): https://www.twitch.tv/clip/<slug>
            if len(path_parts) >= 2 and path_parts[0] == 'clip':
                clip_slug = path_parts[1]
                # Alguns reproductors accepten /?clip=slug, però ho deixem com a URL original per simplicitat.
                return url

            return url

        # --------- VIMEO ----------
        if 'vimeo.com' in host:
            # Format: https://vimeo.com/<id>
            parts = parsed.path.strip('/').split('/')
            if parts and parts[0].isdigit():
                video_id = parts[0]
                return f'https://player.vimeo.com/video/{video_id}'
            return url

        # --------- ALTRES PLATAFORMES ----------
        # Per altres plataformes retornem la mateixa URL. Si és embeddable,
        # l'iframe la mostrarà igualment.
        return url
