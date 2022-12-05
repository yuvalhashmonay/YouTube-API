from datetime import datetime
from __init__ import db
from constants import VIDEO_ID_MAX_LENGTH

class Video_request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(VIDEO_ID_MAX_LENGTH), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    successful = db.Column(db.Boolean, nullable=False, default=True)
    # comments = db.relationship('Comment', backref='video',lazy=True)  # https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete

    def get_all_links_from_comments_and_replies(self):
        all_links = []
        for comment in Comment.query.filter_by(video_id=self.video_id).all():
            all_links.extend(comment.get_links_from_the_comment_and_its_replies())
        return list(set(all_links))

    def __repr__(self):
        return str({'a': 1})

    def dictionary(self):
        comments = Comment.query.filter_by(video_id=self.video_id).all()
        return {
            'video_id': self.video_id,
            'urls_found': self.get_all_links_from_comments_and_replies(),
            'number_of_comments': len(comments),
            'comments': [comment.dictionary() for comment in comments],
        }

class Comment(db.Model):
    id = db.Column(db.String(70), primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    video_id = db.Column(db.String(20), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.Text, nullable=False)
    replies = db.relationship('Reply', backref='parent_comment', lazy=True)
    link_records = db.relationship('Link_in_comment', backref='parent_comment', lazy=True)
    # comments = db.relationship('Comment', cascade="all,delete", backref='post',lazy=True)  # https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete

    def get_links(self):
        return list(set([link_record.link for link_record in self.link_records]))

    def get_links_from_the_comment_and_its_replies(self):
        # replies_links = list(set([reply.links for reply in self.replies]))
        replies_links = []
        for reply in self.replies:
            replies_links.extend(reply.get_links())
        return list(set(self.get_links() + replies_links))

    def dictionary(self):
        return {
                'comment_id': self.id,
                'comment_author': self.username,
                'comment_time': self.time.strftime("%d/%m/%Y, %H:%M:%S"),
                'comment_text': self.text,
                'comment_replies': [reply.dictionary() for reply in self.replies]
                }

class Reply(db.Model):
    id = db.Column(db.String(70), primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.Text, nullable=False)
    comment_id = db.Column(db.String(70), db.ForeignKey('comment.id'), nullable=False)
    link_records = db.relationship('Link_in_reply', backref='parent_reply', lazy=True)

    def get_links(self):
        return list(set([link_record.link for link_record in self.link_records]))

    def dictionary(self):
        return {
                'reply_id': self.id,
                'reply_author': self.username,
                'reply_time': self.time.strftime("%d/%m/%Y, %H:%M:%S"),
                'reply_text': self.text,
                }

class Link_in_comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(2048), nullable=False)
    comment_id = db.Column(db.String(70), db.ForeignKey('comment.id'), nullable=False)

class Link_in_reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(2048), nullable=False)
    reply_id = db.Column(db.String(70), db.ForeignKey('reply.id'), nullable=False)


