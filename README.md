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
