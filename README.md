certbot-dns-asd
===============

A Certbot DNS plugin using the All Secure Domains (ASD) dyanmic DNS API.
------------------------------------------------------------------------
  
ASD offer a secure DNS update API (with fine-grained access control on a
per-record basis).  This plugin allows certbot to use the ASD DNS update API
to carry out an RFC8555 section 8.4 "dns-01" challenge, without the security
issues associated with many other providers' DNS APIs.
  
The API can be used to obtain an SSL certificate from the "Let's Encrypt" service.

License
-------

This software is Copyright 2018, 2019 by SEOSS Ltd, and offered under the GNU
General Public License, see the file `LICENSE` (which you should have recieved
with this software) for more information.

Installation
------------

* Option 1, using the operating-system provided ("packaged") certbot.

1. Install Certbot (for Debian-based OS e.g. Ubuntu Linux), run the following
command (or the equivalent for your OS) as root:

    `apt install git certbot python3-pip`

1. Run the following command as an unprivileged user:

    `git clone https://github.com/tim-seoss/certbot-dns-asd.git`

1. Run the following as root:

    `pip3 install /path/to/certbot-dns-asd/`

Usage
-----

The following example assumes you wish to obtain an SSL certificate for the
host `my-ssl-hostname.example.com`, and that you are managing the DNS for
the `example.com` domain using the ASD DNS service...

1. Using the ASD control panel, add one or more DNS dynamic update TXT records
of the form `_acme-challenge.my-ssl-hostname` within the `example.com` DNS
management settings.  For each newly created _acme-challenge TXT record, tick
the `Enable dynamic (API) upates` box.  Copy the "UUID" which ASD provides you
for the record(s) and use them in the next step:

1. Create a JSON file based on the following example:
    ```json
    {
            "dns_api_keys": {
                    "_acme-challenge.my-ssl-hostname.example.com": {
                            "domain": "example.com",
                            "key": "aaee0065-9d22-4070-8546-14b5c0f17328"
                    },
                    "_acme-challenge.my-other-ssl-hostname.example.com": {
                            "domain": "example.com",
                            "key": "ebacdd45-d71d-46f0-b9f1-194fe9491855"
                    }
            }
    }
    ```
    e.g. in the location `/etc/letsencrypt/asd-dns-api/example_com.json`

    Be sure to restrict the permissions on the file and/or directory to prevent
    reading by unprivileged users.

1. Optionally obtain a test (Let's Encrypt staging server) certificate:

    ```
    me@server:~$ certbot --staging --authenticator certbot-asd:dns \
    --certbot-asd:dns-credentials /etc/letsencrypt/asd-dns-api/example_com.json \
    certonly -d my-ssl-hostname.example.com -d my-other-ssl-hostname.example.com
    ```

1. Optionally change the `certonly` command to automatically install the newly
obtained certificate for application server using the `--installer` option.  See
https://certbot.eff.org/docs/using.html#combining-plugins and
https://certbot.eff.org/docs/using.html#combining-plugins .

1. Once you have finished testing, obtain a production certificate by repeating
your previous command, having first removed the `--staging` argument to `certbot`.


If your certificate request will need more than one challenge to be verified
against a single TXT record (e.g. if you request a single certificate, which is
valid for both `example.com` and the wildcard `*.example.com`, then you will
need to create multiple records via the ASD control panel, and then list the
corresponding multiple keys like this:
    ```json
    {
            "dns_api_keys": {
                    "_acme-challenge.example.com": {
                            "domain": "example.com",
                            "key": ["e18a608f-e5c2-418f-bfd5-847df39280a8", "5f91a2f8-5797-4b4e-a723-3adfcb1c2c88"]
                    }
            }
    }
    ```

Bugs?
----

Please open an issue at https://github.com/tim-seoss/certbot-dns-asd/issues
