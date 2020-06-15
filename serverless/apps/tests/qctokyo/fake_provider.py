# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=wildcard-import,unused-argument

"""
Fake provider class that provides access to fake backends.
"""
from typing import Dict, Optional

from qiskit.providers.baseprovider import BaseProvider
from qiskit.providers.jobstatus import JobStatus
from qiskit.test.mock.fake_provider import FakeProvider
from qiskit.test.mock.fake_job import FakeJob


class FakeProviderFactory:
    """Fake provider factory class.
    
    This class is modified based on the FakeProviderFactory class of Qiskit.
    https://github.com/Qiskit/qiskit-terra/blob/master/qiskit/test/mock/fake_provider.py
    """

    # Fixd by me.
    def __init__(self):
        self.fake_provider = FakeProvider()
        self._token = None

        for backend in self.fake_provider.backends():
            name = backend.configuration().backend_name
            backend.configuration().backend_name = name.replace("fake", "ibmq")

    def load_account(self):
        """Fake load_account method to mirror the IBMQ provider."""
        pass

    # Fixd by me.
    def enable_account(self, token, *args, **kwargs) -> Optional[BaseProvider]:
        """Fake enable_account method to mirror the IBMQ provider factory."""
        self._token = token
        return self.fake_provider

    def disable_account(self):
        """Fake disable_account method to mirror the IBMQ provider factory."""
        pass

    def save_account(self, *args, **kwargs):
        """Fake save_account method to mirror the IBMQ provider factory."""
        pass

    @staticmethod
    def delete_account():
        """Fake delete_account method to mirror the IBMQ provider factory."""
        pass

    # Fixd by me.
    def active_account(self) -> Optional[Dict[str, str]]:
        """Fake active_account method to mirror the IBMQ provider factory."""
        account = {"token": self._token, "url": "dummy_url"} if self._token else None
        return account

    def update_account(self, force=False):
        """Fake update_account method to mirror the IBMQ provider factory."""
        pass

    def providers(self):
        """Fake providers method to mirror the IBMQ provider."""
        return [self.fake_provider]

    def get_provider(self, hub=None, group=None, project=None):
        """Fake get_provider method to mirror the IBMQ provider."""
        return self.fake_provider
