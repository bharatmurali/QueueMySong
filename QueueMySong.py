import spotify
import time
import threading
from flask import Flask, request, redirect, session
from twilio import twiml
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('spotify')
logger.setLevel(logging.INFO)

# Set up Twilio client
account_sid = "AC472e07ebef658f3280db5ce90ee5fb76"
auth_token = "0cdeae501f5a0a6374a5a0e02be684e7"

# Set up flask
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True

logged_in_event = threading.Event()

spotify_session = spotify.Session()
event_loop = spotify.EventLoop(spotify_session)
event_loop.start()

def connection_state_listener(session):
	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
		logged_in_event.set()

spotify_session.on(
	spotify.SessionEvent.CONNECTION_STATE_UPDATED,
	connection_state_listener)

filename = "impt.txt"

secureFile = open(filename, 'r')
spotifyName = secureFile.readline()
spotifyPwd = secureFile.readline()
secureFile.close()

spotify_session.login(spotifyName, spotifyPwd)


while not logged_in_event.wait(0.1):
	spotify_session.process_events()

print("User is now logged in")

container = spotify_session.playlist_container
container.load()

playlist = spotify_session.playlist_container.add_new_playlist('Bharat House Party')
playlist.load()

time.sleep(2)

#set up number -> stage hashmap
stageRecords = {}
songRecords = {}
NUM_SONGS = 3

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

	if (current_stage == 2):
		response.message(str(handleSongChoice(int(message) - 1, user_number)))
		return str(response)

	elif (current_stage == 1):
		response.message(str(handleSongInput(message, user_number)))
		return str(response)

	elif (current_stage == 0 and message == "Q"):
		stageRecords[user_number] = 1
		response.message("Thanks for using Queue My Song! What song would you like to queue today?")
		return str(response)

	else:
		response.message("Please text Q to get started")
		return str(response)

def handleSongChoice (song_index, user_number):
	global songRecords
	global stageRecords
	global logger
	global playlist

	if song_index is None or song_index < 0 or song_index >= NUM_SONGS:
		return "Sorry that is an invalid option. Please choose a number between 1 and " + str(NUM_SONGS)

	tracks = songRecords.get(user_number)
	chosen_track = tracks[song_index]
	playlist.add_tracks(chosen_track)
	stageRecords[user_number] = 0
	return "Thanks, your song has been queued successfully!"


def handleSongInput (song_name, user_number):
		global stageRecords
		global songRecords

		songRecords[user_number] = None

		tracks = search(song_name)

		if not tracks:
			return "Sorry we could not find any songs that matched that your query. Please try again"

		stageRecords[user_number] = 2
		songRecords[user_number] = tracks
		return "We found some songs that match your request. Which one would you like to add? Respond with the number: \n" + tracksToString(tracks)

def tracksToString(tracks):
	stringToReturn = ""
	counter = 1
	for track in tracks:
		stringToReturn += str(counter) + '. ' + str (track.artists[0].name) + ' - ' + str(track.name) + "\n"
		counter+=1

	return stringToReturn

def search(song_name):
	global spotify_session

	search_results = spotify_session.search(query=song_name, track_count=NUM_SONGS).load()
	return search_results.tracks

app.secret_key = 'A0Zr98j/3yXR~XHHfef!!abcd'

if __name__ == "__main__":
	app.run()


