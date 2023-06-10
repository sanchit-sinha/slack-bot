from django.contrib import admin
from .models import Topic
admin.site.register(Topic)

from .models import Subtopic
admin.site.register(Subtopic)
