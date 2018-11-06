# Flask Static Comments

This application is part of the jekyll-comments commenting system
which is described in detail at jekyll-comments (link)

The application accepts comment submissions from Jekyll-generated
static websites and submits the comment information to the user's
github repository.


### Deploy
  * You can deploy this application on a host of your choice.
### Environment variables

Following environment variables are required by the application

* GITHUB_TOKEN - Personal access token with "repo" scope for the Github account
* GITHUB_USERNAME - Username of Github account which owns the repository
* GITHUB_REPO_NAME - Repository name which is your Jekyll blog
* SERVICE_TOKEN - A unique token that you generate


