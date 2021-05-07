from app import app, ask, db
from app.forms import LoginForm, VerificationForm, RegistrationForm, TokenForm
from app.models import User, Echo
from flask import redirect, render_template, url_for, session, flash, request as flask_request
from flask_ask import statement, question, request, context, session as ask_session
from flask_login import current_user, login_user, logout_user, login_required
from random import randint

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
        #see if current user has a canvas api token set
        userToken = db.session.query(User.token).filter(User.echo == existingEcho[0]).first()[0]
        if userToken is None:
            message = render_template('noToken')
            cardText = f"Navigate to {flask_request.url_root}token and follow the instructions. Say verified when you are done."
        else:
            ask_session.attributes["token"] = userToken
            ask_session["user"] = db.session.query(User).filter(User.echo == existingEcho[0]).first()
            print(ask_session["user"])
            welcome_msg = render_template('intro') + ', ' + ask_session["user"].username + "."
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
    binaryQuestion = ask_session.attributes["binaryQuestion"]
    cardText = ""

    #ugh why does python not have a switch
    if binaryQuestion == "list_assignments":
        yes_message = f"Your upcoming assignments are {userAssignments}"

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
    else:
        yes_message = render_template('help')
        cardText = render_template('help')
    
    #Error: not rendering new cards?
    return question(yes_message).reprompt(yes_message).simple_card(title="ChAI", content=cardText)

@ask.intent("WhatAreMyClassesIntent")
def getClasses():
    #get all the names of current courses in one big alexa friendly string
    classes_message = ", ".join(list(userCourseNames))
    
    return question(classes_message)


@ask.intent("WhatAreMyUpcomingAssignmentsIntent")
def getAssignments():
    ask_session.attributes["binaryQuestion"] = "list_assignments"

    assignments_message = f"You have {len(userAssignmentsList)} assignments due soon. Do you want to know exactly what they are?"

    return question(assignments_message)


@ask.intent("WhatAreMyGradesIntent")
def getGrades():
    grades_message = f"Your grades are {userGrades}"

    return question(grades_message)

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