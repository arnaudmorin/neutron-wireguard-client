#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""WireGuard v2 client."""

from keystoneauth1 import adapter

from neutron_wireguard_client.v2 import wireguard


class Client:
    """Client for WireGuard v2 API.

    Uses the Neutron endpoint to access the wireguard extension.
    """

    def __init__(self, session=None, region_name=None, endpoint_type='public',
                 endpoint_override=None, **kwargs):
        """Initialize a new client for the WireGuard v2 API.

        :param session: A keystoneauth1 session object
        :param region_name: Region name to use
        :param endpoint_type: Endpoint type (public, internal, admin)
        :param endpoint_override: Optional endpoint URL override
        """
        self.session = adapter.LegacyJsonAdapter(
            session=session,
            service_type='network',
            interface=endpoint_type,
            region_name=region_name,
            endpoint_override=endpoint_override,
            **kwargs
        )
        self.wireguards = wireguard.WireguardManager(self)

    def get(self, url, **kwargs):
        """Send a GET request."""
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        """Send a POST request."""
        return self.session.post(url, **kwargs)

    def put(self, url, **kwargs):
        """Send a PUT request."""
        return self.session.put(url, **kwargs)

    def delete(self, url, **kwargs):
        """Send a DELETE request."""
        return self.session.delete(url, **kwargs)
