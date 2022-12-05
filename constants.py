
########################################################## YouTube API ##########################################################
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
PART = "snippet,replies"
VIDEO_ID_MAX_LENGTH = 20
PAGE_TOKEN_MAX_LENGTH = 200
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

VIDEO_COMMENTS_ROUTE = "/video_comments"

with open('keys.txt', 'r') as f:
    lines = f.readlines()
    if len(lines) < 2:
        raise Exception("please provide a secret key for Flask on the first row and and a YouTube key on the second.")
    SECRET_KEY = lines[0]
    DEVELOPER_KEY = lines[1]
    print(f"SECRET_KEY = {SECRET_KEY}")
    print(f"DEVELOPER_KEY = {DEVELOPER_KEY}")
    if SECRET_KEY == "" or DEVELOPER_KEY == "":
        raise Exception("please provide a secret key for Flask on the first row and and a YouTube key on the second.")


