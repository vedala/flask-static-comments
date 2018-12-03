from static_comments_app import app, db

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_ip = db.Column(db.String(64))
    user_agent = db.Column(db.String(256))
    referrer = db.Column(db.String(256))
    comment_type = db.Column(db.String(32))
    comment_author = db.Column(db.String(64))
    comment_author_email = db.Column(db.String(128))
    comment_content = db.Column(db.String(512))
    website = db.Column(db.String(64))
    slug = db.Column(db.String(128))
    post_url = db.Column(db.String(128))

    def __repr__(self):
        return '<Comment {}>'.format(self.id)
