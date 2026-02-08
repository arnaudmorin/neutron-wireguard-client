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

"""OpenStackClient plugin for WireGuard."""

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_wireguard_api_version'
API_NAME = 'wireguard'
API_VERSIONS = {
    '2': 'neutron_wireguard_client.v2.client.Client',
}


def make_client(instance):
    """Return a wireguard client."""
    from neutron_wireguard_client.v2 import client as wg_client

    LOG.debug('Instantiating wireguard client')
    return wg_client.Client(session=instance.session,
                            region_name=instance.region_name,
                            endpoint_type=instance.interface)


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-wireguard-api-version',
        metavar='<wireguard-api-version>',
        default=utils.env('OS_WIREGUARD_API_VERSION', default='2'),
        help='WireGuard API version, default=' +
             DEFAULT_API_VERSION +
             ' (Env: OS_WIREGUARD_API_VERSION)')
    return parser
