# Accuknox Django Trainee Assignment

Run: `pip install django && python manage.py test -v 2`

- signals_demo/signals.py   - receiver used by Q1-Q3
- signals_demo/tests.py     - Q1 (sync), Q2 (same thread), Q3 (same transaction), Rectangle tests
- signals_demo/rectangle.py - Rectangle class

## Conclusions
1. Synchronous: save() blocks until the receiver (which sleeps 2s) finishes; event order proves it.
2. Same thread: thread ids of caller and receiver are identical.
3. Same transaction: an exception in the receiver rolls back the caller's row inside atomic();
   receiver also sees connection.in_atomic_block == True.
