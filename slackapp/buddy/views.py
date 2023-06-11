from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.http import HttpResponse, JsonResponse
from .models import Topic, Subtopic
from .helper import *
import slack

client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)


@csrf_exempt
def event(request):
    json_dict = json.loads(request.body.decode('utf-8'))
    if json_dict['token'] != settings.VERIFICATION_TOKEN:
        return HttpResponse(status=403)
    if 'type' in json_dict:
        if json_dict['type'] == 'url_verification':
            response_dict = {"challenge": json_dict['challenge']}
            return JsonResponse(response_dict, safe=False)
    # if 'event' in json_dict:
    #     event_msg = json_dict['event']
    #     if ('subtype' in event_msg) and (event_msg['subtype'] == 'bot_message'):
    #         return HttpResponse(status=200)
    #     if 'bot_id' not in event_msg and event_msg['type'] == 'message':
    #         user = event_msg['user']
    #         msg = event_msg['text']
    #         channel = event_msg['channel']
    #         response_msg = ":wave:, Hello <@%s>" % user
    #         response_msg += "\nYour message was : " + msg
    #         client.chat_postMessage(channel=channel, text=response_msg)
    #         return HttpResponse(status=200)
    return HttpResponse(status=200)


@csrf_exempt
def add(request):
    if request.method == 'POST':
        command_text = request.POST['text']
        command_args = command_text.splitlines()
        channel = request.POST.get('channel_id')

        topic_name = command_args[0]
        topic_exists = Topic.objects.filter(topic_name=topic_name).exists()

        if topic_exists:
            client.chat_postMessage(channel=channel, text="Topic already exists!!")
            mssg = display_topic(topic_name)
            client.chat_postMessage(channel=channel, **mssg)

        else:
            payload = payload_add_subtopics(topic_name)
            client.chat_postMessage(channel=channel, **payload)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


@csrf_exempt
def edit(request):
    if request.method == 'POST':
        channel = request.POST.get('channel_id')
        topic_name = request.POST['text']
        topic_exists = Topic.objects.filter(topic_name=topic_name).exists()

        if topic_exists:
            msg = payload_edit_topic(topic_name)
            client.chat_postMessage(channel=channel, **msg)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)
    return HttpResponse(status=200)

@csrf_exempt
def delete(request):
    if request.method == 'POST':
        channel = request.POST.get('channel_id')
        topic_name = request.POST['text']

        if topic_name == 'all':
            Topic.objects.all().delete()
            client.chat_postMessage(channel=channel, text="All the topics have been successfully deleted!")
        elif Topic.objects.filter(topic_name=topic_name):
            topic = Topic.objects.get(topic_name=topic_name)
            topic.delete()
            client.chat_postMessage(channel=channel, text="Topic - " + topic_name + " successfully deleted!")
        else:
            client.chat_postMessage(channel=channel, text="Topic - " + topic_name + " not present!")
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


@csrf_exempt
def display(request):
    if request.method == 'POST':
        client = slack.WebClient(token=settings.BOT_USER_ACCESS_TOKEN)
        channel = request.POST.get('channel_id')
        command = request.POST['text']
        topics = Topic.objects.all()

        if command == 'topics':
            for topic in topics:
                topic_info = f'- *{topic.topic_name}*\n'
                client.chat_postMessage(channel=channel, text=topic_info)
            return HttpResponse(status=200)
        elif command == 'all':
            for topic in topics:
                topic_info = display_topic(topic.topic_name)
                client.chat_postMessage(channel=channel, **topic_info)
            return HttpResponse(status=200)
        else:
            topic_exists = Topic.objects.filter(topic_name=command).exists()
            if topic_exists:
                topic_info = display_topic(command)
                client.chat_postMessage(channel=channel, **topic_info)
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=403)

    return HttpResponse(status=403)


@csrf_exempt
def interactivity(request):
    payload = json.loads(request.POST.get('payload'))
    if request.method == 'POST':
        channel = payload['container']['channel_id']
        ts = payload['container']['message_ts']
        if payload['type'] == 'block_actions':
            for action in payload['actions']:
                topic_name = payload['message']['blocks'][0]['text']['text']
                if action['action_id'] == 'add_to_db':
                    block_id = payload['message']['blocks'][1]['block_id']
                    subtopics = payload['state']['values'][block_id]['plain_text_input-action']['value']

                    topic = Topic.objects.create(topic_name=topic_name)
                    if subtopics is not None:
                        subtopics = subtopics.splitlines()
                        for subtopic_text in subtopics:
                            Subtopic.objects.create(topic=topic, sentence_text=subtopic_text)
                    response_text = f"Topic '{topic_name}' and subtopics created successfully."
                    res = client.chat_update(channel=channel, ts=ts, text=response_text, blocks=[])

                    display_topic(topic_name)
                    return HttpResponse(status=200)
                elif action['action_id'] == 'edit_in_db':
                    block_id = payload['message']['blocks'][1]['block_id']
                    subtopics = payload['state']['values'][block_id]['plain_text_input-action']['value']

                    topic_fetch = Topic.objects.get(topic_name=topic_name)
                    topic_fetch.delete()

                    if subtopics is not None:
                        topic = Topic.objects.create(topic_name=topic_name)
                        subtopics = subtopics.splitlines()
                        for subtopic_text in subtopics:
                            Subtopic.objects.create(topic=topic, sentence_text=subtopic_text)
                        response_text = f"Topic '{topic_name}' and subtopics created successfully."
                        res = client.chat_update(channel=channel, ts=ts, text=response_text, blocks=[])

                        display_topic(topic_name)
                        return HttpResponse(status=200)
                elif action['action_id'] == 'deny':
                    response_text = f"Topic '{topic_name}' and subtopics not added."
                    res = client.chat_update(channel=channel, ts=ts, text=response_text, blocks=[])
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=403)
    return HttpResponse(status=200)

