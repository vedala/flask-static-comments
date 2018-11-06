# Flask Static Comments

This application is part of the jekyll-comments commenting system
which is described in at [jekyll-comments](https://github.com/vedala/jekyll-comments.git). If you are just starting with this system you should read instructions at `jekyll-comments` repository.

The application in this repository is a flask application accepts comment submissions from Jekyll-generated static websites and submits the comment information to the user's
github repository as a pull request.


## Environment variables

Following environment variables are required by the application.

| Environment Variable | Description |
| --- | --- |
| `GITHUB_TOKEN` | Personal access token with "repo" scope for the Github account that owns the repository.
| `GITHUB_USERNAME` | Username of Github account that owns the repository.
| `GITHUB_REPO_NAME` | Repository name of the jekyll blog.
| `SERVICE_TOKEN` | A unique token that you generate for your deployment of the server.
| `FLASK_APP` | The name of the flask application package within this repository.



## Test on localhost

To test the commenting system locally, you can clone this repository and run the application. The steps to run the application are (you will have to set the environment variables before running 

### Clone the repository

```
$ git clone https://github.com/vedala/flask-static-comments.git


```

### Set environment variables

Set the following environment variables (details in next section):

```
export GITHUB_TOKEN=XXXXXX
export GITHUB_USERNAME=XXXXXX
export GITHUB_REPO_NAME=XXXXXX
export SERVICE_TOKEN=XXXXXX
export FLASK_APP=static_comments_app
```

### Setup python virtual environment for the application

Setup python virtual environment (this step requires python 3.X. If your computer does
have python 3.X installed, you will have to install it using instructions on python
website). I recommend installing the latest python version - 3.7.X).

```
$ cd flask-static-comments

$ python3 -m venv venv

$ source venv/bin/activate
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

The application should now be running on `localhost:5000`.


## Deploy using a hosting provider

Please follow the specific hosting providers' instructions on deploying the application.

The endpoint provided by this application will be consumed by the front-end via
an ajax call. A few items to keep in mind:

* The server will treat the request as CSS, so you need set the CORS headers. The application already sets the CORS header.
* Use `https` and use a real certificate.
