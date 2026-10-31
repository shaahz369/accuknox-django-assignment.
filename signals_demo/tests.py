import threading

from django.db import transaction
from django.test import TransactionTestCase

from . import signals
from .models import Item
from .rectangle import Rectangle


class SignalExperiments(TransactionTestCase):
    def setUp(self):
        signals.reset_trace()

    # ---------------------------------------------------------------- Q1
    def test_q1_signals_are_synchronous(self):
        """
        The receiver sleeps 2s. If signals were asynchronous, save() would
        return immediately and "after_save" would be logged BEFORE
        "receiver_end". The order below proves save() blocks until the
        receiver has completely finished -> synchronous.
        """
        ev = signals.trace["events"]
        ev.append("before_save")
        Item.objects.create(name="q1")
        ev.append("after_save")

        self.assertEqual(
            ev, ["before_save", "receiver_start", "receiver_end", "after_save"]
        )

    # ---------------------------------------------------------------- Q2
    def test_q2_signals_run_in_same_thread(self):
        """Compare the thread id of the caller with the receiver's."""
        caller_thread = threading.get_ident()
        Item.objects.create(name="q2")
        receiver_thread = signals.trace["receiver_thread"]

        print(f"\ncaller thread={caller_thread} receiver thread={receiver_thread}")
        self.assertEqual(caller_thread, receiver_thread)

    # ---------------------------------------------------------------- Q3
    def test_q3_signals_run_in_same_transaction(self):
        """
        Caller opens transaction.atomic(), saves an Item, and the receiver
        raises. The exception propagates, the caller's atomic block rolls
        back, and the Item written by the *caller* disappears. That can only
        happen if the receiver shared the caller's transaction.
        Also the receiver reports connection.in_atomic_block == True.
        """
        signals.trace["raise_in_receiver"] = True
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                Item.objects.create(name="q3")

        self.assertTrue(signals.trace["receiver_in_atomic"])
        self.assertEqual(Item.objects.count(), 0)  # rolled back


class RectangleTests(TransactionTestCase):
    def test_iteration(self):
        r = Rectangle(10, 5)
        self.assertEqual(list(r), [{"length": 10}, {"width": 5}])

    def test_printing(self):
        for d in Rectangle(10, 5):
            print(d)
