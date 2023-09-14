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
    def on_start(self):
        self.client.startup(withMediation=True)

    def on_stop(self):
        self.client.shutdown()

    @task
    def get_invite(self):
        invite = self.client.issuer_getinvite()
        self.invite = invite
        print("INVITE IS ", invite)

    @task
    def accept_invite(self):
        self.client.ensure_is_running()

        connection = self.client.accept_invite(self.invite['invitation_url'])
        self.connection = connection
        print("CONN IS ", connection)

    @task
    def receive_credential(self):
        self.client.ensure_is_running()

        credential = self.client.receive_credential(self.connection['_tags']['invitationId'])

class Issue(CustomLocust):
    tasks = [UserBehaviour]
    wait_time = between(float(os.getenv('LOCUST_MIN_WAIT',0.1)), float(os.getenv('LOCUST_MAX_WAIT',1)))
#    host = "example.com"
