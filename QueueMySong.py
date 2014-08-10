import spotify
import time
import threading

logged_in_event = threading.Event()
def connection_state_listener(session):
	if session.connection.state is spotify.ConnectionState.LOGGED_IN:
		logged_in_event.set()

session = spotify.Session()
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

print((str)(session.user))

