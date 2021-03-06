from flask import redirect, request, url_for, make_response, jsonify, \
    render_template
from static_comments_app import app, db
from static_comments_app.models import Comment
import random
import string
import github3
from datetime import datetime
import hashlib
import re
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
# Following is a library from sendgrid, not the python http.client
from python_http_client import exceptions as sg_exceptions
from pykismet3 import Akismet, AkismetError


def generate_random_str(length):
    return ''.join(random.SystemRandom().choice(
        string.ascii_lowercase + string.digits) for _ in range(int(length)))

def form_has_required_fields():
    return 'name' in request.form and \
        'email' in request.form and \
        'message' in request.form and \
        'slug' in request.form

def create_gravatar_hash(email):
    m = hashlib.md5()
    m.update(email.strip().lower().encode("utf-8"))
    return m.hexdigest()

def get_current_datetime_str(inp_datetime):
    date_obj = inp_datetime.date()
    time_obj = inp_datetime.time()
    date_str = str(date_obj) + \
        ' {:0>2}:{:0>2}:{:0>2}'.format(time_obj.hour,
                                       time_obj.minute, time_obj.second)
    return date_str

def send_email(sendgrid_api_key, email_to, email_str):
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email("no_reply@flask_static_comments.com")
    to_email = Email(email_to)
    subject = "A comment was submitted on your blog"
    content = Content("text/html", email_str)
    mail = Mail(from_email, subject, to_email, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except sg_exceptions.HTTPError as e:
        app.logger.info("Error encountered when sending email: {}".format(e.body))
        return False

    return True

def website_field_check_scheme(website_value):
    #
    # Prepend "http://" if no schema present in url entered by the user.
    #
    # This is required, since Jekyll treats schema-less url as relative
    # urls

    website_return_value = website_value
    if website_value != '':
        if not website_value.startswith('http'):
            website_return_value = 'http://' + website_value
    return website_return_value

def process_message(submitted_message):
    # Message processing
    #     * This is necessary since we want to write the message as
    #       YAML's literal string (See the | character written below)
    #     * Replace CR-LF with LF
    #     * Replace beginning of string with two spaces
    #     * Replace a series of newlines with same number of
    #       newlines but two spaces are appended after the last newline
    message = submitted_message
    message = re.sub("\r\n", "\n", message)
    message = re.sub("^", "  ", message)
    pattern = re.compile("(\n+)")
    message = pattern.sub(r'\1  ', message)

    # prepend YAML literal string indicator
    message = "|\n" + message
    return message

def generate_file_str(name, message, date_str, gravatar_hash, website_value):
    file_str = 'name: ' + name + '\n'
    file_str += 'message: ' + message + '\n'
    file_str += 'date: ' + date_str + '\n'
    file_str += 'gravatar: ' + gravatar_hash + '\n'
    file_str += 'website: ' + website_value + '\n'
    return file_str

def generate_email_str(name, message, date_str, email, website_value, slug):
    email_str = '<pre>'
    email_str += 'blog: ' + slug + '<br><br>'
    email_str += 'name: ' + name + '<br>'
    email_str += 'message: ' + message + '<br>'
    email_str += 'date: ' + date_str + '<br>'
    email_str += 'email: ' + email + '<br>'
    email_str += 'website: ' + website_value + '<br></pre>'
    return email_str

def create_github_pull_request(github_token, github_username, \
    github_repo_name, slug, name, message, date_str, email, \
    website):
    #
    # Authenticate the github account and get the repository object
    #
    gh = github3.login(token=github_token)
    try:
        repo = gh.repository(github_username, github_repo_name)
    except github3.exceptions.GitHubException as e:
        app.logger.info("Error in call to github3 {} method: {}".format(
                                                "repository()", str(e)))
        return False

    #
    # get sha for latest commit on master branch
    #
    try:
        master_ref = repo.ref('heads/master')
    except github3.exceptions.GitHubException as e:
        app.logger.info("Error in call to github3 {} method: {}".format(
                                             "repository ref()", str(e)))
        return False

    sha_str = master_ref.object.sha

    #
    # Create a branch on the repo
    #
    random_str = generate_random_str(16)
    branch_name = 'refs/heads/jekyll_comments_' + random_str
    try:
        repo.create_ref(branch_name, sha_str)
    except github3.exceptions.GitHubException as e:
        app.logger.info("Error in call to github3 {} method: {}".format(
                                     "repository create_ref()", str(e)))
        return False

    gravatar_hash = create_gravatar_hash(email)
    file_str = generate_file_str(name, message, date_str, gravatar_hash,
                                 website)
    content = bytes(file_str, 'utf-8')

    #
    # create a file in the just created branch with data from variable "content"
    #
    file_name = random_str + '.yml'
    full_file_name = '_data/jekyll_comments/' + slug + '/' + file_name
    try:
        repo.create_file( full_file_name,
                        'Create a new comment ' + file_name,
                        content,
                        branch_name)
    except github3.exceptions.GitHubException as e:
        app.logger.info("Error in call to github3 {} method: {}".format(
                                  "repository create_file()", str(e)))
        return False

    #
    # Create pull request
    #
    try:
        repo.create_pull( 'Comment submission', 'master',
            github_username + ':' + branch_name,
            'This pull request creates a data file to be used as comment')
    except github3.exceptions.GitHubException as e:
        app.logger.info("Error in call to github3 {} method: {}".format(
                                    "repository create_pull()", str(e)))
        return False

    return True

def spam_check(user_ip, user_agent, referrer, name, email, message, \
               website, post_url):

    comment_type = "comment"

    akismet_api_key = app.config['AKISMET_API_KEY']
    if not akismet_api_key:
        app.logger.info(
            "Required environment variable AKISMET_API_KEY missing")
        return (False, None)

    a = Akismet(blog_url=post_url,
                api_key=akismet_api_key,
                user_agent=user_agent)

    try:
        is_spam = a.check({'user_ip': user_ip,
            'user_agent': user_agent,
            'referrer': referrer,
            'comment_type': comment_type,
            'comment_author': name,
            'comment_author_email': email,
            'comment_content': message,
            'website': website
        })
    except AkismetError as e:
        app.logger.info(
            "Error in call to pykismet3.check(): {}".format(str(e)))
        return (False, None)

    return (True, is_spam)

def send_spam_email(sendgrid_api_key, email_to, email_str, comment_id):
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email("no_reply@flask_static_comments.com")
    to_email = Email(email_to)
    subject = "A comment was submitted on your blog"
    email_str += "<br>This comment has been identified as spam, \
                 click the link below to mark the comment as valid.<br><br>"
    scheme = 'http' if app.debug else 'https'
    email_str += render_template('is_spam.html', comment_id=comment_id,
                                 scheme=scheme)
    content = Content("text/html", email_str)
    mail = Mail(from_email, subject, to_email, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except sg_exceptions.HTTPError as e:
        app.logger.info("Error encountered when sending email: {}".format(e.body))
        return False

    return True

def send_not_spam_email(sendgrid_api_key, email_to, email_str, comment_id):
    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
    from_email = Email("no_reply@flask_static_comments.com")
    to_email = Email(email_to)
    subject = "A comment was submitted on your blog"
    email_str += "<br>This comment was identified as a valid comment, \
                 click the link below to mark the comment as spam.<br><br>"
    scheme = 'http' if app.debug else 'https'
    email_str += render_template('is_valid.html', comment_id=comment_id,
                                 scheme=scheme)
    content = Content("text/html", email_str)
    mail = Mail(from_email, subject, to_email, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except sg_exceptions.HTTPError as e:
        app.logger.info("Error encountered when sending email: {}".format(e.body))
        return False

    return True

def check_email_env_variables():
    email_to = app.config['EMAIL_TO']
    sendgrid_api_key = app.config['SENDGRID_API_KEY']
    return email_to and sendgrid_api_key

def check_spam_env_variables():
    akismet_api_key = app.config['AKISMET_API_KEY']
    return akismet_api_key and check_email_env_variables()

@app.route('/mark_it_spam/<comment_id>')
def mark_it_spam(comment_id):
    comment = Comment.query.filter_by(
                                id=comment_id, mark_for_delete=False).first()
    if comment is None:
        response = make_response(
            jsonify({'not found': 'No such comment'}), 404)
    else:
        a = Akismet(blog_url=comment.post_url,
                    user_agent=comment.user_agent)
        a.api_key = app.config['AKISMET_API_KEY']

        a.submit_spam({'user_ip': comment.user_ip,
            'user_agent': comment.user_agent,
            'referrer': comment.referrer,
            'comment_type': comment.comment_type,
            'comment_author': comment.comment_author,
            'comment_author_email': comment.comment_author_email,
            'comment_content': comment.comment_content,
            'website': comment.website
        })
        comment.mark_for_delete = True
        db.session.commit()
        app.logger.info("The comment was submitted as spam")
        response = make_response(
            jsonify({'success': 'The comment was submitted as spam'}), 200)

    return response

@app.route('/mark_it_valid/<comment_id>')
def mark_it_valid(comment_id):
    comment = Comment.query.filter_by(
                                id=comment_id, mark_for_delete=False).first()
    if comment is None:
        response = make_response(
            jsonify({'not found': 'No such comment'}), 404)
    else:
        a = Akismet(blog_url=comment.post_url,
                    user_agent=comment.user_agent)
        a.api_key = app.config['AKISMET_API_KEY']

        a.submit_ham({'user_ip': comment.user_ip,
            'user_agent': comment.user_agent,
            'referrer': comment.referrer,
            'comment_type': comment.comment_type,
            'comment_author': comment.comment_author,
            'comment_author_email': comment.comment_author_email,
            'comment_content': comment.comment_content,
            'website': comment.website
        })

        date_str = get_current_datetime_str(comment.submit_datetime)
        name = comment.comment_author
        email = comment.comment_author_email
        website_value = comment.website
        message = comment.comment_content
        slug = comment.slug

        github_token = app.config['GITHUB_TOKEN']
        github_username = app.config['GITHUB_USERNAME']
        github_repo_name = app.config['GITHUB_REPO_NAME']

        if not create_github_pull_request(github_token, github_username, \
            github_repo_name, slug, name, message, date_str, \
            email, website_value):
            app.logger.info("Problem encountered during creation of pull request")
            response = make_response(jsonify({'error': 'Internal Error'}), 500)
        else:
            app.logger.info("Pull request created successfully")
            comment.mark_for_delete = True
            db.session.commit()
            response = make_response(
                jsonify({'success': 'The comment was submitted as valid'}), 200)

    return response

def save_comment_to_database(user_ip, user_agent, referrer, name, \
                 email, message, website, slug, post_url, submit_datetime):
    comment_type = "comment"

    comment = Comment(user_ip=user_ip, user_agent=user_agent,
        referrer=referrer, comment_type=comment_type, comment_author=name,
        comment_author_email=email, comment_content=message, website=website,
        slug=slug, post_url=post_url, submit_datetime=submit_datetime)
    db.session.add(comment)
    db.session.commit()

    return comment.id

@app.route('/comment/<submitted_token>', methods=["POST"])
def comments(submitted_token):
    github_token = app.config['GITHUB_TOKEN']
    github_username = app.config['GITHUB_USERNAME']
    github_repo_name = app.config['GITHUB_REPO_NAME']
    service_token = app.config['SERVICE_TOKEN']

    if not (github_token and github_username and github_repo_name and
            service_token):
        response = make_response(jsonify({'error': 'Internal Error'}), 500)
        return response

    if not form_has_required_fields():
        response = make_response(
            jsonify({'error': 'Required form fields not set'}), 400)
        return response

    if submitted_token != service_token:
        response = make_response(
            jsonify({'error': 'Invalid service token supplied'}), 400)
        return response

    form_name = request.form['name']
    submit_datetime = datetime.today()
    date_str = get_current_datetime_str(submit_datetime)
    form_email = request.form['email']
    website_value = website_field_check_scheme(request.form.get('website', ''))
    message = process_message(request.form['message'])
    form_slug = request.form['slug']

    #
    # We are using akismet spam prevention. Akismet provides spam check call
    # returns a boolean value identify a submission as either spam or valid.
    # In addition, Akismet requires that we submit missed spam and false
    # positives (a false positive is a submission that Aksimet identifies as
    # spam but is actually a valid submission).
    #
    # To keep the application simple, we are using links within email to
    # submit missed spam and false positives.
    #
    email_notification = app.config['EMAIL_NOTIFICATION']
    if email_notification:
        email_notification = email_notification.lower()

    spam_prevention = app.config['SPAM_PREVENTION']
    if spam_prevention:
        spam_prevention = spam_prevention.lower()

    if spam_prevention == "yes":
        #
        # Check for spam and send email with links as described above
        #

        if not check_spam_env_variables():
            app.logger.info("Required environment variables missing"
                            " for spam prevention")
            response = make_response(jsonify({'error': 'Internal Error'}), 500)
        else:
            user_ip = request.remote_addr
            user_agent = str(request.user_agent)
            referrer = request.environ.get('HTTP_REFERER') or "unknown"
            post_url = request.form['post_url']
            retval, is_spam = spam_check(user_ip, user_agent, referrer,
                form_name, form_email, message, website_value, post_url)
            if not retval:
                app.logger.info("Problem encountered during spam check")
                response = make_response(
                    jsonify({'error': 'Internal Error'}), 500)
            else:
                comment_id = save_comment_to_database(user_ip, user_agent,
                    referrer, form_name, form_email, message, website_value,
                    form_slug, post_url, submit_datetime)
                if is_spam:
                    email_str = generate_email_str(request.form['name'], message,
                        date_str, request.form['email'], website_value,
                        request.form['slug'])
                    retval = send_spam_email(app.config['SENDGRID_API_KEY'],
                                            app.config['EMAIL_TO'],
                                            email_str, comment_id)
                    if not retval:
                        app.logger.info("Problem encountered in send_spam_email")
                        response = make_response(
                            jsonify({'error': 'Internal Error'}), 500)
                    else:
                        response = make_response(jsonify(
                            {'success': 'Comment submitted successfully'}), 201)
                else:
                    email_str = generate_email_str(request.form['name'], message,
                        date_str, request.form['email'], website_value,
                        request.form['slug'])
                    retval = send_not_spam_email(app.config['SENDGRID_API_KEY'],
                                            app.config['EMAIL_TO'],
                                            email_str, comment_id)
                    if not retval:
                        app.logger.info("Problem encountered in send_email")

                    if not create_github_pull_request(github_token, github_username, \
                        github_repo_name, form_slug, form_name, message, date_str, \
                        form_email, website_value):
                        app.logger.info("Problem encountered during creation of pull request")
                        response = make_response(jsonify({'error': 'Internal Error'}), 500)
                    else:
                        response = make_response(
                            jsonify({'success': 'Comment submitted successfully'}), 201)
    elif email_notification == "yes":
        #
        # Send a regular email notification (without spam-related links)
        #
        if not check_email_env_variables():
            app.logger.info("Required environment variables missing"
                  " for email notification - regular email notification")
        else:
            email_str = generate_email_str(request.form['name'], message,
                date_str, request.form['email'], website_value,
                request.form['slug'])
            retval = send_email(app.config['SENDGRID_API_KEY'],
                            app.config['EMAIL_TO'],
                            email_str)
            if not retval:
                app.logger.info("Problem encountered in send_email")

            if not create_github_pull_request(github_token, github_username, \
                github_repo_name, form_slug, form_name, message, date_str, \
                form_email, website_value):
                app.logger.info("Problem encountered during creation of pull request")
                response = make_response(jsonify({'error': 'Internal Error'}), 500)
            else:
                response = make_response(
                    jsonify({'success': 'Comment submitted successfully'}), 201)
    else:
        if not create_github_pull_request(github_token, github_username, \
            github_repo_name, form_slug, form_name, message, date_str, \
            form_email, website_value):
            app.logger.info("Problem encountered during creation of pull request")
            response = make_response(jsonify({'error': 'Internal Error'}), 500)
        else:
            response = make_response(
                jsonify({'success': 'Comment submitted successfully'}), 201)

    return response
