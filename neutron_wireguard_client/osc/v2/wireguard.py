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

"""WireGuard OSC commands."""

import logging

from cliff import columns as cliff_columns
from cliff import command
from cliff import lister
from cliff import show
from osc_lib import exceptions
from osc_lib import utils

LOG = logging.getLogger(__name__)


class ListColumn(cliff_columns.FormattableColumn):
    """Formats a list as a comma-separated string for display."""

    def human_readable(self):
        if self._value is None:
            return ''
        if isinstance(self._value, (list, tuple)):
            return ', '.join(str(v) for v in self._value)
        return str(self._value)

# Columns to display in list output
LIST_COLUMNS = (
    'id',
    'name',
    'router_id',
    'port',
    'ipaddress',
    'peer_endpoint',
    'status',
)

# Columns to display in show output
SHOW_COLUMNS = (
    'id',
    'name',
    'project_id',
    'router_id',
    'public_key',
    'port',
    'ipaddress',
    'peer_public_key',
    'peer_endpoint',
    'peer_allowed_ips',
    'status',
)


def _get_columns(item):
    """Get column names and values for display."""
    columns = SHOW_COLUMNS
    return (
        columns,
        utils.get_item_properties(item, columns, formatters={
            'peer_allowed_ips': ListColumn,
        })
    )


class CreateWireguard(show.ShowOne):
    """Create a new WireGuard connection."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='Name of the WireGuard connection',
        )
        parser.add_argument(
            '--router',
            metavar='<router>',
            required=True,
            help='Router to attach the WireGuard interface to (name or ID)',
        )
        parser.add_argument(
            '--ipaddress',
            metavar='<cidr>',
            required=True,
            help='IP address for the WireGuard interface in CIDR notation '
                 '(e.g., 10.0.0.1/24)',
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            default=51820,
            help='WireGuard listen port (default: 51820)',
        )
        parser.add_argument(
            '--peer-public-key',
            metavar='<key>',
            help="Peer's WireGuard public key",
        )
        parser.add_argument(
            '--peer-endpoint',
            metavar='<host:port>',
            help="Peer's endpoint address (e.g., 203.0.113.1:51820)",
        )
        parser.add_argument(
            '--peer-allowed-ip',
            metavar='<cidr>',
            action='append',
            dest='peer_allowed_ips',
            help='Allowed IP range for the peer (can be repeated)',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.wireguard

        # Resolve router name to ID if needed
        router_id = _get_router_id(self.app.client_manager, parsed_args.router)

        kwargs = {
            'name': parsed_args.name,
            'router_id': router_id,
            'ipaddress': parsed_args.ipaddress,
            'port': parsed_args.port,
        }

        if parsed_args.peer_public_key:
            kwargs['peer_public_key'] = parsed_args.peer_public_key
        if parsed_args.peer_endpoint:
            kwargs['peer_endpoint'] = parsed_args.peer_endpoint
        if parsed_args.peer_allowed_ips:
            kwargs['peer_allowed_ips'] = parsed_args.peer_allowed_ips

        wireguard = client.wireguards.create(**kwargs)
        return _get_columns(wireguard)


class DeleteWireguard(command.Command):
    """Delete WireGuard connection(s)."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'wireguard',
            metavar='<wireguard>',
            nargs='+',
            help='WireGuard connection(s) to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.wireguard
        result = 0

        for wg_id in parsed_args.wireguard:
            try:
                wireguard = client.wireguards.find(wg_id)
                client.wireguards.delete(wireguard.id)
            except Exception as e:
                result += 1
                LOG.error("Failed to delete wireguard '%(wg)s': %(e)s",
                          {'wg': wg_id, 'e': e})

        if result > 0:
            total = len(parsed_args.wireguard)
            raise exceptions.CommandError(
                f"{result} of {total} wireguards failed to delete."
            )


class ListWireguard(lister.Lister):
    """List WireGuard connections."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--router',
            metavar='<router>',
            help='Filter by router (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Filter by name',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.wireguard
        filters = {}

        if parsed_args.router:
            filters['router_id'] = _get_router_id(
                self.app.client_manager, parsed_args.router)
        if parsed_args.name:
            filters['name'] = parsed_args.name

        wireguards = client.wireguards.list(**filters)

        return (
            LIST_COLUMNS,
            (utils.get_item_properties(wg, LIST_COLUMNS) for wg in wireguards)
        )


class SetWireguard(command.Command):
    """Update a WireGuard connection."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'wireguard',
            metavar='<wireguard>',
            help='WireGuard connection to update (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set a new name for the WireGuard connection',
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help='Set the WireGuard listen port',
        )
        parser.add_argument(
            '--ipaddress',
            metavar='<cidr>',
            help='Set the IP address in CIDR notation',
        )
        parser.add_argument(
            '--peer-public-key',
            metavar='<key>',
            help="Set the peer's WireGuard public key",
        )
        parser.add_argument(
            '--peer-endpoint',
            metavar='<host:port>',
            help="Set the peer's endpoint address",
        )
        parser.add_argument(
            '--peer-allowed-ip',
            metavar='<cidr>',
            action='append',
            dest='peer_allowed_ips',
            help='Set allowed IP range for the peer (can be repeated, '
                 'replaces existing values)',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.wireguard
        wireguard = client.wireguards.find(parsed_args.wireguard)

        kwargs = {}
        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name
        if parsed_args.port is not None:
            kwargs['port'] = parsed_args.port
        if parsed_args.ipaddress is not None:
            kwargs['ipaddress'] = parsed_args.ipaddress
        if parsed_args.peer_public_key is not None:
            kwargs['peer_public_key'] = parsed_args.peer_public_key
        if parsed_args.peer_endpoint is not None:
            kwargs['peer_endpoint'] = parsed_args.peer_endpoint
        if parsed_args.peer_allowed_ips is not None:
            kwargs['peer_allowed_ips'] = parsed_args.peer_allowed_ips

        if not kwargs:
            raise exceptions.CommandError("No changes specified.")

        client.wireguards.update(wireguard.id, **kwargs)


class ShowWireguard(show.ShowOne):
    """Show details of a WireGuard connection."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'wireguard',
            metavar='<wireguard>',
            help='WireGuard connection to display (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.wireguard
        wireguard = client.wireguards.find(parsed_args.wireguard)
        return _get_columns(wireguard)


def _get_router_id(client_manager, router_name_or_id):
    """Get router ID from name or ID.

    :param client_manager: The OpenStack client manager
    :param router_name_or_id: Router name or ID
    :returns: Router UUID
    """
    try:
        # Try to use the network client to resolve router
        network_client = client_manager.network
        router = network_client.find_router(router_name_or_id,
                                            ignore_missing=False)
        return router.id
    except Exception:
        # If network client fails, assume it's already a UUID
        return router_name_or_id
