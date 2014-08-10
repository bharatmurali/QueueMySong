import spotify
import time
import threading
from flask import Flask, request, redirect, session
from twilio import twiml
import json
from twilio.rest import TwilioRestClient

logged_in_event = threading.Event()
def connection_state_listener(session):
	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
		logged_in_event.set()

session = spotify.Session()
event_loop = spotify.EventLoop(session)
event_loop.start()

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
	global spotify
	global session


