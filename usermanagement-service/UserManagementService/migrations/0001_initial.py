# Generated by Django 5.1.2 on 2024-11-29 11:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('nb_game', models.IntegerField(default=0)),
                ('nb_win', models.IntegerField(default=0)),
                ('nb_losses', models.IntegerField(default=0)),
                ('avg_duration', models.FloatField(default=0)),
                ('friends', models.ManyToManyField(through='UserManagementService.Friendship', to='UserManagementService.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('match_start_time', models.DateTimeField()),
                ('match_end_time', models.DateTimeField(blank=True, null=True)),
                ('score_player_1', models.IntegerField(default=0)),
                ('score_player_2', models.IntegerField(default=0)),
                ('player_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player_1', to='UserManagementService.userprofile')),
                ('player_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches_as_player_2', to='UserManagementService.userprofile')),
            ],
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_user_1', to='UserManagementService.userprofile'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_user_2', to='UserManagementService.userprofile'),
        ),
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together={('user_1', 'user_2')},
        ),
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by', to='UserManagementService.userprofile')),
                ('blocker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_users', to='UserManagementService.userprofile')),
            ],
            options={
                'verbose_name': 'Blocked User',
                'verbose_name_plural': 'Blocked Users',
                'unique_together': {('blocker', 'blocked')},
            },
        ),
    ]
