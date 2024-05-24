import aiohttp
import asyncio
from tqdm.asyncio import tqdm

PANEL_URL = 'https://panel.tcnetwk.cloud'
API_KEY = 'ptla_sEVl5kIJHdiuqeFD1bf8124dcOol2MTZdFEs4i56QJY'
LOCATION_ID = 2  # Location ID for servers you want to delete

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

async def get_servers_by_location(session, location_id):
    url = f'{PANEL_URL}/api/application/servers'
    servers = []
    page = 1

    while True:
        params = {'page': page, 'per_page': 50}
        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                print(f'Failed to retrieve servers: {response.status}')
                break

            data = await response.json()

            for server in data['data']:
                server_location_id = server['attributes']['node']  # Adjusted to get the correct location ID
                if server_location_id == location_id:
                    servers.append(server['attributes']['id'])

            pagination = data.get('meta', {}).get('pagination', {})
            if not pagination.get('links', {}).get('next'):
                break

            page += 1

    return servers

async def delete_server(session, server_id):
    url = f'{PANEL_URL}/api/application/servers/{server_id}/force'
    async with session.delete(url, headers=headers) as response:
        if response.status == 204:
            return True
        else:
            print(f'Failed to delete server {server_id}: {response.status} - {await response.text()}')
            return False

async def delete_servers_concurrently(servers):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for server_id in servers:
            tasks.append(delete_server(session, server_id))
            await asyncio.sleep(1/3)  # To delete 3 servers per second

        results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Deleting servers", unit="server")]

def main():
    async def run():
        async with aiohttp.ClientSession() as session:
            servers_to_delete = await get_servers_by_location(session, LOCATION_ID)
            print(f'Servers to delete: {servers_to_delete}')
            await delete_servers_concurrently(servers_to_delete)

    asyncio.run(run())

if __name__ == '__main__':
    main()
