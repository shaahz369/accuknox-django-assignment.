"""
Receivers used by the three experiments. Each receiver records what it
observes into a shared dict / list (``trace``) so the tests can inspect it.
"""
import threading
import time

from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Item

# Shared scratchpad that the tests read from and reset.
trace = {
    "events": [],            # Q1: ordering of events
    "receiver_thread": None, # Q2: thread id seen inside the receiver
    "receiver_in_atomic": None,  # Q3: was the receiver inside a transaction?
    "raise_in_receiver": False,  # Q3: flag to make receiver fail
}


def reset_trace():
    trace["events"] = []
    trace["receiver_thread"] = None
    trace["receiver_in_atomic"] = None
    trace["raise_in_receiver"] = False


@receiver(post_save, sender=Item)
def item_post_save(sender, instance, created, **kwargs):
    # Q1: log start, sleep (a slow handler), log end
    trace["events"].append("receiver_start")
    time.sleep(2)
    trace["events"].append("receiver_end")

    # Q2: remember which thread executed the receiver
    trace["receiver_thread"] = threading.get_ident()

    # Q3: is the receiver running inside an open DB transaction?
    trace["receiver_in_atomic"] = connection.in_atomic_block
    if trace["raise_in_receiver"]:
        raise RuntimeError("boom from receiver")
