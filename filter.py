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
from traceback import print_exc
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
    def write_message(self, data):
        url = u"https://twitter.com/{0}/status/{1}".format(
            data['user']['screen_name'],
            data['id_str']
        )
        spacer = u"-" * 80
        message = u"{0} -- {1}:\n\n{2}\n\n{3}\n{4}\n".format(
            data['user']['screen_name'],
            data['user']['location'],
            data['text'],
            url,
            spacer
        )
        with open(OUTPUT, "a") as f:
            try:
                f.write(message.encode("utf-8"))
            except (UnicodeDecodeError, UnicodeEncodeError):
                # punt on unicode :(
                f.write(message.decode("ascii", "ignore").encode("utf-8"))

    def print_message(self, data):
        stdout.write(u"{0}\n{1}\n\n".format(
            colored(data['user']['screen_name'], "yellow"),
            colored(data['text'], "white", attrs=['bold'])
        ))

    def notify(self, data):
        if growl:
            growl.mini(u"{0}:\n{1}".format(
                data['user']['screen_name'],
                data['text']
            ))

    def on_success(self, data):
        if 'text' in data:
            self.write_message(data)
            self.print_message(data)
            self.notify(data)

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
        stderr.write(colored("\n{0}\n".format(e), "red"))
        stderr.write("\n" + colored("-" * 40, "red") + "\n")
        print_exc(file=stderr)
        stderr.write("\n" + colored("-" * 40, "red") + "\n")
        raise e
