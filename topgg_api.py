import aiohttp
import json

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

class TopGGAPI:
    def __init__(self):
        self.token = config['top_gg_api_token']

    async def has_voted(self, user_id, bot_id):
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': self.token
            }
            async with session.get(f'https://top.gg/api/bots/{bot_id}/check', headers=headers, params={'userId': user_id}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('voted', False)
                else:
                    return False
