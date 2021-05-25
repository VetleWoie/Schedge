# schedge

Event scheduler - Finds the time for what you want!!

## Server setup
### Running the server locally
1. Install pipenv  
```$ pip3 install pipenv```
2. Navigate to the ```/schedge/ziginc/``` directory (containing the ```/Pipfile/``` directory) 
3. Install the dependencies in the virtual enviroment  
```$ pipenv install```
4. Start the virtual enviroment shell  
```$ pipenv shell```
5. Run the server  
```$ ./manage.py runserver```

## Web application user manual
### Creating a user
1. Press _Create an account_ on the landing page
2. Enter credentials
3. Read terms and conditions and _then_ check the box
4. Press _Sign up_

### Signing in 
1. Press _Sign in_ on the landing page
2. Enter credentials
3. Press _Sign in_

### Resetting password 
1. Press _Sign in_ on the landing page
2. Press _Reset Password_
3. Enter a valid email
4. Follow link in email (inside ```/schedge/ziginc/schedge/sent_emails/```)
5. Follow instructions on screen to reset password

### Adding a friend
0. Be signed in (see _Signing in_ section)
1. Press _Friends_ on localhost:8000/mypage/
2. Enter the username of the friend you want to add and click the button to the right

### Answer a friend request
0. Be signed in (see _Signing in_ section)
1. Press _Friends_ on localhost:8000/mypage/
2. Pick the appropriate response to the friend request

### Creating an event
0. Be signed in (see _Signing in_ section)
1. Press _Create event_ on localhost:8000/mypage/
2. Enter a fitting title for the event and proceed to the next step  
_2.1 (Optional: Enter a description and choose an event image)_  
3. Enter a location where the event should take place or press _Use Your Current Location_,  
then proceed to the next step 
4. Enter dates between when the event may take place, then proceed to the next step
5. Enter the approximated duration of the event, then proceed to the next step
6. Enter between the time of day the event should take place, then confirm
7. If all the information was valid you will have the option to go to the event,  
elsewise you will be taken back to step 2.

### Invite someone to your event
0. Be navigated to one of your event's page
1. Press _Invite someone to the event_ 
2. Pick a friend from the drop down list or enter someones username and press the button

### Answer an event invite
0. Be signed in (see _Signing in_ section)
1. Press _Home_ on localhost:8000/mypage/
2. Pick the appropriate response to the invite

### Add a time slot you are available to an event
0. Be navigated to one of your event's pages
1. Press _Add a time_
2. Enter the time interval at a date you are available and press _Submit_

### Deciding the time of the event
0. Be navigated to one of your event's pages that you are hosting
1. Make sure you have selected the _overlapping time slots_ tab
2. Select an overlapping time slot
3. Select the exact time of the event from the menu choices and confirm 

### Edit an existing event
0. Be navigated to one of your event's pages that you are hosting
1. Press _Edit_
2. Follow the _Creating an event_ section from step 2.

### Deleting an event 
0. Be navigated to one of your event's pages that you are hosting
1. Press _Edit_
2. Press _Delete Event_ in the bottom right corner

### Removing a participant from an event
0. Be navigated to one of your event's pages that you are hosting
1. Press _Attendees_
2. Press the bin next to the user you want to remove

