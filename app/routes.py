from app import app, ask, db
from app.forms import LoginForm, VerificationForm, RegistrationForm, TokenForm
from app.models import User, Echo
from flask import redirect, render_template, url_for, session, flash, request as flask_request
from flask_ask import statement, question, request, context, session as ask_session
from flask_login import current_user, login_user, logout_user, login_required
from random import randint
import requests
import pandas as pd
from datetime import datetime, timedelta


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.auth_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    form = VerificationForm()
    if form.validate_on_submit():
        verified = db.session.query(Echo.id).filter(Echo.code == int(form.code.data)).first()
        if verified is not None:
            session['verified'] = True
            session['echo'] = verified[0]
            return redirect(url_for('register'))
        else:
            flash("Verification code is not valid")
    return render_template('verify.html', title='Verify New Echo', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated or (session.get('verified') is None or session['verified'] == False):
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        echo = Echo.query.filter(Echo.id == session['echo']).first()
        user = User(username=form.username.data, echo=session['echo'])
        echo.verified = True
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session.pop('verified', None)
        session.pop('echo', None)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@login_required
@app.route('/token', methods=['GET', 'POST'])
def setToken():
    form = TokenForm()
    if form.validate_on_submit():
        current_user.token = form.token.data
        db.session.commit()
        flash(f'New token has been successfully set {current_user.token}')
        return redirect(url_for('index'))
    return render_template('token.html', title='Set Token', form=form)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@ask.launch
@ask.intent('VerifiedIntent')
def init():
    #check if the echo has an account registered in the database
    existingEcho = db.session.query(Echo.id).filter(Echo.echo_id == context.System.device.deviceId, Echo.verified == True).first()
    
    message = ''
    cardText = ''
    if existingEcho is None:
        message = render_template('newUser')
        cardText = "Do you want to register a new account for this echo?"

        #store this so the yes intent can figure out what we are saying yes to
        ask_session.attributes["binaryQuestion"] = "register_account"
        ask_session.attributes["echoID"] = context.System.device.deviceId
    else:
        #Get the user account linked to the echo
        ask_session["user"] = db.session.query(User).filter(User.echo == existingEcho[0]).first()

        #check if the user has set a token
        userToken = ask_session["user"].token
        if userToken is None:
            message = render_template('noToken')
            cardText = f"Navigate to {flask_request.url_root}token and follow the instructions. Say verified when you are done."
        else:
            #set the headers for any api queries that follow
            ask_session.attributes["headers"] = {"Authorization": "Bearer " + userToken}
            canvasUser = requests.get('https://canvas.instructure.com/api/v1/users/self/profile', headers=ask_session.attributes["headers"])

            #check if user token is authorized
            if canvasUser.status_code == 401:
                message = render_template('unauthorized')
                cardText = render_template('unauthorized')
                return statement(message).simple_card(title="ChAI", content=cardText)

            canvasUserDf = pd.json_normalize(canvasUser.json())
            ask_session.attributes["userID"] = int(canvasUserDf['id'])

            welcome_msg = render_template('intro') + ', ' + ask_session["user"].username + "."
            help_msg = render_template('help')
            message = welcome_msg + ' ' + help_msg
            cardText = "Welcome to CHAI"

    return question(message).simple_card(title="ChAI", content=cardText)


@ask.intent("AMAZON.NoIntent")
@ask.intent("AMAZON.HelpIntent")
def help():

    help_msg = render_template('help')
    return question(help_msg).reprompt(help_msg)


@ask.intent("AMAZON.StopIntent")
def stop():

    stop_message = render_template('stop')
    return statement(stop_message)


@ask.intent("AMAZON.YesIntent")
def yes():
    binaryQuestion = ask_session.attributes["binaryQuestion"]
    cardText = ""

    #ugh why does python not have a switch
    if binaryQuestion == "list_assignments":
        yes_message = f"Your upcoming assignments are {ask_session.attributes['userAssignments']}"

    elif binaryQuestion == "register_account":
        existingCode = db.session.query(Echo.code).filter(Echo.echo_id == context.System.device.deviceId).first()
        if existingCode is None: 
            #create a new echo entry, and a verification code
            randomCode = randint(100000, 999999)
            newEcho = Echo(echo_id=ask_session.attributes["echoID"], code=randomCode)
            db.session.add(newEcho)
            db.session.commit()
            yes_message = f"Navigate to {addCommas(addSpaces(flask_request.url_root))}verify, and enter in the following code" + ': ' + addPeriods(addSpaces(str(randomCode)))
            yes_message += ". Say 'verified' when you are done."
            cardText = f"Navigate to {flask_request.url_root}verify and enter in the following code" + ': ' + str(randomCode)
            
        else:
            #if the user has already tried to connect once but failed to verify
            yes_message = f"Navigate to {addCommas(addSpaces(flask_request.url_root))}verify, and enter in the following code" + ': ' + addPeriods(addSpaces(str(existingCode[0])))
            yes_message += ". Say 'verified' when you are done."
            cardText = f"Navigate to {flask_request.url_root}verify and enter in the following code" + ': ' + str(existingCode[0])

    elif binaryQuestion == "post_calendar":
        files = ask_session.attributes["calendarFiles"]
        response = requests.post('https://canvas.instructure.com/api/v1/calendar_events', headers=ask_session.attributes["headers"], files=files)
        yes_message = "Your calendar has been successfully updated"
        cardText = "Your calendar has been successfully updated"

    else:
        yes_message = render_template('help')
        cardText = render_template('help')
    
    #Error: not rendering new cards?
    return question(yes_message).reprompt(yes_message).simple_card(title="ChAI", content=cardText)


@ask.intent("WhatAreMyClassesIntent")
def getClasses():
    initCourseDf()
    print(ask_session.attributes["coursedf"])
    coursedf = pd.read_json(ask_session.attributes["coursedf"])

    userCourseNames = coursedf['name']
    #get all the names of current courses in one big alexa friendly string
    classes_message = ", ".join(list(userCourseNames))
    
    return question(classes_message)


@ask.intent("WhatAreMyUpcomingAssignmentsIntent", default={'numdays': 5}, convert={'numdays': int})
def getAssignments(numdays):
    initCourseDf()
    coursedf = pd.read_json(ask_session.attributes["coursedf"])

    today = datetime.today()
    futuredays = today + timedelta(days=numdays)
    todaystr = today.strftime("%Y-%m-%d")
    futurestr = futuredays.strftime("%Y-%m-%d")

    userAssignmentsList = []
    for i in coursedf['id']:
        upcoming = requests.get(f'https://canvas.instructure.com/api/v1/users/{ask_session.attributes["userID"]}/calendar_events?per_page=100&start_date={todaystr}&end_date={futurestr}&context_codes[]=course_{i}&type=assignment', headers=ask_session.attributes["headers"])
        userAssignmentsList.append(pd.json_normalize(upcoming.json()))    
    all_upcoming_assignments = pd.concat(userAssignmentsList)
    all_upcoming_assignments = all_upcoming_assignments.sort_values(by = ['start_at'])
        
    userAssignments = ", ".join(list(all_upcoming_assignments['title'])).replace(':', '').replace('&', 'and').replace('-', ' ').replace('/', '')

    ask_session.attributes["binaryQuestion"] = "list_assignments"

    ask_session.attributes["userAssignments"] = userAssignments

    assignments_message = f"You have {len(userAssignmentsList)} assignments due soon. Do you want to know exactly what they are?"

    return question(assignments_message)


@ask.intent("WhatAreMyGradesIntent")
def getGrades():
    initCourseDf()
    coursedf = pd.read_json(ask_session.attributes["coursedf"])

    grades = [str(x["enrollments"][0]["computed_current_score"]) + " in " + x["name"] for x in coursedf.iloc]
    userGrades = ", ".join(grades)
    grades_message = f"Your grades are {userGrades}"

    return question(grades_message)


@ask.intent("SetCalendarIntent", default={'date': datetime.today().strftime('%Y-%m-%d'), 'time': '12:00'})
def setCalendar(title, date, time):
    #hard coded to EST, needs adjustment for the future if this ever gets built on
    add4 = str(int(time[:2]) + 4)
    endhour = str(int(time[:2]) + 5)
    if len(add4) == 1:
        add4 = "0" + add4
    if len(endhour) == 1:
        endhour = "0" + endhour
    time = add4 + time[2:]

    startTime = date + 'T' + add4 + time[2:] + ":00Z"
    endTime = date + 'T' + endhour + time[2:] + ":00Z"

    files = {
    'calendar_event[context_code]': (None, f'user_{ask_session.attributes["userID"]}'),
    'calendar_event[title]': (None, f'{title}'),
    'calendar_event[start_at]': (None, f'{startTime}'),
    'calendar_event[end_at]': (None, f'{endTime}'),
    }
    ask_session.attributes["calendarFiles"] = files
    ask_session.attributes["binaryQuestion"] = "post_calendar"

    return question(f"Are you sure you want set a calendar event titled {title} on {date} at {add4 + time[2:]}?")


#function to init coursedf in session attributes
def initCourseDf():
    if ask_session.attributes.get("coursedf") is None:
        courses = requests.get('https://canvas.instructure.com/api/v1/courses?per_page=100&include[]=total_scores', headers=ask_session.attributes["headers"])
        coursedf = pd.json_normalize(courses.json())
        coursedf = coursedf[list(set(["id", "name", "original_name", "course_code", "start_at", "created_at", "enrollment_term_id", "calendar.ics", "enrollments"]) & set(coursedf.columns))]
        coursedf = coursedf[coursedf['name'].notna()]
        coursedf = coursedf[coursedf['start_at'].notna()]
        coursedf['start_at'] = coursedf['start_at'].apply(lambda x: datetime.strptime(x[:-1], "%Y-%m-%dT%H:%M:%S") if type(x) == str else x)
        coursedf['name'] = coursedf['name'].apply(lambda x: x.replace(':', '-').replace('_', ' ').replace('&', 'and').split('-')[-1])
        coursedf = coursedf.drop(coursedf[coursedf['start_at'] < datetime.strptime("2021-01-01T05:00:00", "%Y-%m-%dT%H:%M:%S")].index)
        coursedf.reset_index(drop=True, inplace = True)
        ask_session.attributes["coursedf"] = coursedf.to_json()
        return True
    return False

#helper function to take a string and insert spaces between each letter so alexa pronounces the letters
def addSpaces(s):
    s = s.replace("", " ")
    s = s.replace(".", "dot")
    s = s.replace(":", "colon")
    s = s.replace("/", "slash")
    return s

#helper function that adds periods so alexa takes longer to pronounce
def addPeriods(s):
    ns = ""
    for i in range(len(s)):
        if s[i].isnumeric():
            ns = ns + s[i] + ". "
    return ns

#helper function that adds commas so alexa takes slightly longer to pronounce
def addCommas(s):
    ns = ""
    for i in range(len(s)):
        if s[i] == " ":
            ns = ns + " ," + s[i]
        else:
            ns = ns + s[i]
    return ns


if __name__ == '__main__':

    app.run(debug=True)