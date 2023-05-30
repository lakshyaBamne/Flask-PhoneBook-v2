###############################################################################
# MAIN FLASK APPLICATION ENRTY POINT
###############################################################################

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

import json

###############################################################################
# Initializing the WSGI application
app = Flask(
    __name__,
    template_folder='templates'
)

###############################################################################
# decorators and their handlers for the flask application

@app.route('/', methods=['GET','POST'])
def index():
    return render_template(
        'index.html'
    )

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    # when user navigates to the SIGN UP page
    if request.method == "GET":
        return render_template(
            'signup.html'
        )
    # when user submits the form to sign up as a user
    elif request.method == "POST":
        # first store the user data in two different dictionaries
        # getting the form data in form of a dictionary
        form_data = request.form.to_dict(flat=True)

        username = form_data["username"]
        password = form_data["password"]
        fullname = form_data["fullname"]
        email = form_data["email"]
        contact_number = form_data["cno"]

        # now we can store these values in the required dictionaries

        data_dict = {
            "name" : f"{fullname}",
            "email" : f"{email}",
            "contact" : f"{contact_number}",
            "contact list" : []
        }
        
        # first we should check if the same username exists or not

        with open('data/auth.json', 'r') as auth_file:
            file_content = dict(json.loads(auth_file.read()))

        if f"{username}" in file_content:
            flash("A user already exists with the given username!!")
            return redirect(url_for('signup'))
        else:
            # if given username does not exist
            # we need to add it in the auth.json file
            file_content[f"{username}"] = f"{password}"
            with open('data/auth.json', 'w') as auth_file:
                json.dump(file_content, auth_file, indent=4)

            # now we need to add the other information about the user
            # in the data file

            with open('data/data.json', 'r') as data_file:
                data_content = dict(json.loads(data_file.read()))
                
            with open('data/data.json', 'w') as data_file:
                data_content[f"{username}"] = data_dict
                json.dump(data_content, data_file, indent=4)

            # now we should redirect the new user to his user page
            # to actually use the application
            return redirect(url_for('user_page', username=f"{username}"))

@app.route('/user/<username>', methods=["GET", "POST"])
def user_page(username):
    """
        View function to show a user's Landing page
        after signup/signin
    """
    if request.method == "GET":
        # we need to get the information of the player from the data base
        with open('data/data.json', 'r') as data_file:
            data_dict = dict(json.loads(data_file.read()))
            user_dict = data_dict[f"{username}"]

        return render_template(
            'user.html',
            username=username,
            user_data=user_dict,
            to_flash_success=False
        )
    
    # now we need to handle the case when user inputs more data 
    # from his/her profile page
    elif request.method == "POST":
        form_data = request.form.to_dict(flat=True)
        
        new_name = form_data['name']
        new_email = form_data['email']
        new_contact = form_data['contact']

        new_contact_dict = {
            "name" : new_name,
            "email" : new_email,
            "contact number" : new_contact
        }

        # now we want to store this data in the contact list of the logged in user

        # we can extract the user which made the request using this following method
        endpoint_username = str(request.url).split('/')[-1]

        with open('data/data.json', 'r') as data_file:
            data_dict = dict(json.loads(data_file.read()))

        with open('data/data.json', 'w') as data_file:
            # now we can update this data dictionary
            data_dict[f"{endpoint_username}"]["contact list"].append(new_contact_dict)
            # now just dump the updated json to the same file
            json.dump(data_dict, data_file, indent=4)

            # we need to flash this message correctly
            flash("Added New contact successfully")
        
        return redirect(url_for('user_page', username=f"{endpoint_username}", to_flash_success=True))

@app.route('/signin/', methods=['GET','POST'])
def signin():
    """
        Sign in endpoint for the Users
    """
    # when the user navigates to the signin page
    if request.method == "GET":
        return render_template(
            'signin.html'
        )
    # when the user submits a request to log in to his account
    elif request.method == "POST":
        # first we need to extract the form data into variables to be used
        form_data = request.form.to_dict(flat=True)

        username = form_data["username"]
        password = form_data["password"]

        # now we need to get the data present in the auth file
        with open('data/auth.json', 'r') as auth_file:
            file_content = dict(json.loads(auth_file.read()))
        
        if username in file_content:
            # we then check password, if correct
            # then user can be signed in successfully
            if password == file_content[f"{username}"]:
                return redirect(url_for('user_page', username = username))
            else:
                # username is correct but password is wrong
                # thus we need to flash a message
                # then redirect to the sign in page
                flash("Wrong password entered!!")
                return redirect(url_for('signin'))
        else:
            # entered username does not exist
            flash("Entered username does not exist!!")
            return redirect(url_for('signin'))
        

###############################################################################
# running the application in development environment
if __name__ == '__main__':

    # cannot perform signin/signup without these 2 lines
    # cannot use flash messages without these 2 lines
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(
        host='0.0.0.0',
        debug=True
    )

###############################################################################
