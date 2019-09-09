"""Certbot DNS plugin using the All Secure Domains (ASD) dyanmic DNS API.

ASD offers a secure DNS update API (with fine-grained access control on a
per-record basis).  This plugin allows certbot to use the ASD DNS update API
to carry out an RFC8555 section 8.4 "dns-01" challenge.

This can be used to obtain an SSL certificate from the "Let's Encrypt" service.

"""
import logging

import json
import requests
import zope.interface

from certbot import interfaces
from certbot.plugins import dns_common

LOGGER = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator using the ASD Dynamic DNS update API

    This Authenticator uses the ASD Dynamic DNS update API to fulfull a dns-01 challenge.
    """

    description = ('Obtain certificates using a preconfigured DNS TXT record (for domains '
                   'which are served by the "All Secure Domains" DNS service.')

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        """Adds command line argument for credentials needed to use the API"""
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=330)
        add('credentials',
            type=str,
            help=('ASD DNS credentials ("dns_api_keys") JSON file, see {} for' +
                  'examples.').format("FIXME location of README.md or similar"))

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return 'This plugin configures a pre-existing DNS TXT record to respond to a dns-01 ' + \
                'challenge using the All Secure Domains DNS web API.'

    def _setup_credentials(self):  # pragma: no cover
        """
        Establish credentials, prompting if necessary.
        """
        if self.conf('credentials') is None:
            self._configure_file('credentials',
                                 'ASD authorisation token map JSON file')
            dns_common.validate_file_permissions(self.conf('credentials'))
            # Because this is a JSON format file, rather than the usual
            # Certbot INI-style file, we don't use the certbot helper
            # functions to validate the file contents e.g.
            # self._configure_credentials() and self._validate_credentials()

    def _perform(self, _domain, validation_domain_name, validation):
        return self._get_asd_client().modify_txt_record(validation_domain_name, validation)

    def _cleanup(self, _domain, validation_domain_name, _validation):
        """
        Deletes the DNS TXT record which would have been created by `_perform_achall`.

        Fails gracefully if no such record exists.

        :param str domain: The domain being validated.
        :param str validation_domain_name: The validation record domain name.
        :param str validation: The validation record content.
        """
        # There is currently no ASD DNS API for TXT record deletion, so we
        # change the record content to the empty string instead.
        # can set this to the empty string.
        #
        # FIXME we should test the current value (does the ASD API provide this?)
        # and if it matches the contents of the validation variable, only then
        # should we do this:
        return self._get_asd_client().modify_txt_record(validation_domain_name, '')

    def _get_asd_client(self):
        return _AsdClient(credentials_json=self.conf('credentials'))


class _AsdClient(object):
    """
    For communication with the All Secure Domains dyanmic DNS update API.
    """
    def __init__(self, credentials_json=None):
        #import ipdb; ipdb.set_trace()
        import pprint
        self.cred_filename = credentials_json
        with open(self.cred_filename) as asd_info:
            try:
                self.config = json.load(asd_info)
                LOGGER.debug("Content of user-provided auth key JSON file: %s",
                             pprint.pformat(self.config))
            except json.decoder.JSONDecodeError:
                LOGGER.error("Sorry, %s doesn't seem to be a valid JSON file, please check.",
                             self.cred_filename)
                exit(1)
        if 'globals' not in 'self.config':
            self.config['globals'] = dict()
            self.config['globals']['server_base_uri'] = 'https://www.allsecuredomains.com'
            self.config['globals']['server_path'] = '/api/dns/setDynamic'

        try:
            self.api_endpoint = self.config['globals']['server_base_uri'] + \
                    self.config['globals']['server_path']
        except KeyError:
            LOGGER.error("server_base_uri or server_path is missing from the globals in %s"
                         " please check...", self.cred_filename)
            exit(1)

    def modify_txt_record(self, dynamic_fqdn, new_content):
        """
        Bodge - only works with pre-existing keys, but does modify content.

        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occurs communicating with the DNS server
        """
        LOGGER.debug("Modify txt record for: %s", str(dynamic_fqdn))
        #data = []
        try:
            domain = self.config['dns_api_keys'][dynamic_fqdn]['domain']
            LOGGER.debug("ASD domain: %s", domain)
            hostname = dynamic_fqdn.replace('.' + domain, '')
            LOGGER.debug("ASD hostname: %s", hostname)
            key = self.config['dns_api_keys'][dynamic_fqdn]['key']
        except KeyError:
            print("Sorry, there doesn't seem to be a key for " + dynamic_fqdn + " in: " +
                  self.cred_filename + " Please add one and try again.")
            exit(1)

        query_params = {'domain': domain, 'hostname': hostname, 'key': key, 'myip': new_content}
        req = requests.request('GET', self.api_endpoint, params=query_params)
        # FIXME, check ASD API docs and handle common failures here?
        req.raise_for_status()
