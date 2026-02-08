# neutron-wireguard-client

OpenStack wireguard client library and CLI plugin for python-openstackclient.

This client provides a CLI interface for managing wireguard VPN connections
through the Neutron wireguard extension.

## Installation

```bash
pip install neutron-wireguard-client
```

Or install from source:

```bash
git clone https://github.com/openstack/neutron-wireguard-client
cd neutron-wireguard-client
pip install -e .
```

## Requirements

- Python 3.10+
- python-openstackclient >= 8.0.0
- Neutron server with the neutron-wireguard extension installed

## Usage

Once installed, the wireguard commands are automatically available through
the `openstack` CLI.

### Create a wireguard connection

```bash
openstack wireguard create my-wireguard \
    --router my-router \
    --ipaddress 10.0.0.1/24 \
    --port 51820 \
    --peer-public-key "aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890abcdefg=" \
    --peer-endpoint "203.0.113.1:51820" \
    --peer-allowed-ip 10.0.0.0/24 \
    --peer-allowed-ip 192.168.1.0/24
```

### List wireguard connections

```bash
# List all
openstack wireguard list

# Filter by router
openstack wireguard list --router my-router

# Filter by name
openstack wireguard list --name my-wireguard
```

### Show wireguard connection details

```bash
openstack wireguard show my-wireguard
openstack wireguard show <wireguard-id>
```

### Update a wireguard connection

```bash
# Update name
openstack wireguard set my-wireguard --name new-name

# Update peer configuration
openstack wireguard set my-wireguard \
    --peer-public-key "newPublicKey1234567890abcdefghijklmnopqrstu=" \
    --peer-endpoint "198.51.100.1:51820" \
    --peer-allowed-ip 10.0.0.0/8
```

### Delete wireguards

```bash
# Delete single
openstack wireguard delete my-wireguard

# Delete multiple
openstack wireguard delete wg1 wg2 wg3
```

## Python API

You can also use the client library directly in Python:

```python
from keystoneauth1 import session
from keystoneauth1.identity import v3 as identity
from neutron_wireguard_client.v2 import client

# Create a session
auth = identity.Password(
    auth_url='http://controller:5000/v3',
    username='admin',
    password='secret',
    project_name='admin',
    user_domain_name='Default',
    project_domain_name='Default',
)
sess = session.Session(auth=auth)

# Create the wireguard client
wg_client = client.Client(session=sess)

# List all wireguards
for wg in wg_client.wireguards.list():
    print(f"{wg.name}: {wg.public_key}")

# Create a new wireguard
new_wg = wg_client.wireguards.create(
    name='my-vpn',
    router_id='<router-uuid>',
    ipaddress='10.0.0.1/24',
    peer_public_key='...',
    peer_endpoint='203.0.113.1:51820',
    peer_allowed_ips=['10.0.0.0/24'],
)
print(f"Created: {new_wg.id}, Public Key: {new_wg.public_key}")

# Update a wireguard
wg_client.wireguards.update(
    new_wg.id,
    name='updated-vpn',
)

# Delete a wireguard
wg_client.wireguards.delete(new_wg.id)
```

## Configuration

The client uses the standard OpenStack authentication environment variables:

```bash
export OS_AUTH_URL=http://controller:5000/v3
export OS_PROJECT_NAME=myproject
export OS_USERNAME=myuser
export OS_PASSWORD=mypassword
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

Or use a clouds.yaml file:

```yaml
clouds:
  mycloud:
    auth:
      auth_url: http://controller:5000/v3
      project_name: myproject
      username: myuser
      password: mypassword
      user_domain_name: Default
      project_domain_name: Default
```

Then:

```bash
export OS_CLOUD=mycloud
openstack wireguard list
```

## License

Apache License 2.0
