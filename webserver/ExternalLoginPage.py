from flask import render_template, request, redirect, url_for
from flask.views import View
from shared.ansi_logger import getLogger

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
from shared import load_secrets

class ExternalLoginPage(View):
    

    def __init__(self, model, template):
        self.config = model["config"]
        self.google_provider_cfg = model["google_provider_cfg"]
        self.google_oath_client : WebApplicationClient = model["google_oath_client"]
        self.logger = getLogger(self.config, __name__)
        self.template = template
        
    def dispatch_request(self):
        if self.google_oath_client is None:
            return render_template(self.template)
        else:
            secrets = load_secrets()
            authorization_endpoint = self.google_provider_cfg["authorization_endpoint"]
            redirect_url = url_for("/Account/ExternalLogin/callback", _external=True) if "reverse_proxy_url" not in secrets or not secrets["reverse_proxy_url"] or "local_url" not in secrets or not secrets["local_url"] else str.replace(url_for("/Account/ExternalLogin/callback", _external=True), secrets["local_url"], secrets["reverse_proxy_url"])

            request_uri = self.google_oath_client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=redirect_url,
                scope=["openid", "email", "profile"],
            )
            
            return redirect(request_uri)
