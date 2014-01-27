"""
Toy app to filter messages from the twitter streaming api.

Requires an APP Key and OAuth tokens in your environ:

* TWITTER_APP_KEY
* TWITTER_APP_SECRET
* TWITTER_OAUTH_TOKEN
* TWITTER_OAUTH_TOKEN_SECRET

USAGE:

    $ source ~/.twitter && python filter.py "some search terms"

"""
from os import environ
from pprint import pprint
from sys import argv, stderr, stdout
from termcolor import colored
from twython import TwythonStreamer

try:
    import gntp.notifier as growl
except ImportError:
    growl = None  # NOQA


# Write at matches to file for now.
OUTPUT = "/Users/brad/Desktop/tweets.txt"


class StreamNotifier(TwythonStreamer):
    """
    A Custom Streamer for the Twitter Streaming API.

    See:
    http://twython.readthedocs.org/en/latest/usage/streaming_api.html
    and
    https://dev.twitter.com/docs/api/1.1/post/statuses/filter

    """
    def on_success(self, data):
        if 'text' in data:
            text = data['text'].encode('utf-8')
            name = data['user']['name'].encode('utf-8')
            username = data['user']['screen_name'].encode('utf-8')
            location = data['user']['location'].encode('utf-8')
            tid = data['id_str']
            url = u"https://twitter.com/{0}/status/{1}".format(username, tid)

            msg = u"{0} [{1}]\n{2}\n\n{3}\n{4}\n{5}".format(
                username, name, location, text, url, '-' * 80
            )
            with open(OUTPUT, "a") as f:
                f.write(msg)

            if growl:
                growl.mini(u"{0}:\n{1}".format(username, text))

            stdout.write(colored(u"{0}/{1}\n".format(username, name), "yellow"))
            stdout.write(colored(u"{0}\n\n".format(text), "white", attrs=['bold']))

    def on_error(self, status_code, data):
        if growl:
            growl.mini(u"ERROR: {0}".format(status_code))
        stderr.write(colored(u"ERROR: {0}\n".format(status_code), "red"))
        pprint(data)


def filter(keywords):
    """Creates/Returns an EventStreamer"""
    stream = StreamNotifier(
        environ['TWITTER_APP_KEY'],
        environ['TWITTER_APP_SECRET'],
        environ['TWITTER_OAUTH_TOKEN'],
        environ['TWITTER_OAUTH_TOKEN_SECRET']
    )
    stream.statuses.filter(track=keywords)


if __name__ == "__main__":
    try:
        search_terms = argv[1]
        stdout.write(colored("\nSearching for: {0}\n".format(search_terms), "yellow"))
        filter(search_terms)
    except Exception as e:
        if growl:
            growl.mini("Twitter Filter Failed!")
        stderr.write(colored("{0}".format(e), "red"))
        raise e
