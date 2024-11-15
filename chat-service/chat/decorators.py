from functools import wraps
import httpx
from channels.exceptions import DenyConnection

def auth_token(func):
	@wraps(func)
	async def wrapper(self, *args, **kwargs):
		try:
			subprotocols = self.scope.get('subprotocols', [])
			print(len(subprotocols))
			if not subprotocols or len(subprotocols) != 1:
				raise DenyConnection("Invalid subprotocols format")
			token = subprotocols[0]
			if not token.startswith("Bearer_"):
				raise DenyConnection("Invalid authorization format")
			tokenVal = token[len("Bearer "):].strip()
			if not tokenVal:
				raise DenyConnection("Authorization token missing")

			async with httpx.AsyncClient(timeout=5) as client:
				response = await client.post(
					'http://alias:8000/api/auth/token/validate/',
					headers={'Authorization': f'Bearer {tokenVal}'}
				)
			if response.status_code != 200:
				raise DenyConnection("Invalid authorization token")

			user_data = response.json()
			self.user_id = user_data.get('id')
			self.username = user_data.get('username')

			return await func(self, *args, **kwargs)
        
		except httpx.RequestError as exc:
			raise DenyConnection(f"Authentication service unreachable: {exc}")
		except Exception as exc:
			raise DenyConnection("Authentication failed")

	return wrapper