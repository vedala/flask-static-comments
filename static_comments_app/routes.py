from flask import redirect, request, flash, url_for, session
from static_comments_app import app, db
from static_comments_app.forms import LoginForm, RegistrationForm, \
    JekyllCommentAuthorize, JekyllCommentRepo
import os
import random
import string
import github3
from datetime import datetime


def generate_random_str(length):
    return ''.join(random.SystemRandom().choice(
        string.ascii_lowercase + string.digits) for _ in range(int(length)))

@app.route('/comment/<api_token>', methods=["POST"])
def comments(api_token):
    user = User.query.filter_by(api_token=api_token).first()
    if user.github_access_token:
        # private repo
        # use  user.access_token for authorization
        github_token = user.github_access_token
    else:
        # public repo 
        # use GITHUB_TOKEN from environment for authorization
        github_token = os.environ.get('GITHUB_TOKEN')

    gh = github3.login(token=github_token)
    repo = gh.repository(user.github_username, user.github_repo_name)

    # get sha for latest commit on master branch
    master_ref = repo.ref('heads/master')
    sha_str = master_ref.object.sha
    random_str = generate_random_str(16)
    branch_name = 'refs/heads/static_comments_app_' + random_str
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
    file_str += 'parent:' + '\n'
    content = bytes(file_str, 'utf-8')

    # create a file in the just created branch with data from "content"
    file_name = random_str + '.yml'
    full_file_name = '_data/static_comments_app/' + request.form['slug'] + '/' + file_name
    repo.create_file( full_file_name,
                      'Create a new comment ' + file_name,
                      content,
                      branch_name)

    repo.create_pull( 'Adding a comment', 'master',
                      user.github_username + ':' + branch_name,
                      'This pull request creates a data file to be used as comment')

    referer = request.headers['Referer']
    return redirect(referer)
