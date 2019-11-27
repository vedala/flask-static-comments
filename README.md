# Flask Static Comments

This application is part of the jekyll-comments commenting system
which is described in detail at [jekyll-comments](https://github.com/vedala/jekyll-comments.git). If you are just starting with this system you should read instructions at `jekyll-comments` repository first.

The application in this repository is a flask application that accepts comment submissions from Jekyll-generated static websites and submits the comment information to the user's
github repository as a pull request.

## Inspiration

This project is inspired by and derived from Damien Guard's project that is described
in detail at the blog post [here](https://damieng.com/blog/2018/05/28/wordpress-to-jekyll-comments)
and in the two github repositories: [here](https://github.com/damieng/jekyll-blog-comments) and
[here](https://github.com/Azure-Functions/jekyll-blog-comments).

## Basic functionality

You can be deploy the application and update your static blog repository to submit comments to
the application without using any of the optional features. The basic functionality is creation
of a comment submission as a pull request of the blog repository.


## Optional features

### Email notifications of application errors

Enable this feature to receive email notifications if you application crashes. This is
useful as you will be immediately informed in case the deployed application crashes due to any reason.


### Email notifications of comment submissions

Enable this feature to receive email notifications on comment submissions.


### Spam Prevention

Enable this feature to prevent spam submissions. The application uses Akismet service to catch
spam.


## Test on localhost

To test the commenting system locally, you can clone this repository and run the application. The steps to run the application are described below.

### Clone the repository

```
$ git clone https://github.com/vedala/flask-static-comments.git
```

### Set the required environment variables

Set the following required environment variables:

```
export GITHUB_TOKEN=XXXXXX
export GITHUB_USERNAME=XXXXXX
export GITHUB_REPO_NAME=XXXXXX
export SERVICE_TOKEN=XXXXXX
export FLASK_APP=static_comments_app
```

Details of each environment variable are described in the configuration section below.


### Setup optional features

To enable any of the optional features, set the environment variables required for the
feature to appropriate values. More details in the Configuration section below.


### Setup python virtual environment

Setup python virtual environment (this step requires python 3.X. If your computer does
not have python 3.X installed, you will have to install it using instructions on python
website. I recommend installing the latest python version - 3.7.X).

```
$ cd flask-static-comments

$ python3 -m venv myenv

$ source myenv/bin/activate
```

### Download python packages used by the application

```
$ pip install -r requirements.txt
```

### Start the application

Run the following command:

```
$ flask run
```

The application should now be running on `http://localhost:5000`.


### Upate _config.yml on your schema repository

This is described further in [`jekyll-comments`](https://github.com/vedala/jekyll-comments#update-your-_configyml-with-server-details) repository.


## Configuration

The application is configured by setting the following environment variables:


### Required configuration

The following environment variables are required by the application:

| Environment Variable | Description |
| --- | --- |
| `GITHUB_TOKEN` | Personal access token with "repo" scope for the Github account that owns the repository.
| `GITHUB_USERNAME` | Username of Github account that owns the repository.
| `GITHUB_REPO_NAME` | Repository name of the jekyll blog.
| `SERVICE_TOKEN` | A unique token that you generate for your deployment of the server. You can generate a token using a service such as [this](https://www.uuidgenerator.net/).
| `FLASK_APP` | The name of the flask application package within this repository.


### Email notifications on application errors

| Environment Variable | Description |
| --- | --- |
|`LOGGING_EMAIL_NOTIFY`| Set this variable's value to "yes" to receive emails on application errors. Default is "no".|
|`MAIL_SERVER`| Set to your choice of SMTP server. For example, `smtp.sendgrid.net`.|
|`MAIL_PORT`| The port to be used on mail server. A common setting is `587`.|
|`MAIL_USE_TLS`| Set to `1` to use SSL or `0` for no SSL.|
|`MAIL_USERNAME`| The username of the account to be used for sending emails. If using Sendgrid, set this to `apikey`.|
|`MAIL_PASSWORD`| The password of the account to be used for sending emails. If using Sendgrid, the value of this variable is your Sendgrid account's API key.|
|`LOGGING_EMAIL_TO`| Email address of the recipient to receive notifications.|


### Email notifications on comment submissions

| Environment Variable | Description |
| --- | --- |
|`EMAIL_NOTIFICATION`| To enable email notifications, set this variable's value to "yes". Default is "no".|
|`EMAIL_TO`| The email address for recieving notifications.|
|`SENDGRID_API_KEY`| API key of Sendgrid account.|


### Spam prevention

The application uses Aksimet service to catch spam. 

| Environment Variable | Description |
| --- | --- |
|`SPAM_PREVENTION`| To enable spam prevention, set this variable's value to "yes". Default is "no".|
|`AKISMET_API_KEY`| Akismet API Key. Signup for the service [here](https://akismet.com/).

Akismet requires that users submit any inaccurate spam detection to Akismet to improve
accuracy. The flask-static-comments application uses email as the interface for
reporting to Akismet. Because email is used, the spam prevention feature uses environment
variables from the previous feature. The environment variables `EMAIL_TO` and
`SENDGRID_API_KEY` are required. The spam prevention feature overrides the "email notifications
on comment submissions" feature. Therefore, you will receive spam email notifications even
if the `EMAIL_NOTIFICATION` environment variable is set to "no".

_Spam Prevention Workflow_

_1. A comment submission identified as spam_

* You receive an email notification with a link at the bottom that says `Not spam, this is a valid comment`. At this stage, a pull request is not yet created on your repository.
* No action is needed if the comment submission is indeed spam.
* Click the link if the comment submission is not spam but a valid submission. Clicking the link will create a pull request on your repository. Clicking the link also makes an API call Akismet to report the inaccuracy.

_2. A comment submission identified as valid (not spam)_

* You receive an email notification information you that a comment was submitted and it was detected as a valid submission. At this stage, a pull request is already created on your repository.
* At the bottom of the email, there is a link that says `Mark this as spam`.
* No action is needed if the comment submission is a valid submission.
* Click the link if the comment submission was inaccurately detected as valid, although it is in fact spam. Clicking the link will report the inaccuracy to Akismet.
* Note that clicking the link will not delete the pull request. You will have to close the pull request without merging to discard the comment.


## Deploy using a hosting provider

Please follow the specific hosting providers' instructions on deploying the application.

The endpoint provided by this application will be consumed by the front-end via
an ajax call.

A few items to keep in mind:

* The server will treat the request as Cross-Site Script, so CORS headers are required. The application already sets the CORS header. But if you want you deployment to be fronted by a webserver such as Apache or Nginx, then you can set CORS headers in Apache/Nginx.
* Use a real certificate if you want to use `https`. While we can choose to ignore certificate errors when using interactive web applications, when accessing api endpoints via ajax calls, the ajax call will fail silently.
