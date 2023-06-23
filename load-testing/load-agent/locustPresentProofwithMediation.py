from locust import SequentialTaskSet, task, User, between
from locustClient import CustomClient
import time
import inspect
import json

import fcntl
import os
import signal

class CustomLocust(User):
    abstract = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.client = CustomClient(self.host)

class UserBehaviour(SequentialTaskSet):
    def get_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite

    def accept_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        self.connection = connection

    def receive_credential(self):
        self.client.ensure_is_running()

        credential = self.client.receive_credential(self.invite['connection_id'])

    def on_start(self, reinstantiate=False):
        self.client.startup(withMediation=True, reinstantiate=reinstantiate)
        self.get_invite()
        self.accept_invite()
        self.receive_credential()

    def on_stop(self):
        self.client.shutdown()
        
    @task
    def presentation_exchange(self):
        if not self.client.is_running:
            self.on_start(self, reinstantiate=True) 

        # Need connection id
        presentation = self.client.presentation_exchange(self.invite['connection_id'])

class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"

# -- Receive Credential -- 
# Offer Received (ariesCore.CredentialState.OfferReceived)
    # Accept Offer (agent.credentials.acceptOffer...)
# Credential State is Done
    # Turn off ariesCore.CredentialEventTypes.CredentialStateChanged

# Propose credential, credential preview,
# request credential, ack


# -- Present Proof -- 
## Propose credential, credential preview,
# Request credential, propose presentation,
# Presentation 
