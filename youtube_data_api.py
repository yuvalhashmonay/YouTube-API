import googleapiclient.discovery
from constants import API_SERVICE_NAME, API_VERSION, DEVELOPER_KEY, PART
import os

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)

def get_video_comments_response(videoId, maxResults=None, pageToken=None):
    request = youtube.commentThreads().list(
        part=PART,
        maxResults=maxResults,
        pageToken=pageToken,
        videoId=videoId
    )
    try:
        return request.execute()
    except Exception as e:
        return e
