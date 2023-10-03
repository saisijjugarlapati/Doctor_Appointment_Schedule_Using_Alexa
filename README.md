# :man_health_worker:Doctor_Appointment_Schedule_Using_Alexa
Doctor_Appointment_Schedule_Using_Alexa is an intelligent appointment scheduling system designed to streamline and simplify the process of booking doctor appointments. This bot utilizes AWS services and integrates with Google Calendar API to provide a seamless user experience for scheduling medical consultations.

## Problem Statement

The Doctor Appointment Scheduler using Alexa skill seeks to transform the traditional process of scheduling doctor appointments, elevating it to new heights of convenience and efficiency for patients. With a seamless and user-friendly interface, this skill empowers patients to effortlessly register, verify their identity, and schedule appointments with their preferred doctors, taking into account real-time availability. The primary objective is to enhance the overall appointment scheduling experience, ensuring patients can easily manage their medical appointments in a professional and hassle-free manner.

## Solution Overview

The Doctor Appointment Scheduler skill is developed using the Alexa Skills Kit (ASK) and utilizes AWS Lambda for serverless processing. It makes use of AWS DynamoDB for storing patient and doctor details, integrates with the Google Calendar API to check doctor availability, and employs Amazon Simple Email Service (SES) for sending email notifications.

The following outlines the primary components of the solution:

1.**New User Registration:** New patients can create an account by providing essential information such as their name, age, gender, and email address. The skill ensures email verification to confirm the user's identity securely.

2.**Existing User Login:** Existing patients can log in using their patient ID. In case they forget their patient ID, they have the option to verify their identity by entering forgot ID.

3.**Doctor Availability Check:** The skill integrates with the Google Calendar API to access doctors' schedules and availability. Patients can inquire about available doctors based on their specialization, date, and time preferences.

4.**Appointment Booking:** Patients can effortlessly schedule appointments with their chosen doctors, taking into account the availability retrieved from the Google Calendar API. Once an appointment is booked, the skill reserves the slot in the doctor's calendar to avoid overlapping appointments.

5.**Appointment Confirmation:** After successfully booking an appointment, the skill sends a confirmation email to the patient, containing details such as the appointment date, time and doctor's name.

6.**Voice-Based Doctor Recommendations:** For added convenience, the skill can offer voice-based doctor recommendations. Patients can inquire about suitable doctors based on their specific symptoms or medical conditions. The skill responds with a list of doctors specialized in relevant fields.

7.**Voice Authentication (Optional):** To enhance security, the skill can implement voice authentication technology. This ensures that only authorized users can access sensitive account information and book appointments.

8.**Email Notifications:** Amazon Simple Email Service (SES) is utilized to send verification and confirmation emails securely. These emails play a crucial role in verifying user identities and keeping patients informed about their scheduled appointments.


## Tech Stack

The Hospital Appointment Scheduler skill is powered by a sophisticated tech stack that includes:

1. **Alexa Skills Kit (ASK):** A cutting-edge set of APIs and tools that enable seamless voice-driven interactions.
2. **AWS Lambda:** A robust serverless compute service that efficiently handles code execution in response to Alexa requests.
3. **AWS DynamoDB:** A high-performing NoSQL database service utilized for secure and scalable storage of patient and doctor data.
4. **Google Calendar API:** An advanced interface that facilitates smooth management of doctor schedules and availability.
5. **Amazon Simple Email Service (SES):** A reliable solution for sending well-timed and informative emails to users, ensuring effective communication.
   
## Work Flow

![work flow](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/d4459745-225a-4ca4-9523-c64a5ef78f5e)
## Skill Features
### User Registration and Verification
* New patients can easily register by providing essential information like name, age, gender, date of birth, father's name, and email.
* The skill sends a verification email to the provided email address for identity confirmation.
* After confirmation, the patient's details are securely stored in the DynamoDB table.
### Existing Patient Authentication:
* Existing patients can log in using their patient ID.
* In case they forget their patient ID, the skill offers an alternative verification method by saying "forgot ID".
### Doctor Availability Checking
* Patients can search for available doctors based on a specified specialization, date, and time.
* The details of the doctors are retrieved from the DynamoDB table of doctors_details.
* Utilizing the Google Calendar API, the skill checks the real-time availability of doctors for the specified time slot.
### Appointment Booking
* Patients can schedule appointments with their chosen doctor based on availability.
* The skill ensures that the appointment slot is successfully reserved in the respective doctor's Google Calendar.
### Voice-Based Doctor Recommendations
* Alexa can provide doctor recommendations based on the patient's symptoms or medical conditions.
* Users can ask Alexa for suggestions, and the skill will offer a list of doctors specializing in relevant fields.
### Voice Authentication
* The skill can use voice authentication technology for secure user registration and login.
### Email Notifications
* The skill sends verification emails to new patients for identity confirmation.
* Additionally, confirmation emails for scheduled appointments are sent to patients' registered email addresses, ensuring they have all necessary details at their fingertips.
## Lambda Function Code
The Lambda function for the Hospital Appointment Scheduler skill is responsible for handling user requests and interacting with the backend services. It is written in Python and integrated with the ASK SDK for Alexa interactions. The code is structured into several intent handlers to handle different user intents, such as registration, login, appointment booking, doctor recommendations, and more. <br />
**Code Link**:[Click Here](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/blob/main/lambda_function.py)
## Skill Invocation and User Flow
1.**Skill Launch**: Users can invoke the skill by saying "Alexa, open Doctor Appointment."

2.**New Patient**: New patients can provide their information during the registration process,the skill will send a verification email to the provided email address.After verification stores the information in DynamoDB.

3.**Verification**: New patients need to verify their email by following the instructions in the verification email.

4.**Existing Patient**: Existing patients can log in using their patient ID. If they forget their ID, they can verify their identity by providing their father's name.

5.**Doctor Availability Checking**: Patients can check the availability of doctors based on specialization, date, and time.

6.**Appointment Booking**: Patients can book appointments with available doctors.

7.**Voice-Based Doctor Recommendations**: Patients can ask Alexa for doctor recommendations based on their symptoms or medical conditions.

8.**Voice Authentication**: The skill uses voice authentication for user identity verification during registration and login.

9.**Email Notifications**: Verification emails are sent to new patients, and confirmation emails are sent for scheduled appointments.

## Working with New Patients
New patients can efficiently register and schedule appointments through the Hospital Appointment Scheduler skill. Below is a step-by-step guide on how new patients can utilize the skill:

1.**Skill Invocation**: New patients can initiate the skill by saying "Alexa, open Hospital Appointment Scheduler."

2.**Registration**: Alexa will guide the new patient through the registration process. The patient needs to provide the following information:
   - Full Name
   - Age
   - Gender
   - Date of Birth (DOB)
   - Father's Name
   - Email Address
3.**Email Verification**: After registration, the skill will send a verification email to the provided email address. The patient must check their email and follow the instructions to complete the verification process.

4.**Account Creation**: Once the email is verified, the skill will create a unique patient ID for the new patient. The patient can use this ID for future logins.

5.**Storing the Information**: The details of the patient are successfully stored in the DynamoDB in the form of table.

6.**Doctor Availability Checking**: New patients can inquire about doctor availability based on their preferred specialization, date, and time.

7.**Appointment Booking**: After selecting a suitable doctor and appointment slot, the patient can proceed to book the appointment. Alexa will confirm the booking and send a confirmation email to the patient.

![1n](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/51e88fef-e84f-4665-a077-c613543c1234)

![4_20230731_053157351](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/4488b97e-434d-4eef-879b-32f8a0dc6a41)

## Working with Existing Patients
Existing patients can conveniently access their accounts and manage appointments through the Doctor Appointment Scheduler skill. Here's a step-by-step guide on how existing patients can use the skill:

1.**Skill Invocation**: Existing patients can launch the skill by saying "Alexa, open doctor appointment."

2.**Existing patient Login**: Alexa will prompt the existing patient to provide their unique patient ID for authentication. The patient can say, "My patient ID is [patient ID]," to log in directly.

3.**Appointment Management**: Once logged in, existing patients can manage their appointments with ease. They can schedule appointments, check available doctors by giving date, time and your required specialization.

4.**Doctor Recommendations**: Existing patients can also ask for doctor recommendations based on their medical condition or symptoms. Alexa will provide a list of doctors specializing in relevant fields to help them make informed decisions.

5.**Appointment Booking**: After selecting a suitable doctor and appointment slot, the patient can proceed to book the appointment. Alexa will confirm the booking and send a confirmation email to the patient.

![e1](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/d669ee0d-57bc-44d0-a010-fc87e9eca534)

# If Patient forgets ID
-->**Forgot Patient ID**: In case the patient forgets their patient ID, Alexa will offer an alternative way to verify their identity. The patient can say, "I forgot my ID," and Alexa will ask their email for verification.

![f20230731_053223610](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/77ebcd35-91b2-4038-be88-b2fbc9dba2dc)

# DynamoDB
In our project we use two DynamoDB tables:

1. ### UserInfo Table:
* **Purpose**: This table is used to store the registration details of new patients who use the Alexa skill for the first time. -Attributes: - patient_id: The unique identifier for each patient. - full_name: The full name of the patient. - age: The age of the patient. - gender: The gender of the patient. - DOB: The date of birth of the patient. - Father_name: The father's name of the patient. - email: The email address of the patient used for verification and communication.

* **Usage**: When a new patient uses the skill, their registration information is collected and stored in this table. It is also used to retrieve the patient's details when they return to the skill.

* **UserInfo csv file**:[Patient data](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/blob/main/Patient%20data.csv)

2. ### Doctor_info Table:
Purpose: This table is used to store the availability details of doctors for scheduling appointments.

* **Attributes**: - doctor_name: The name of the doctor. - specialization: The medical specialization of the doctor. - calendar_id: The unique identifier for the doctor's Google Calendar. -Usage: The skill checks this table to find available doctors based on user-requested medical specialization and schedules appointments by updating the doctors' calendars with the appointment details.

* **Doctor_info csv file**:[Doctor details](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/blob/main/Doctor%20details.csv)


# Emails you get while working with the skill
## Verification Email

![20230731_052320579](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/1ee45a0b-b784-4299-9897-32bdb2a0b8ea)

## Confirmation page

![c_20230731_052808309](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/d48d2cd1-616e-4ac1-9521-9708a524c09d)

## Details Email

![u_20230731_052929582](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/d4849be3-7063-4db4-9d1d-cb17bbd40a84)

## Appointment Scheduled Email 

![a_20230731_052904732](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/66a94204-1e25-4f2a-b081-c352aa9d52cf)

## Appointment Scheduling Process in Google Calendar
-> The image below will provide the information or pictorial representation how the appointments of different patients are scheduled in calendar (Hospital Calendar)

![doctorCalendar](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/05b6a308-0a8c-4845-912b-5642aeb8daea)

->The image below will provide the representation how the doctor will be able to access the information of patient in his personal calendar or whole hospital calendar

![detailsOfPatient](https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa/assets/107229888/7994dded-998c-40fc-b613-7ea2fbe2bb10)

# Applications
1.**Voice-Based Doctor Recommendations**: Implement a feature that allows Alexa to recommend doctors based on the patient's symptoms or medical conditions. Users can ask Alexa for suggestions, and the skill can provide a list of doctors specializing in relevant fields.

2.**Appointment Reminders**: Enable the skill to send appointment reminders to patients a day or a few hours before their scheduled appointment. This can help reduce no-shows and improve overall patient attendance.

3.**Multilingual Support**: Extend the skill's capabilities to support multiple languages. Patients from diverse linguistic backgrounds can then interact with the skill in their preferred language.

4.**Voice Authentication**: Integrate voice authentication technology to improve security during the registration and login process. This can enhance the skill's ability to verify the identity of patients securely.

5.**Emergency Services**: Add emergency response capabilities, where users can request immediate medical assistance or information during critical situations.

# Author
The Doctor Appointment Scheduler using Alexa skill was developed by :

* [@saisijjugarlapati](https://github.com/saisijjugarlapati)
* Repository : https://github.com/saisijjugarlapati/Doctor_Appointment_Schedule_Using_Alexa
Feedback
For any feedback or queries, please reach out to me at gssr2593@gmail.com
