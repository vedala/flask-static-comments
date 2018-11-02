from flask import redirect, request, url_for, make_response, jsonify
from static_comments_app import app
import random
import string
import github3
from datetime import datetime
import hashlib
import re
import os


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

def local_print():
    # message = request.form['message']
    # print(":".join("{:02x}".format(ord(c)) for c in message))
    today_dt = datetime.today()
    date_obj = today_dt.date()
    time_obj = today_dt.time()
    date_str = str(date_obj) + \
        ' {:0>2}:{:0>2}:{:0>2}'.format(time_obj.hour, time_obj.minute, time_obj.second)
    gravatar_hash = create_gravatar_hash(request.form['email'])
    if request.form.get('website'):
        website_value = request.form['website']
        if not website_value.startswith('http'):
            website_value = 'http://' + website_value
    else:
        website_value = ''
    # Message processing
    #     * Replace CR-LF with LF
    #     * Replace beginning of string with two spaces
    #     * Replace a series of newlines with same number of
    #       newlines but two spaces are appended after the last newline
    message = request.form['message']
    message = re.sub("\r\n", "\n", message)
    message = re.sub("^", "  ", message)
    pattern = re.compile("(\n+)")
    message = pattern.sub(r'\1  ', message)
    file_str = 'name: ' + request.form['name'] + '\n'
    file_str += 'message: |\n'
    file_str += message + '\n'
    file_str += 'date: ' + date_str + '\n'
    file_str += 'gravatar: ' + gravatar_hash + '\n'
    file_str += 'website: ' + website_value + '\n'
    directory = "~"
    filename_with_path = os.path.join(
                            os.path.expanduser(directory),
                            "submit.yml")
    f = open(filename_with_path, 'w')
    f.write(file_str)

@app.route('/comment/<submitted_token>', methods=["POST"])
def comments(submitted_token):
    github_token = app.config['GITHUB_TOKEN']
    github_username = app.config['GITHUB_USERNAME']
    github_repo_name = app.config['GITHUB_REPO_NAME']
    service_token = app.config['SERVICE_TOKEN']

    if not (github_token and github_username and github_repo_name and
            service_token):
        response = make_response(jsonify({'error': 'Internal Error'}), 500)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    if not form_has_required_fields():
        response = make_response(
            jsonify({'error': 'Required form fields not set'}), 400)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    if submitted_token != service_token:
        response = make_response(
            jsonify({'error': 'Invalid service token supplied'}), 400)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # local_print()
    # return "OK"

    gh = github3.login(token=github_token)
    repo = gh.repository(github_username, github_repo_name)

    # get sha for latest commit on master branch
    master_ref = repo.ref('heads/master')
    sha_str = master_ref.object.sha
    random_str = generate_random_str(16)
    branch_name = 'refs/heads/jekyll_comments_' + random_str
    repo.create_ref(branch_name, sha_str)

    today_dt = datetime.today()
    date_obj = today_dt.date()
    time_obj = today_dt.time()
    date_str = str(date_obj) + \
        ' {:0>2}:{:0>2}:{:0>2}'.format(time_obj.hour, time_obj.minute, time_obj.second)
    gravatar_hash = create_gravatar_hash(request.form['email'])
    if request.form.get('website'):
        website_value = request.form['website']
        if not website_value.startswith('http'):
            website_value = 'http://' + website_value
    else:
        website_value = ''

    # Message processing
    #     * This is necessary since we want to write the string as
    #       YAML's literal string (See the | character written below)
    #     * Replace CR-LF with LF
    #     * Replace beginning of string with two spaces
    #     * Replace a series of newlines with same number of
    #       newlines but two spaces are appended after the last newline
    message = request.form['message']
    message = re.sub("\r\n", "\n", message)
    message = re.sub("^", "  ", message)
    pattern = re.compile("(\n+)")
    message = pattern.sub(r'\1  ', message)

    file_str = 'name: ' + request.form['name'] + '\n'
    file_str += 'message: |\n'
    file_str += message + '\n'
    file_str += 'date: ' + date_str + '\n'
    file_str += 'gravatar: ' + gravatar_hash + '\n'
    file_str += 'website: ' + website_value + '\n'
    content = bytes(file_str, 'utf-8')

    #
    # create a file in the just created branch with data from "content"
    #
    file_name = random_str + '.yml'
    full_file_name = '_data/jekyll_comments/' + request.form['slug'] + '/' + file_name
    repo.create_file( full_file_name,
                      'Create a new comment ' + file_name,
                      content,
                      branch_name)

    repo.create_pull( 'Adding a comment', 'master',
                      github_username + ':' + branch_name,
                      'This pull request creates a data file to be used as comment')

    response = make_response(
        jsonify({'success': 'Comment submitted successfully'}), 201)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
