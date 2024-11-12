from functools import wraps
from channels.exceptions import DenyConnection
import httpx

def auth_token(func):
	@wraps(func)
	async def wrapper(self, *args, **kwargs):
		print(self.scope)
		token = None
		headers = self.scope['headers']
		for header in headers:
			if header[0] == b'authorization':
				token = header[1].decode()
		if not token:
			raise DenyConnection("Authorization token missing")

		async with httpx.AsyncClient() as client:
			response = await client.post(
				'http://alias:8000/api/auth/token/validate/',
				headers={'authorization': token}
			)
		if response.status_code != 200:
			raise DenyConnection("Invalid authorization token")
		
		self.user_id = response.json().get('id')
		return await func(self, *args, **kwargs)

	return wrapper
