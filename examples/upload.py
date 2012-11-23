""" Upload a file specified by command line
"""
import sys
from dropbox_uploader import Uploader

uploader = Uploader(config='myconf')

if '--authorize' in sys.argv:
    from getpass import getpass

    username = raw_input('username>>> ')
    password = getpass('password>>> ')
    token = uploader.authorize(username, password)
    print "This is your access token, please store it in your configuration " \
          "to allow future calls: ('{0}', '{1}')".format(token.key, token.secret)
    exit(0)

for fname in sys.argv:
    try:
        print "Uploading {0}...".format(fname),
        print "Done" if uploader.upload(fname) else "Failed"
    except IOError, e:
        print "Failed:", e
