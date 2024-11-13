# Generated by Django 5.1.2 on 2024-11-13 18:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManagementService', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avg_duration',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='MatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_match', models.DateTimeField(auto_now_add=True)),
                ('score_player_1', models.IntegerField()),
                ('score_player_2', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('player_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player_1', to='UserManagementService.userprofile')),
                ('player_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player_2', to='UserManagementService.userprofile')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='won_matches', to='UserManagementService.userprofile')),
            ],
        ),
    ]
