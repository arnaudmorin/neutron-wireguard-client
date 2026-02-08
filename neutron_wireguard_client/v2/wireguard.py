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

"""WireGuard resource manager."""


class Wireguard:
    """Represents a WireGuard connection."""

    def __init__(self, info):
        """Initialize a Wireguard object from API response data."""
        self._info = info
        for key, value in info.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Wireguard id={self.id} name={self.name}>"

    def to_dict(self):
        """Return the wireguard data as a dictionary."""
        return self._info


class WireguardManager:
    """Manager class for WireGuard resources."""

    resource_path = '/v2.0/wireguards'

    def __init__(self, client):
        """Initialize the WireguardManager.

        :param client: The WireGuard client instance
        """
        self.client = client

    def list(self, **filters):
        """List all WireGuard connections.

        :param filters: Optional filters (name, router_id, etc.)
        :returns: List of Wireguard objects
        """
        resp, body = self.client.get(self.resource_path, params=filters)
        return [Wireguard(wg) for wg in body.get('wireguards', [])]

    def get(self, wireguard_id):
        """Get a specific WireGuard connection.

        :param wireguard_id: The UUID of the wireguard
        :returns: Wireguard object
        """
        url = f"{self.resource_path}/{wireguard_id}"
        resp, body = self.client.get(url)
        return Wireguard(body.get('wireguard', body))

    def create(self, **kwargs):
        """Create a new WireGuard connection.

        :param name: Name of the wireguard connection
        :param router_id: UUID of the router to attach to
        :param ipaddress: IP address in CIDR notation (e.g., "10.0.0.1/24")
        :param port: WireGuard listen port (default: 51820)
        :param peer_public_key: Peer's public key
        :param peer_endpoint: Peer's endpoint (host:port)
        :param peer_allowed_ips: List of allowed IP ranges for the peer
        :returns: Created Wireguard object
        """
        body = {'wireguard': kwargs}
        resp, response_body = self.client.post(self.resource_path, json=body)
        return Wireguard(response_body.get('wireguard', response_body))

    def update(self, wireguard_id, **kwargs):
        """Update a WireGuard connection.

        :param wireguard_id: The UUID of the wireguard to update
        :param kwargs: Fields to update
        :returns: Updated Wireguard object
        """
        url = f"{self.resource_path}/{wireguard_id}"
        body = {'wireguard': kwargs}
        resp, response_body = self.client.put(url, json=body)
        return Wireguard(response_body.get('wireguard', response_body))

    def delete(self, wireguard_id):
        """Delete a WireGuard connection.

        :param wireguard_id: The UUID of the wireguard to delete
        """
        url = f"{self.resource_path}/{wireguard_id}"
        self.client.delete(url)

    def find(self, name_or_id):
        """Find a wireguard by name or ID.

        :param name_or_id: The name or UUID of the wireguard
        :returns: Wireguard object
        :raises: Exception if not found or multiple matches
        """
        # First try to get by ID
        try:
            return self.get(name_or_id)
        except Exception:
            pass

        # Search by name
        matches = self.list(name=name_or_id)
        if len(matches) == 0:
            raise Exception(f"No wireguard found with name or id '{name_or_id}'")
        elif len(matches) > 1:
            raise Exception(
                f"Multiple wireguards found with name '{name_or_id}'. "
                "Please use the UUID instead."
            )
        return matches[0]
