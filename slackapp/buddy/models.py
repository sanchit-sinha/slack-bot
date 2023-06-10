from django.db import models


class Topic(models.Model):
    topic_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_name


class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    sentence_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sentence_text
