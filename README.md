A Twitter Filter
================

This is a simple python script that connects to the Twitter streaming api
and searches for keywords.

Usage
-----

This app requires a Twitter App Key and OAuth tokens, which it will read from
the following environment variables:

* `TWITTER_APP_KEY`
* `TWITTER_APP_SECRET`
* `TWITTER_OAUTH_TOKEN`
* `TWITTER_OAUTH_TOKEN_SECRET`


I stick these in `~/.twitter`, and run `source ~/.twitter` prior to running
the filter.

The filter requires two parameters:

1. A search Query, and
2. A path to a text file. Matching tweets will be appended to this file.


Example usage:

    $ source ~/.twitter && python filter/main.py "search query" /path/to/tweets.txt


