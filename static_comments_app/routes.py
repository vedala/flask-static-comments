from flask import redirect, request, url_for, make_response, jsonify
from static_comments_app import app
import random
import string
import github3
from urllib.parse import urljoin
from datetime import datetime


def generate_random_str(length):
    return ''.join(random.SystemRandom().choice(
        string.ascii_lowercase + string.digits) for _ in range(int(length)))

def form_has_required_fields():
    return 'name' in request.form and \
        'email' in request.form and \
        'message' in request.form and \
        'slug' in request.form and \
        'submitting_site' in request.form

def construct_redirect_url(scheme, submitting_site, redirect_to):
    return urljoin(scheme + "://" + submitting_site, redirect_to)

@app.route('/comment', methods=["POST"])
def comments():
    github_token = app.config['GITHUB_TOKEN']
    github_username = app.config['GITHUB_USERNAME']
    github_repo_name = app.config['GITHUB_REPO_NAME']
    expected_site = app.config['EXPECTED_SITE']

    if not (github_token and github_username and github_repo_name
                                                        and expected_site):
        return make_response(jsonify({'error': 'Internal Error'}), 500)

    if not form_has_required_fields():
        return make_response(
            jsonify({'error': 'Required form fields not set'}), 400)

    submitting_site = request.form['submitting_site']

    if submitting_site != expected_site:
        return make_response(
            jsonify({'error':
                'Site {} cannot submit comments to this service'.format(
                                                            submitting_site)}),
            400)

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
    file_str = 'name: ' + request.form['name'] + '\n'
    file_str += 'email: ' + request.form['email'] + '\n'
    file_str += 'message: ' + request.form['message'] + '\n'
    file_str += 'date: ' + date_str + '\n'
    content = bytes(file_str, 'utf-8')

    # create a file in the just created branch with data from "content"
    file_name = random_str + '.yml'
    full_file_name = '_data/jekyll_comments/' + request.form['slug'] + '/' + file_name
    repo.create_file( full_file_name,
                      'Create a new comment ' + file_name,
                      content,
                      branch_name)

    repo.create_pull( 'Adding a comment', 'master',
                      github_username + ':' + branch_name,
                      'This pull request creates a data file to be used as comment')

    if request.form.get('redirect_to'):
        redirect_url = construct_redirect_url(request.scheme, submitting_site,
                                              request.form['redirect_to'])
        return redirect(redirect_url)

    return '', 201
