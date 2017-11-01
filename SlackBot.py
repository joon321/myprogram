import os
import time
from slackclient import SlackClient


# testbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
Time = int(time.time())

# constants
# AT_BOT = "<@" + BOT_ID + ">"
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
			return True


def del_user(u):
	length = len(history)
	for i in range(length):
		if history[i]['user'] == u:
			del history[i]


def past_seconds(t):
	"""
	t value is time in seconds
	"""
	for i, j in enumerate(history):
		if int(history[i]['time']) + t < Time:
			return True


def send_message(response, channel):
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def handle_response(command, channel):
	"""
		Receives commands directed at the bot and determines if they
		are valid commands. If so, then acts on the commands. If not,
		returns back what it needs for clarification.
	"""

	init_response = "Ok, create case.\n " \
				    "Enter data\n" \
				    "Customer: <account name> <Alt+Enter>\n" \
				    "Description: <UI not working>"

	if REQUEST_COMMAND[0] in command and not is_user_in_list(user):
		append_history({'time': ts[0:10], '__SESSION__': "initiated", 'user': user})
		send_message(init_response, channel)
	elif is_user_in_list(user) and "customer:" in command and "description:" in command:
		send_message("""add your API code now""", channel)
		del_user(user)
	elif is_user_in_list(user) and not past_seconds(300):
		send_message("Enter data\n"
					 "Customer: <account name> <Alt+Enter>\n"
					 "Description: <UI not working>", channel)


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
	if slack_client.rtm_connect():
		print("TestBot connected and running!")
		while True:
			command, channel, ts, user = parse_slack_output(slack_client.rtm_read())
			if command and channel and ts and user:
				handle_response(command, channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")
