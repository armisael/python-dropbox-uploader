""" dropbox_uploader contains what you need to easily upload files
on your dropbox directory
"""
import requests

from dropbox import client, session
from pyquery import PyQuery
from urlparse import urlparse, urlunparse


def pyquery_w(obj_list):
    for obj in obj_list:
        yield PyQuery(obj)


class Uploader(object):
    """ Allow to upload files on dropbox by handling authentication
    and session for you.
    """
    params = ['app_key', 'app_secret', 'access_type', 'access_token']

    def __init__(self, **kwargs):
        config = kwargs.get('config', None)

        for param in self.params:
            setattr(self, param, None)

        if config:
            self._load_config_from_module(config)
        self._load_config(kwargs, dict.get)
        self.session = None

    def authorize(self, username=None, password=None):
        self.session = session.DropboxSession(
            self.app_key, self.app_secret, self.access_type)
        request_token = self.session.obtain_request_token()
        url = self.session.build_authorize_url(request_token)

        if not (username and password):
            print "Please visit {0} to authorize this app, then " \
                  "press ENTER".format(url)
            raw_input()
            return self.session.obtain_access_token(request_token)

        # GET login page
        req_sess = requests.session()
        response = req_sess.get(url)
        form_data = self._get_form_from_html(
            response, lambda form: form.attr['action'] == '/login'
        )
        form_data['post']['login_email'] = username
        form_data['post']['login_password'] = password
        assert form_data['url'], '{0}\n{1}'.format(
            response.url, response.content)

        # POST login data and redirect
        response = req_sess.post(form_data['url'], form_data['post'])
        form_data = self._get_form_from_html(
            response, lambda form: form.attr['action'] == 'authorize'
        )
        assert form_data['url'], '{0}\n{1}'.format(
            response.url, response.content)

        # POST authorization data
        req_sess.post(form_data['url'], form_data['post'])

        access_token = self.session.obtain_access_token(request_token)
        return access_token

    def authenticate(self):
        if not self.session:
            self.session = session.DropboxSession(
                self.app_key, self.app_secret, self.access_type)
            if not hasattr(self, 'access_token'):
                print 'Please set the access_token or authorize this app'
                return False
            self.session.token = self.access_token
        return self.session.token is not None

    def upload(self, filename, out_dir='/'):
        if not self.authenticate():
            return False
        self.client = client.DropboxClient(self.session)
        with open(filename) as f:
            self.client.put_file(out_dir + '/' + filename, f)
        return True

    def _load_config(self, an_obj, a_fun):
        for param in self.params:
            val = a_fun(an_obj, param, None)
            if val:
                setattr(self, param, val)

    def _load_config_from_module(self, module_name):
        try:
            module = __import__(module_name, fromlist=self.params)
        except ImportError, e:
            print e
        else:
            self._load_config(module, getattr)

    def _get_absolute_url(self, response_url, form):
        """ given a form, returns its absolute URL
        """
        url_tokens = urlparse(response_url)
        action = form.attr['action']
        if action.startswith('/'):
            path = action
        else:
            path = url_tokens[2][:url_tokens[2].rindex('/')+1] + action
        return urlunparse(list(url_tokens[:2]) + [path] + [''] * 3)

    def _get_form_from_html(self, response, test_form):
        """
        @response: the response object returned GETting or POSTing
        a webpage
        @test_form: a method that takes an html form in input and
        returns whether the form is the required one
        @return: a dictionary containing data about the given form
        """
        form_data = {'url': None, 'post': {}}
        page = PyQuery(response.content)
        for form in pyquery_w(page('form')):
            if test_form(form):
                form_data['url'] = self._get_absolute_url(response.url, form)
                form_data['method'] = form.attr['method'].lower()
                for input_obj in form('input'):
                    input = PyQuery(input_obj)
                    form_data['post'][input.attr['name']] = input.attr['value']
                return form_data
        return form_data
