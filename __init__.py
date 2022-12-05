from flask import Flask, request, make_response, jsonify
from youtube_data_api import get_video_comments_response
from flask_sqlalchemy import SQLAlchemy
from models import *
from dateutil import parser
from constants import VIDEO_ID_MAX_LENGTH, PAGE_TOKEN_MAX_LENGTH, URL_REGEX, SECRET_KEY
import re
import html
import googleapiclient
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # check why
app.config['JSON_SORT_KEYS'] = False # disable alphabetical sorting of json keys
db = SQLAlchemy(app)

# basedir = os.path.abspath(os.path.dirname(__file__))
# @app.before_first_request
# def before_first_request():
#     db.create_all()
#     db.session.commit()




def get_urls(string):
    # from  https://www.geeksforgeeks.org/python-check-url-string/
    regex = URL_REGEX
    url = re.findall(regex, string)
    return list(set([x[0] for x in url]))


def add_and_commit_record(record):
    db.session.add(record)
    db.session.commit()

def save_request(response, video_id):
    successful = not isinstance(response, googleapiclient.errors.HttpError)
    video_request = Video_request(video_id=video_id, successful=successful)
    add_and_commit_record(video_request)
    return video_request

def save_link_in_comment(url, comment_record):
    # link_in_comment_record = Link_in_comment(link=url, comment_id=comment_id)
    link_in_comment_record = Link_in_comment(link=url, parent_comment=comment_record)
    add_and_commit_record(link_in_comment_record)


def save_new_comment_links(urls, comment_record):
    for url in urls:
        if Link_in_comment.query.filter_by(link=url, comment_id=comment_record.id).first() is None:
            link_in_comment_record = Link_in_comment(link=url, parent_comment=comment_record)
            db.session.add(link_in_comment_record)
    db.session.commit()

def save_reply_links(urls, reply_record):
    for url in urls:
        if Link_in_reply.query.filter_by(link=url, reply_id=reply_record.id ).first() is None:
            link_in_reply_record = Link_in_reply(link=url, parent_reply=reply_record)
            db.session.add(link_in_reply_record)
    db.session.commit()

def save_comment_if_it_is_new(username, time, text, urls, comment_id, video_id):
    comment_record = Comment.query.get(comment_id)
    if comment_record is None:
        comment_record = Comment(id=comment_id, username=username, video_id=video_id, text=text, time=time)
        add_and_commit_record(comment_record)
    save_new_comment_links(urls, comment_record)
    return comment_record

def save_reply_if_it_is_new(username, time, text, urls, reply_id, comment_record):
    reply_record = Reply.query.get(reply_id)
    if reply_record is None:
        reply_record = Reply(id=reply_id, username=username, text=text, time=time, parent_comment=comment_record)
        add_and_commit_record(reply_record)
    save_reply_links(urls, reply_record)
    return reply_record


# def save_reply(username, time, text, urls, video_id, comment_id)


def get_comment_or_reply_values(comment_details):
    username = comment_details['authorDisplayName']
    time = parser.parse(comment_details['publishedAt'])
    text = html.unescape(comment_details['textDisplay'])
    urls = get_urls(text)
    return username, time, text, urls

def create_failure_message(response):
        print(response)
        if response.status_code == 403:
            message = "The video has disabled comments"
        elif response.status_code == 404:
            message = "The video could not be found."
        else:
            message = response.reason
        return make_response(jsonify(message), response.status_code)

def validate_params(video_id, max_results, page_token):
    review = ""
    status_code = 200
    if video_id is None:
        review  += "Please provide a video id.\n"
        status_code = 400
    elif len(video_id) > VIDEO_ID_MAX_LENGTH:  # do i need to make sure it's a string?
        review += f"The video id length cannot exceed {VIDEO_ID_MAX_LENGTH}.\n"
        status_code = 400
    if page_token and len(page_token) > PAGE_TOKEN_MAX_LENGTH:
        review += f"The page token is too long.\n"
        status_code = 400
    if max_results:
        try:
            int(max_results)
        except:
            review += "max_results must be an integer.\n"
            status_code = 400

    return make_response(review, status_code)


def create_response_dict(response, video_id):
    response_dict = {}
    if 'nextPageToken' in response:
        response_dict['nextPageToken'] = response['nextPageToken']
    response_dict['video_id'] = video_id
    response_dict['urls_found'] = []
    response_dict['pageInfo'] = response['pageInfo']
    # response_dict['number_of_comments'] = 0
    response_dict['comments'] = []
    return response_dict



def get_all_comments(response):
    all_comments = []
    all_urls = []
    for item in response['items']:  # will isPublic be a problem when False?
        comment_dict = {}
        comment_dict['id'] = item['id']
        comment_details = item['snippet']['topLevelComment']['snippet']
        comment_dict['username'], comment_dict['time'], comment_dict['text'], urls = get_comment_or_reply_values(
            comment_details)
        comment_record = save_comment_if_it_is_new(comment_dict['username'], comment_dict['time'], comment_dict['text'],
                                                   urls, comment_dict['id'], video_id)

        comment_dict['time'] = comment_dict['time'].strftime("%d/%m/%Y, %H:%M:%S")
        comment_dict['replies'] = []
        # response_dict['urls_found'].extend(urls)
        all_urls.extend(urls)

        if 'replies' in item:
            replies = item['replies']['comments']
            for reply in replies:
                reply_dict = {}
                reply_dict['reply_id'] = reply['id']
                reply_details = reply['snippet']
                reply_dict['username'], reply_dict['time'], reply_dict['text'], urls = get_comment_or_reply_values(
                    reply_details)
                save_reply_if_it_is_new(reply_dict['username'], reply_dict['time'], reply_dict['text'], urls,
                                        reply_dict['reply_id'], comment_record)

                reply_dict['time'] = reply_dict['time'].strftime("%d/%m/%Y, %H:%M:%S")
                print(reply_dict['text'])
                comment_dict['replies'].append(reply_dict)
                all_urls.extend(urls)

        all_comments.append(comment_dict)
        return all_comments, all_urls


@app.route("/video_comments")
@app.route("/video_comments/")
@app.route("/video_comments/<video_id>/")
@app.route("/video_comments/<video_id>/<max_results>")
def video_comments(video_id=None, max_results=None):

    page_token = request.args.get('page')
    # page_token = request.headers.get('page_token')
    print(page_token)
    params_validation_review = validate_params(video_id, max_results, page_token)
    if params_validation_review.status_code != 200:
        return params_validation_review

    response = get_video_comments_response(video_id, max_results, page_token)
    save_request(response, video_id)

    if isinstance(response, googleapiclient.errors.HttpError):
        return create_failure_message(response)

    response_dict = create_response_dict(response, video_id)

    response_dict['comments'], response_dict['urls_found'] = get_all_comments(response)



    response_dict['urls_found'] = list(set(response_dict['urls_found']))
    return response_dict


if __name__ == '__main__':
    app.run(debug=True)  # set it to False before deploying


