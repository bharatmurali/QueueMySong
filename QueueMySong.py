import spotify
import time
import threading
from flask import Flask, request, redirect, session
from twilio import twiml
import json

# Set up Twilio client
account_sid = "AC472e07ebef658f3280db5ce90ee5fb76"
auth_token = "0cdeae501f5a0a6374a5a0e02be684e7"

# Set up flask
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True

logged_in_event = threading.Event()

session = spotify.Session()
event_loop = spotify.EventLoop(session)
event_loop.start()

def connection_state_listener(session):
	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
		logged_in_event.set()

session.on(
	spotify.SessionEvent.CONNECTION_STATE_UPDATED,
	connection_state_listener)

filename = "impt.txt"

secureFile = open(filename, 'r')
spotifyName = secureFile.readline()
spotifyPwd = secureFile.readline()
secureFile.close()

session.login(spotifyName, spotifyPwd)


while not logged_in_event.wait(0.1):
	session.process_events()

print("User is now logged in")

container = session.playlist_container
container.load()

playlist = session.playlist_container.add_new_playlist('Bharat House Party')

time.sleep(2)

#set up number -> stage hashmap
stageRecords = {}

@app.route("/call")
def call():

	r = twiml.Response()
	r.say("Thanks for using Queue-My-Song. Please text Q to this number to get started")
	return str(r)

@app.route("/sms", methods=['GET', 'POST'])
def sms():
	global stageRecords

	message = str(request.values.get('Body'))
	user_number = str(request.values.get('From'))
	current_stage = stageRecords.get(user_number, 0)
	response = twiml.Response()

	if (current_stage == 1):
		stageRecords[user_number] = 0
		tracks = search(message)
		response.message(str(tracks))
		return str(response)

	elif (current_stage == 0 and message == "Q"):
		stageRecords[user_number] = 1
		response.message("Thanks for using Queue My Song! What song would you like to queue today?")
		return str(response)

	else:
		response.message("Please text Q to get started")
		return str(response)

def search(song_name):
	global session
	global spotify

	tracks = session.search(query=song_name, track_count=3).load()
	return tracks


app.secret_key = 'A0Zr98j/3yXR~XHHfef!!abcd'

if __name__ == "__main__":
	app.run()


