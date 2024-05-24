import requests

PANEL_URL = 'https://your-panel-url.com'
API_KEY = 'your-api-key'
LOCATION_ID = 1  # Location ID for servers you want to delete

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

def get_servers_by_location(location_id):
    url = f'{PANEL_URL}/api/application/servers'
    servers = []
    page = 1

    while True:
        params = {'page': page, 'per_page': 50}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        for server in data['data']:
            server_location_id = server['attributes']['node']  # Adjusted to get the correct location ID
            if server_location_id == location_id:
                servers.append(server['attributes']['id'])

        if not data['meta']['pagination']['links']['next']:
            break

        page += 1

    return servers

def delete_server(server_id):
    url = f'{PANEL_URL}/api/application/servers/{server_id}/force'
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f'Successfully deleted server {server_id}')
    else:
        print(f'Failed to delete server {server_id}: {response.status_code}')

servers_to_delete = get_servers_by_location(LOCATION_ID)
print(f'Servers to delete: {servers_to_delete}')

for server_id in servers_to_delete:
    delete_server(server_id)
