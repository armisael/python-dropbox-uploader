#!/usr/bin/env python
""" Upload a file specified by command line
"""

from clint import args
from dropbox_uploader import Uploader

uploader = Uploader(config='myconf')

if '--authorize' in args:
    from getpass import getpass

    username = raw_input('username>>> ')
    password = getpass('password>>> ')
    token = uploader.authorize(username, password)
    print "This is your access token, please store it in your configuration " \
          "to allow future calls: ('{0}', '{1}')".format(token.key, token.secret)
    exit(0)

for fname in args.files:
    try:
        print "Uploading {0}...".format(fname),
        print "Done" if uploader.upload(fname) else "Failed"
    except IOError, e:
        print "Failed:", e
