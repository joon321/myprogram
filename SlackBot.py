import os
import time
from slackclient import SlackClient


# testbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# command requests
REQUEST_COMMAND = ['create case', 'escalate case', 'update case']

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

history = []


def append_history(t):
	if len(history) > 20:
		del history[:1]
	history.append(t)
	return True


def is_user_in_list(u):
	length = len(history)
	for i in range(length):
		if history[i]['user'] == u:
			return i, True


def del_user(u):
	length = len(history)
	for i in range(length):
		if history[i]['user'] == u:
			del history[i]


def get_user_name(user_id):
	api_call = slack_client.api_call("users.list")
	if api_call.get('ok'):
		users = api_call.get('members')
		for user in users:
			if 'name' in user and user.get('id') == user_id:
				return user['name']
	else:
		return user_id


def past_seconds(user, t):
	"""
	t value is time in seconds
	"""
	epoch = int(time.time())

	if is_user_in_list(user):
		index = is_user_in_list(user)
		print(int(history[index[0]]['time']) + 300, epoch)
		if int(history[index[0]]['time']) + t < epoch:
			return True


def submit_api_sf():
	pass


def send_message(response, channel):
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def handle_help(command, channel):
	if AT_BOT and 'help' in command:
		send_message("Hi, I am a bot created by Joon, I can help you create a SF case\n"
					 "just type <create case> to proceed", channel)


def handle_response(command, channel, user):
	"""
		Receives commands directed at the bot and determines if they
		are valid commands. If so, then acts on the commands. If not,
		returns back what it needs for clarification.
	"""

	if REQUEST_COMMAND[0] in command and not is_user_in_list(user):
		append_history({'time': ts[0:10], '__SESSION__': "initiated", 'user': user})
		user_name = get_user_name(user)
		send_message(user_name + " create case request received.\n" \
					 "Enter data\n" \
					 "Customer: <account name> <Alt+Enter>\n" \
					 "Description: <UI not working>\n"
					 "To cancel, type <cancel>", channel)
	elif is_user_in_list(user) and "customer:" in command and "description:" in command:
		send_message("""add your API code now""", channel)
		del_user(user)
	elif is_user_in_list(user) and 'cancel' in command:
		del_user(user)
		send_message("""Your create case request canceled""", channel)
	elif is_user_in_list(user) and not past_seconds(user, 300):
		user_name = get_user_name(user)
		send_message("@" + user_name + ", still proceed with creating case?\n"
					 "Customer: <account name> <Alt+Enter>\n"
					 "Description: <UI not working>\nTo cancel, type <cancel>", channel)


def not_bot(output):
	if 'bot_id' not in output:
		return True


def parse_slack_output(slack_rtm_output):
	"""
		The Slack Real Time Messaging API is an events firehose.
		this parsing function returns None unless a message is
		directed at the Bot, based on its ID.
	"""
	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		print(output_list)
		for output in output_list:
			if 'text' in output and not_bot(output):
				# return text after the @ mention, whitespace removed
				return output['text'].strip().lower(), output['channel'], output['ts'], output['user']

	return None, None, None, None


if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	try:
		if slack_client.rtm_connect():
			print("TestBot connected and running!")
			while True:
				command, channel, ts, user = parse_slack_output(slack_client.rtm_read())
				if command and channel and ts and user:
					handle_help(command, channel)
					handle_response(command, channel, user)
				time.sleep(READ_WEBSOCKET_DELAY)
		else:
			print("Connection failed. Invalid Slack token or bot ID?")
	except ConnectionResetError:
		slack_client.rtm_connect()
