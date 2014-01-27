# NOTE: this is not tested code.

import sys
from twython import TwythonStreamer
from pprint import pprint

class MyStreamer(TwythonStreamer):
    """
    A Custom Streamer for the Twitter Streaming API.

    See:
    http://twython.readthedocs.org/en/latest/usage/streaming_api.html
    and
    https://dev.twitter.com/docs/api/1.1/post/statuses/filter

    """
    def on_success(self, data):
        if 'text' in data:
            print(data['text'].encode('utf-8'))
        pprint(data)

    def on_error(self, status_code, data):
        print(status_code)
        pprint(data)

def filter(keywords):
    """Creates/Returns an EventStreamer"""
    stream = EventStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    stream.statuses.filter(track=keywords)

if __name__ == "__main__":
    filter(sys.argv[0])