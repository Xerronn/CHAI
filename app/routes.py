from app import app, ask, db
from app.forms import LoginForm
from app.models import User
from flask import render_template
from flask_ask import statement, question, session, request, context

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


@ask.launch
def init():
    #check if the echo has an account registered in the database
    isExistingUser = db.session.query(User.id).filter_by(echo_id=context.System.device.deviceId).first() is not None
    
    message = ''
    cardText = ''
    if not isExistingUser:
        message = render_template('newUser')
        cardText = "Do you want to register a new account for this echo?"
        session.attributes["binaryQuestion"] = "register_account"
    else:
        welcome_msg = render_template('intro')
        help_msg = render_template('help')
        message = welcome_msg + ' ' + help_msg
        cardText = "Welcome to CHAI"

    return question(message).simple_card(title="ChAI", content=cardText)


@ask.intent("AMAZON.HelpIntent" or "AMAZON.NoIntent")
def help():

    help_msg = render_template('help')
    print("Device ID: {}".format(len(context.System.device.deviceId)))
    return question(help_msg).reprompt(help_msg)


@ask.intent("AMAZON.StopIntent")
def stop():

    stop_message = render_template('stop')

    return statement(stop_message)


@ask.intent("AMAZON.YesIntent")
def yes():
    binaryQuestion = session.attributes["binaryQuestion"]

    #ugh why does python not have a switch
    if binaryQuestion == "list_assignments":
        yes_message = f"Your upcoming assignments are {userAssignments}"
    elif binaryQuestion == "register_account":
        yes_message = "test"
    else:
        yes_message = render_template('help')
    
    return question(yes_message)

@ask.intent("WhatAreMyClassesIntent")
def getClasses():
    #get all the names of current courses in one big alexa friendly string
    classes_message = ", ".join(list(userCourseNames))
    
    return question(classes_message)


@ask.intent("WhatAreMyUpcomingAssignmentsIntent")
def getAssignments():
    session.attributes["binaryQuestion"] = "list_assignments"

    assignments_message = f"You have {len(userAssignmentsList)} assignments due soon. Do you want to know exactly what they are?"

    return question(assignments_message)


@ask.intent("WhatAreMyGradesIntent")
def getGrades():
    grades_message = f"Your grades are {userGrades}"

    return question(grades_message)


if __name__ == '__main__':

    app.run(debug=True)