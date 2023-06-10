from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.http import HttpResponse, JsonResponse
from .models import Topic, Subtopic
import slack


@csrf_exempt
def event(request):
    client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
    json_dict = json.loads(request.body.decode('utf-8'))
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
    if 'event' in json_dict:
        event_msg = json_dict['event']
        if ('subtype' in event_msg) and (event_msg['subtype'] == 'bot_message'):
            return HttpResponse(status=200)
        if 'bot_id' not in event_msg and event_msg['type'] == 'message':
            user = event_msg['user']
            msg = event_msg['text']
            channel = event_msg['channel']
            response_msg = ":wave:, Hello <@%s>" % user
            response_msg += "\nYour message was : " + msg
            client.chat_postMessage(channel=channel, text=response_msg)
            return HttpResponse(status=200)
    return HttpResponse(status=200)


@csrf_exempt
def add(request):
    if request.method == 'POST':
        client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
        command_text = request.POST['text']
        command_args = command_text.splitlines()
        channel = request.POST.get('channel_id')

        topic_name = command_args[0]
        topic_exists = Topic.objects.filter(topic_name=topic_name).exists()

        if topic_exists:
            topic = Topic.objects.get(topic_name=topic_name)
            subtopics = topic.subtopic_set.all()

            response_text = f"Topic '{topic_name}' already exists. Existing commands:\n"
            for subtopic in subtopics:
                response_text += f"- {subtopic.sentence_text}\n"

            client.chat_postMessage(channel=channel, text=response_text)

        else:
            # Topic does not exist, create a new topic and add subtopics
            topic = Topic.objects.create(topic_name=topic_name)
            subtopics = command_args[1:]  # Remaining lines are commands

            for subtopic_text in subtopics:
                Subtopic.objects.create(topic=topic, sentence_text=subtopic_text)

            response_text = f"Topic '{topic_name}' and subtopics created successfully."
            client.chat_postMessage(channel=channel, text=response_text)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


@csrf_exempt
def delete(request):
    if request.method == 'POST':
        client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
        channel = request.POST.get('channel_id')
        topic_name = request.POST['text']

        print(topic_name)
        if Topic.objects.filter(topic_name=topic_name):
            topic = Topic.objects.get(topic_name=topic_name)
            print(topic)
            topic.delete()
            client.chat_postMessage(channel=channel, text="Topic - " + topic_name + " successfully deleted!")
        else:
            client.chat_postMessage(channel=channel, text="Topic - " + topic_name + " not present!")
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)
