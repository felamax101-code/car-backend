"""
Task One 3.5 — payment step, kept behind one function so a real provider
(e.g. M-Pesa Daraja) can replace `charge()` later without touching any
view that calls it.
"""

import uuid


def charge(payment, method="MOCK"):
    """
    Mock gateway: always succeeds and returns a fake reference.

    Swap this function's body for a real API call later — everything
    that calls `charge()` only cares about the returned (success, reference)
    shape, not how the charge happened.
    """
    reference = f"MOCK-{uuid.uuid4().hex[:10].upper()}"
    return True, reference