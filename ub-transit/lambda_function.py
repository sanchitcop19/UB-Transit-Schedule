"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from datetime import datetime, timedelta, timezone
import time
import numpy as np

#---------------------shuttle code----------------------

def get_shuttle_schedule():
    today = datetime.now()

    year = today.year
    month = today.month
    date = today.day
    np.set_printoptions(threshold=np.inf)
    data = np.zeros((77, 18), dtype = 'datetime64[s]')
    start = datetime(year, month, date, 6, 30)
    increments = [0, 5, 5, 2, 2, 1, 5, 1, 1, 8, 5, 2, 1, 2, 1, 2, 2, 3]
    inc = True

    def next_row(start):
        nonlocal inc
        if start < datetime(year, month, date, 7, 19):
            return start + timedelta(minutes = 25)
        elif start > datetime(year, month, date, 21, 54):
            if start < datetime(year, month, date, 22, 19):
                return start + timedelta(minutes = 25)
            else:
                return start + timedelta(minutes=50)
        elif inc:
            inc = False
            return start + timedelta(minutes = 12)
        elif not inc:
            inc = True
            return start + timedelta(minutes = 13)
        else:
            raise Exception('this time is not being handled yet')

    for i in range(77):
        t = start
        for j, increment in enumerate(increments):
            if start.hour == 0 and start.minute == 50 and j == 9:
                break
            t = (t + timedelta(minutes = increment))
            data[i, j] = datetime(year, month, date, t.hour, t.minute)
        start = next_row(start)
    return data
#------------------------------------------------------

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi! Would you like me to get the bus or the shuttle schedule for you?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please say either bus or shuttle."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the UB Bus Schedule Retriever. Have a good day!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}

def set_vehicle(vehicle):
    return {"vehicle": vehicle}

def get_bus(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    speech_output = ""
    if 'vehicle' in intent['slots']:
        vehicle = intent['slots']['vehicle']['value']
        session_attributes = set_vehicle(vehicle)
        next_arrival = ""
        local = (np.datetime64(datetime.now()) + np.timedelta64(-4, 'h'))
        if vehicle == "bus":
            pass
        else:
            schedule = get_shuttle_schedule()
            for t in schedule.T[0]:
                #speech_output += (t.astype(str)[11:13] + ":" + t.astype(str)[14:16] + "      " + local.astype(str)[11:13] + ":" + local.astype(str)[14:16])

                if t > local:
                    next_arrival = t.astype(str)[11:13] + ":" + t.astype(str)[14:16]
                    break
        speech_output =  "The " + vehicle.capitalize() + " arrival time for Creekside Village after the time specified is " + next_arrival
        reprompt_text = "Could you state either bus or shuttle one more time?"
    else:
        speech_output = "Please try again."
        reprompt_text = "Please try again, by saying bus or shuttle."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetBusScheduleIntent":
        return get_bus(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

