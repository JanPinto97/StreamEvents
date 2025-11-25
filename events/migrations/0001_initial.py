# Generated manually for initial Event migration
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

import events.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=events.models.CATEGORY_CHOICES, max_length=50)),
                ('scheduled_date', models.DateTimeField()),
                ('status', models.CharField(choices=events.models.STATUS_CHOICES, default='scheduled', max_length=20)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='events/thumbnails/')),
                ('max_viewers', models.PositiveIntegerField(default=100)),
                ('is_featured', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', models.CharField(blank=True, max_length=500)),
                ('stream_url', models.URLField(blank=True, max_length=500)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Esdeveniment',
                'verbose_name_plural': 'Esdeveniments',
                'ordering': ['-created_at'],
            },
        ),
    ]
