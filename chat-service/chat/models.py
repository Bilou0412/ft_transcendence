from django.db import models

class Conversation(models.Model):
    participant1 = models.IntegerField()
    participant2 = models.IntegerField()

    def __str__(self):
        return f'Conversation between {self.participant1} and {self.participant2}'

class DirectMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'From {self.sender}: {self.content[:20]}'