# Flask Static Comments

This application is part of the jekyll-comments commenting system
which is described in detail at [jekyll-comments](https://github.com/vedala/jekyll-comments.git). If you are just starting with this system you should read instructions at `jekyll-comments` repository first.

The application in this repository is a flask application that accepts comment submissions from Jekyll-generated static websites and submits the comment information to the user's
github repository as a pull request.


## Configuration

The application is configured setting the following environment variables:


### Required configuration

The following environment variables are required by the application:

| Environment Variable | Description |
| --- | --- |
| `GITHUB_TOKEN` | Personal access token with "repo" scope for the Github account that owns the repository.
| `GITHUB_USERNAME` | Username of Github account that owns the repository.
| `GITHUB_REPO_NAME` | Repository name of the jekyll blog.
| `SERVICE_TOKEN` | A unique token that you generate for your deployment of the server.
| `FLASK_APP` | The name of the flask application package within this repository.


The following optional configuration can be set to enable email notifications on
comment submission:

### Email notifications on comment submissions

| Environment Variable | Description |
| --- | --- |
|`EMAIL_NOTIFICATION`| To enable email notifications set this variable's value to "yes". Default is "no".|
|`EMAIL_TO`|The email address for recieving notifications.|
|`SENDGRID_API_KEY`|API key of Sendgrid account.|


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

## Test on localhost

To test the commenting system locally, you can clone this repository and run the application. The steps to run the application are described below.

### Clone the repository

```
$ git clone https://github.com/vedala/flask-static-comments.git
```

### Set environment variables

Set the following environment variables:

```
export GITHUB_TOKEN=XXXXXX
export GITHUB_USERNAME=XXXXXX
export GITHUB_REPO_NAME=XXXXXX
export SERVICE_TOKEN=XXXXXX
export FLASK_APP=static_comments_app
```

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


## Deploy using a hosting provider

Please follow the specific hosting providers' instructions on deploying the application.

The endpoint provided by this application will be consumed by the front-end via
an ajax call.

A few items to keep in mind:

* The server will treat the request as Cross-Site Script, so you need set the CORS headers. The application already sets the CORS header. But if you want you deployment to be fronted by a webserver such as Apache or Nginx, then you can set CORS headers in Apache/Nginx.
* Use a real certificate if you want to use `https`. While we can choose to ignore certificate errors when accessing a web application, when accessing api endpoints via ajax calls, the front-end will fail silently.


# Changes for spam prevention

## jekyll_comments_form.html modified to include page_url hidden field
