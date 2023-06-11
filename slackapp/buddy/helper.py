from .models import Topic, Subtopic


def display_topic(topic_name):
    topic = Topic.objects.get(topic_name=topic_name)
    subtopics = topic.subtopic_set.all()

    command_text = " *" + str(topic_name) + "* :\n"
    for subtopic in subtopics:
        command_text += f" `{subtopic.sentence_text}`\n"

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": command_text
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    return payload


def payload_add_subtopics(topic_name):
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": topic_name
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter Commands",
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Approve"
                        },
                        "style": "primary",
                        "value": "click_me_123",
                        "action_id": "add_to_db"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Deny"
                        },
                        "style": "danger",
                        "value": "click_me_123",
                        "action_id": "deny"
    }
                ]
            },
            {
                "type": "divider"
            }
        ]
    }

    return payload


def payload_edit_topic(topic_name):
    topic = Topic.objects.get(topic_name=topic_name)
    subtopics = topic.subtopic_set.all()

    command_text = ""
    for subtopic in subtopics:
        command_text += f"{subtopic.sentence_text}\n"
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": topic_name
                }
            },
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action",
                    "initial_value": command_text
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter Commands",
                    "emoji": True
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Edit"
                        },
                        "style": "primary",
                        "value": "click_me_123",
                        "action_id": "edit_in_db"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Deny"
                        },
                        "style": "danger",
                        "value": "click_me_123",
                        "action_id": "deny"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
    }

    return payload