# Mail Processor and API
This is a barebones mail processing server and HTTP-based API for searching those messages.

It's not made for any type of heavy load or whatnot, so don't even try it.

## Installation
I'm assuming a few things: you have this repo cloned and are in that directory, you're on a Linux distro, and Python 2.7+ and `screen` are installed.

1. Create a virtualenv with `virtualenv .venv` and source it `source .venv\bin\activate`.
1. Install Python dependencies with `pip install -r requirements.txt`
1. Rename the config template file to `config.json` and make any necessary changes.
1. Start the mail server: `screen -S mailserver -d -m python mail.py`
1. Start the API server: `screen -S httpapi -d -m python api.py`

There's absolutely no security on the API, so limit access to it using a firewall or something. The mail server port defaults to `25`.

## DNS Records
You'll also need to set DNS records.

### MX
MX records tell SMTP servers where to send e-mail for a domain. You'll need to set these up for each domain you want this server to receive mail for.

Every host is different about setting MX records, but they all need a _priority_ and an _IP address or hostname_. Use a _priority_ of `0` and the IP address of your server.

### A
A records translate a domain name into the IP of a server -- usually for HTTP requests. You'll only need to set this up for the domain you'll want to use for the HTTP API. And it's okay just to use an IP address directly.

The A record will only need the IP address.

## API Requests
The API is a basic HTTP-based server. You can use anything, but I recommend `requests`.

All the magic happens at `/`, so that's where you make your GET request.

The following parameters can be used to search for messages:
* `to`: Searches the To line.
* `from`: Searches the From line.
* `subject`: Searches the Subject line.
* `body`: Search the message body.
* `before`: Uses a date/time string in `YYYY-MM-DDTHH:MM:SS` format to search the timestamps.

A search for _google.com_ in the From line would be something like: `0.0.0.0/?to=google.com`. Easy peasy.

The request will return a dictionary (in Python, you'll use `json.loads(response)` to transform it into a dictionary) with two keys: `count` is just the number of messages returned and `messages` is a list of message dictionaries.

The message dictionary will have the following keys:
* `timestamp`: date string in `YYYY-MM-DD HH:MM:SS` format (use `%Y-%m-%d %H:%M:%S` to convert using `strftime`)
* `from`: a string of the sender
* `recipients`: a list of recipients
* `subject`: the subject
* `body`: the full body of the message (HTML is chosen over text)
* `headers`: a dictionary of all the headers
