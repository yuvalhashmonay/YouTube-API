This is an API written in Python and Flask. the API returns a YouTube video's comments, replies and the URLs found in those comments and replies.
All new results are saved in a relational DB, the request itself is documented as well.


Using the API:


Installation: 

1.	Clone the repo.
2.	Create a virtual environment and Install the requirements
3.	To exempt you from setting environment variables, I provided a text file called keys.txt.
	Replace the first line of the file with an arbitrary key for the Flask application and replace the second line with a valid YouTube API key (Open the file keys.txt and things will be clear)
4.	Run the file create_db.py
5.	Run the file __init__.py



After deploying:

This API holds a single endpoint (GET).
The first URL parameter is the video id and the second is the maximum number of comments (optional), YouTube's default for maximum comments is 20.
Endpoint - http://<IP>/video_comments/<video id>/<max comments>
You can also ask for a specific page by sending a query param called 'page' with the value being the desired page number.


Response:

The response body will contain the following:
1.	The token for the next page (if received)
2.	All URLs found in the comments & replies
3.	The video's id
4.	The number of results
5.	All comments and their replies


