import logging
import ask_sdk_core.utils as ask_utils
import boto3
import uuid
import re 
import pytz
from datetime import datetime, timedelta
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

scope = ["https://www.googleapis.com/auth/calendar"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
API_NAME = 'calendar'
API_VERSION = 'v3'

# google calendar service
service = build(API_NAME, API_VERSION, credentials=creds)

class LaunchRequestHandler(AbstractRequestHandler): 
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! Welcome to our appointment scheduling service.Are you already a user with us? If yes,say 'existing user' to schedule a doctor appointment. If you are a new user,say 'new user' to create a new user ID."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class UserIntentHandler(AbstractRequestHandler):
    """Handler for UserIntent for new user."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("UserIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots

        name = slots['name'].value
        age = slots['age'].value
        # Get the main value of the gender slot
        gender_slot = slots['gender']
        gender = gender_slot.resolutions.resolutions_per_authority[0].values[0].value.name
        email = slots['email'].value
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['name'] = name
        session_attr['age'] = age
        session_attr['gender'] = gender
        
        email = email.lower()
        email = email.replace(" at ", "@").replace(" dot ", ".").replace(" ","")
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        session_attr['email'] = email
        if(re.match(pattern, email) is not None):

            # Check if the email is already verified in SES
            ses_client = boto3.client('ses', region_name="eu-west-1")
            response = ses_client.list_identities(IdentityType='EmailAddress')
            verified_emails = response['Identities']
    
            if email not in verified_emails:
                # Email not verified, send verification email
                verify_email_identity(email)
                speak_output = f"Thank you for providing your information. A verification email has been sent to your email address. Please check your inbox and follow the instructions to verify your email. Once you have verified your email, say 'Verified'."
            else:
                # Email already verified, generate user ID and send user information
                user_id = generate_user_id()
                session_attr['user_id'] = user_id
                store_user_info(user_id, name, age, gender, email)
                subject = "User ID is successfully created "
                body = f"Dear {name},your information has been stored. Your ID is {user_id}."
                send_email(email,subject,body)
                speak_output = f"Thank you for providing your information. Your ID is {user_id}. The details have been sent to the email.If you want to schedule an appointment say 'schedule'"
        else:
            speak_output="I'm sorry, the provided email address is not valid. Please try again."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )      
        
class UserIDIntentHandler(AbstractRequestHandler): 
    """Handler for UserID Info Intent for existing user."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("UserIDIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        user_id = slots["userID"].value
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['user_id'] = user_id
        email=get_email_of_user_by_ID(user_id)
        session_attr['email'] = email
        speak_output=f"Your Id is {user_id}"
        try:
            # Check if the user ID exists in your user database
            if check_user_exists(user_id):
                speak_output="Your ID is confirmed if you want to schedule an appointment say 'schedule'"
            else:
                speak_output="We don't have your ID in our data base.If you want to create one say 'new user'"
        except ValueError:
            # Invalid user ID format
            speak_output = "The user ID should be a valid integer. Please try again."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )
        
def check_user_exists(user_id):
    dynamodb_client = boto3.client('dynamodb')
    table_name = 'UserInfo'

    response = dynamodb_client.get_item(
        TableName=table_name,
        Key={'ID': {'S': user_id}}
    )

    return 'Item' in response
    
def verify_email_identity(email):
    ses_client = boto3.client('ses', region_name="eu-west-1")
    response = ses_client.verify_email_identity(EmailAddress=email)
    return response
    
class VerifyEmailIntentHandler(AbstractRequestHandler): 
    """Handler for the 'VerifyEmailIntent' to handle user confirmation of email verification."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("VerifyEmailIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        email = session_attr.get('email')
        name=session_attr.get('name')
        age=session_attr.get('age')
        gender=session_attr.get('gender')

        if email:
            user_id = generate_user_id()
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr['user_id'] = user_id
            store_user_info(user_id, name, age, gender, email)
            subject = "User ID is successfully created "
            body = f"Dear {name},your information has been stored. Your ID is {user_id}."
            send_email(email,subject,body)
            speak_output = f"Thank you for verifying your email. Your ID is {user_id}.The details have been sent to the email.If you want to schedule an appointment say 'schedule'"
        else:
            # No email provided in session attributes
            speak_output = "Sorry, I couldn't find any pending email verification. Please provide your information again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
        
class ScheduleIntentHandler(AbstractRequestHandler):
    """Handler for Scheduler Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ScheduleIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        date = str(slots["date"].value)
        time = str(slots["time"].value)
        department=str(slots["department"].value)
        doctors = get_doctors_by_department(department)
        handler_input.attributes_manager.session_attributes["date"] = date
        handler_input.attributes_manager.session_attributes["time"] = time
        handler_input.attributes_manager.session_attributes["department"] = department
        # Convert the doctors list to a string for speech output
        doctors_str = ", ".join(doctors)
        
        return (
            handler_input.response_builder
                .speak(f"The available doctors in the {department} department are {doctors_str}. Please select a doctor for scheduling.Say 'schedule an appointment with DoctorName'")
                .response
        )
        
class doctorScheduleHandler(AbstractRequestHandler):
    """Handler for doctorScheduleHandler Intent for scheduling with a user specified doctor."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("doctorSchedule")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        doctName = slots["doctName"].value
        # Retrieve the calendar ID from the DynamoDB table based on the doctor's name
        calendar_id = get_calendar_id_by_doctor_name(doctName)
        # Store the calendar ID in session attributes
        handler_input.attributes_manager.session_attributes["calendar_id"] = calendar_id
        handler_input.attributes_manager.session_attributes["doctName"] = doctName
        
        session_attr = handler_input.attributes_manager.session_attributes
        date = session_attr.get('date')
        time = session_attr.get('time')
        dateSlot = datetime.strptime(date, "%Y-%m-%d")
        hour = int(time.split(":")[0])
        mins = int(time.split(":")[1])
        time_min = datetime(dateSlot.year, dateSlot.month, dateSlot.day, hour, mins)
        time_max = time_min + timedelta(hours=1)
        # Store the time_min value in session attributes
        handler_input.attributes_manager.session_attributes["time_min"] = str(time_min)
        if check_free_busy(time_min, time_max,calendar_id):
            
            reserve_appointment(handler_input,time_min, time_max,calendar_id)

            session_attr = handler_input.attributes_manager.session_attributes
            email = session_attr.get('email')
            user_id=session_attr.get('user_id')
            department = session_attr.get('department')
            
            subject = "Appointment Scheduled"
            body = f"Dear {user_id},your appointment is successfully scheduled at {time} with {doctName} in {department} department."
            send_email(email,subject,body)
            
            speak_output = f"Your appointment on {date} at {time} is successfully scheduled."
        else :
            speak_output = f"Sorry, the selected time is not available. Would you like to schedule in the next available slot?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )
           
    
class ConfirmationIntentHandler(AbstractRequestHandler):
    """Handler for Confirmation Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ConfirmationIntent")(handler_input)

    def handle(self, handler_input):
        time_min = handler_input.attributes_manager.session_attributes.get("time_min")
         
        slots = handler_input.request_envelope.request.intent.slots
        confirmation_slot = slots["confirmation"]
        # Retrieve the calendar ID from the session attributes
        calendar_id = handler_input.attributes_manager.session_attributes.get("calendar_id")
        if confirmation_slot and confirmation_slot.resolutions and confirmation_slot.resolutions.resolutions_per_authority:
            confirmation_value = confirmation_slot.resolutions.resolutions_per_authority[0].values[0].value.name
            
            if confirmation_value == "yes":
                next_slot = find_next_available_slot(handler_input,time_min)
                
                if next_slot is not None:
                    reserve_appointment(handler_input,next_slot['start'], next_slot['end'],calendar_id)
                    speak_output = f"Your appointment on {next_slot['date']} at {next_slot['time']} is successfully scheduled."
                else:
                    speak_output = "Sorry, there are no available slots at the moment. Please try again later."
            else:
                speak_output = "Alright, let me know when you want to schedule an appointment."
        else:
            speak_output = "Sorry, I didn't understand your confirmation. Please try again."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("How can I assist you further?")
                .response
        )
        
def get_doctors_by_department(department):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Doctor_info')

    response = table.scan(
        FilterExpression='department = :dep',
        ExpressionAttributeValues={
            ':dep': department
        }
    )

    doctors = [item['doctorName'] for item in response['Items']]
    return doctors   
              
        
class ForgotUserIDIntentHandler(AbstractRequestHandler):
    """Handler for the ForgotUserIDIntent to retrieve user IDs based on email."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ForgotUserIDIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        user_email = slots["userEmail"].value
        user_email = user_email.lower()
        user_email = user_email.replace(" at ", "@").replace(" dot ", ".").replace(" ","")

        # Retrieve the user IDs based on the provided email from the DynamoDB table
        user_ids = get_user_ids_by_email(user_email)

        if user_ids:
            speak_output = f"The user IDs associated with the email {user_email} are {', '.join(user_ids)}."
        else:
            speak_output = f"No user IDs found for the email {user_email}. Please check the email or try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


def get_user_ids_by_email(email):
    # Initialize the DynamoDB client
    dynamodb = boto3.client('dynamodb')

    response = dynamodb.scan(
        TableName='UserInfo',
        FilterExpression='email = :email',
        ExpressionAttributeValues={
            ':email': {'S': email}
        }
    )

    # Check if any matching records were found
    if response['Count'] > 0:
        user_ids = [item['ID']['S'] for item in response['Items']]
        return user_ids

    return None


client = boto3.client('dynamodb')
def store_user_info(id, name, age, gender, email):
    # Put item (store user information) in the table
    response = client.put_item(
        TableName='UserInfo',
        Item={
            'ID': {'S': id},
            'name': {'S': name},
            'age': {'N': str(age)},
            'gender': {'S': gender},
            'email': {'S': email}
        }
    )

def send_email(email, subject,body):
    ses_client = boto3.client('ses',region_name="eu-west-1")
    sender_email = "gssr2593@gmail.com" 
    
    response = ses_client.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [email]},
        #Destination={'ToAddresses': ["gssr2593@gmail.com"]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    return response

dynamodb = boto3.client('dynamodb')
def generate_user_id():
    # Set the time zone to your desired time zone
    time_zone = pytz.timezone('Asia/Kolkata')
    # Get the current date and time in the specified time zone
    current_date = datetime.now(time_zone).strftime('%Y%m%d')
    # Query all items in the DynamoDB table
    response = dynamodb.scan(
        TableName='UserInfo'
    )

    existing_ids = [item['ID']['S'] for item in response['Items']]

    if not existing_ids:
        # If no existing user IDs, set sequence number to 1
        sequence_number = 1
    else:
        # Filter existing IDs based on matching first 8 characters of the current date
        existing_ids = [user_id for user_id in existing_ids if user_id.startswith(current_date)]

        if not existing_ids:
            # If no existing user IDs for the current date, set sequence number to 1
            sequence_number = 1
        else:
            # Find the maximum sequence number
            max_sequence_number = max(int(user_id[8:]) for user_id in existing_ids)

            # Increment the sequence number until a unique ID is found
            sequence_number = (max_sequence_number + 1) % 1000

    new_user_id = f"{current_date}{sequence_number:03d}"

    return new_user_id


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(VerifyEmailIntentHandler())
sb.add_request_handler(UserIntentHandler())
sb.add_request_handler(UserIDIntentHandler())
sb.add_request_handler(ScheduleIntentHandler())
sb.add_request_handler(ConfirmationIntentHandler())
sb.add_request_handler(doctorScheduleHandler())
sb.add_request_handler(ForgotUserIDIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()


client = boto3.client('dynamodb')
def reserve_appointment(handler_input,time_min, time_max,calendar_id):
    
    # Retrieve the user ID from the session attributes
    user_id = handler_input.attributes_manager.session_attributes.get("user_id")
    
    # Specify the time zone as IST
    timezone = pytz.timezone('Asia/Kolkata')

    # Convert the start and end times to IST
    time_min_ist = time_min.astimezone(timezone)
    time_max_ist = time_max.astimezone(timezone)
    # Retrieve the username from the DynamoDB table using the user ID
    response = client.get_item(
        TableName='UserInfo',
        Key={'ID': {'S': user_id}}
    )

    if 'Item' in response:
        username = response['Item']['name']['S']
    else:
        # Handle the case when the user is not found
        username = "Unknown"
    event = {
        'summary': 'appointment',
        'description': f'UserID of patient:{user_id} \nPatient name: {username} ',
        'start': {
            'dateTime': time_min_ist.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': time_max_ist.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    response = service.events().insert(calendarId=calendar_id, body=event).execute()

def check_free_busy(time_min, time_max,calendar_id):
    try:
        # Convert time_min and time_max to IST timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        time_min_ist = time_min.astimezone(ist_timezone)
        time_max_ist = time_max.astimezone(ist_timezone)
        
        free_busy_query = {
            'timeMin': time_min_ist.isoformat(),
            'timeMax': time_max_ist.isoformat(),
            'timeZone': 'Asia/Kolkata',
            'items': [{'id': calendar_id}]
        }
        response = service.freebusy().query(body=free_busy_query).execute()
        calendars = response.get('calendars', {})
        calendar = calendars.get(calendar_id, {})
        busy_slots = calendar.get('busy', [])
        return len(busy_slots) == 0
    except Exception as e:
        logging.error(f"Error querying free/busy: {str(e)}")
        return False

def schedule_appointment():
    next_slot = find_next_available_slot()
    if next_slot is not None:
        # Book the appointment
        reserve_appointment(next_slot['start'], next_slot['end'])
        return True, f"Your appointment on {next_slot['date']} at {next_slot['time']} is successfully scheduled."
    else:
        return False, "Sorry, there are no available slots at the moment. Please try again later."

def find_next_available_slot(handler_input,time_min):
    # Retrieve the calendar ID from the session attributes
    calendar_id = handler_input.attributes_manager.session_attributes.get("calendar_id")
    time_min = datetime.strptime(time_min, "%Y-%m-%d %H:%M:%S")
    # Get the current time
    current_time =time_min
    # Set the time range to search for available slots (e.g., next 1 day)
    time_min = current_time
    time_max = current_time + timedelta(days=1)
    # Increment the time in intervals to find the next available slot
    interval = timedelta(minutes=60)
    while time_min <= time_max:
        if check_free_busy(time_min, time_min + interval,calendar_id):
            # Found an available slot
            return {
                'start': time_min,
                'end': time_min + interval,
                'date': time_min.date().strftime("%Y-%m-%d"),
                'time': time_min.time().strftime("%H:%M")
            }

        time_min += interval

    return None

def get_calendar_id_by_doctor_name(doctName):
    # Initialize the DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    response = dynamodb.scan(
        TableName='Doctor_info',
        FilterExpression='doctorName = :name',
        ExpressionAttributeValues={
            ':name': {'S': doctName}
        }
    )
    # Check if a matching record was found
    if response['Count'] > 0:
        item = response['Items'][0]
        calendar_id = item['calendarID']['S']
        return calendar_id
    
    return None

def get_email_of_user_by_ID(user_id):
    # Initialize the DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    response = dynamodb.scan(
        TableName='UserInfo',
        FilterExpression='ID = :name',
        ExpressionAttributeValues={
            ':name': {'S': user_id}
        }
    )
    # Check if a matching record was found
    if response['Count'] > 0:
        item = response['Items'][0]
        email = item['email']['S']
        return email
    
    return None