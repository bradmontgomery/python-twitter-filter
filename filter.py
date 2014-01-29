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
from pprint import pformat
from sys import argv, exit, stderr, stdout
from termcolor import colored
from traceback import print_exc
from twython import TwythonStreamer

try:
    import gntp.notifier as growl
except ImportError:
    growl = None  # NOQA


class StreamNotifier(TwythonStreamer):
    """A Custom Streamer for the Twitter Streaming API.

    Usage:

        stream = StreamNotifier(
            environ['TWITTER_APP_KEY'],
            environ['TWITTER_APP_SECRET'],
            environ['TWITTER_OAUTH_TOKEN'],
            environ['TWITTER_OAUTH_TOKEN_SECRET'],
            output=output,
            exit_on_error=True
        )

    For more info, see:
        http://twython.readthedocs.org/en/latest/usage/streaming_api.html
    and
        https://dev.twitter.com/docs/api/1.1/post/statuses/filter

    """
    def __init__(self, *args, **kwargs):
        self.output_file = kwargs.pop("output", "tweets.txt")
        self.exit_on_error = kwargs.pop("exit_on_error", False)
        return super(StreamNotifier, self).__init__(*args, **kwargs)

    def _tweet_url(self, data):
        return u"https://twitter.com/{0}/status/{1}".format(
            data['user']['screen_name'],
            data['id_str']
        )

    def write_message(self, data):
        url = self._tweet_url(data)
        spacer = u"-" * 80
        message = u"{0} -- {1}:\n\n{2}\n\n{3}\n{4}\n".format(
            data['user']['screen_name'],
            data['user']['location'],
            data['text'],
            url,
            spacer
        )
        with open(self.output_file, "a") as f:
            try:
                f.write(message.encode("utf-8"))
            except (UnicodeDecodeError, UnicodeEncodeError):
                # punt on unicode :(
                f.write(message.decode("ascii", "ignore").encode("utf-8"))

    def print_message(self, data):
        url = self._tweet_url(data)
        stdout.write(u"{0}\n{1}\n{2}\n\n".format(
            colored(data['user']['screen_name'], "yellow"),
            colored(data['text'], "white", attrs=['bold']),
            colored(url, "red")
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
        stderr.write(colored("{0}\n\n".format(pformat(data)), "red"))
        if self.exit_on_error:
            exit(1)


def filter(keywords, output=None):
    """Creates an EventStreamer instance and filters the streaming API for
    any tweets matching the given keywords.

    * keywords -- a string containing keywords to match in tweets.
    * output -- path to a text file where matched tweets are written

    """
    stream = StreamNotifier(
        environ['TWITTER_APP_KEY'],
        environ['TWITTER_APP_SECRET'],
        environ['TWITTER_OAUTH_TOKEN'],
        environ['TWITTER_OAUTH_TOKEN_SECRET'],
        output=output,
        exit_on_error=True
    )
    stream.statuses.filter(track=keywords)


if __name__ == "__main__":
    if len(argv) != 3:
        stderr.write(
            colored("\nUSAGE: <search-terms> <path-to-file>\n\n", "red")
        )
        exit(1)

    try:
        search_terms = argv[1]
        output_file = argv[2]

        stdout.write(
            colored("\nSearching for: {0}\n\n".format(search_terms), "yellow")
        )
        filter(search_terms, output_file)  # run the streaming filter
    except Exception as e:
        if growl:
            growl.mini("Twitter Filter Failed!")
        stderr.write(colored("\n\n{0}\n".format(e), "red"))
        stderr.write(colored("\n{0}\n".format("-" * 40), "red"))
        print_exc(file=stderr)
        stderr.write(colored("\n{0}\n".format("-" * 40), "red"))
        raise e
