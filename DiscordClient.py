import asyncio
import aiohttp

class DiscordClient:

    def __init__(self, api_url):
        self.api_url = api_url
        self.session = aiohttp.ClientSession()

    async def connect(self):
        async with self.session.get(f"{self.api_url}/gateway") as response:
            if response.status == 200:
                data = await response.json()
                self.gateway_url = data["url"]
            else:
                raise ValueError(f"Failed to connect to Discord: {response.status}")

    async def send_message(self, channel_id, message_content):
        async with self.session.post(
            f"{self.api_url}/channels/{channel_id}/messages",
            data={"content": message_content}
        ) as response:
            if response.status == 200:
                return True
            else:
                raise ValueError(f"Failed to send message: {response.status}")

    async def receive_message(self, channel_id):
        async with self.session.get(
            f"{self.api_url}/channels/{channel_id}/messages"
        ) as response:
            if response.status == 200:
                data = await response.json()
                return Message(data["id"], data["content"], data["author"]["username"])
            else:
                raise ValueError(f"Failed to receive message: {response.status}")

    async def edit_message(self, channel_id, message_id, message_content):
        async with self.session.put(
            f"{self.api_url}/channels/{channel_id}/messages/{message_id}",
            data={"content": message_content}
        ) as response:
            if response.status == 200:
                return True
            else:
                raise ValueError(f"Failed to edit message: {response.status}")

    async def delete_message(self, channel_id, message_id):
        async with self.session.delete(
            f"{self.api_url}/channels/{channel_id}/messages/{message_id}"
        ) as response:
            if response.status == 204:
                return True
            else:
                raise ValueError(f"Failed to delete message: {response.status}")

    async def get_user_info(self, user_id):
        async with self.session.get(f"{self.api_url}/users/{user_id}") as response:
            if response.status == 200:
                data = await response.json()
                return User(data["id"], data["username"], data["discriminator"], data["avatar"])
            else:
                raise ValueError(f"Failed to get user info: {response.status}")

    async def get_channel_info(self, channel_id):
        async with self.session.get(f"{self.api_url}/channels/{channel_id}") as response:
            if response.status == 200:
                data = await response.json()
                return Channel(data["id"], data["name"], data["type"])
            else:
                raise ValueError(f"Failed to get channel info: {response.status}")

    async def close(self):
        await self.session.close()


class Message:
    def __init__(self, id, content, author):
        self.id = id
        self.content = content
        self.author = author


class User:
    def __init__(self, id, username, discriminator, avatar):
        self.id = id
        self.username = username
        self.discriminator = discriminator
        self.avatar = avatar


class Channel:
    def __init__(self, id, name, channel_type):
        self.id = id
        self.name = name
        self.channel_type = channel_type


async def fetch_channel_messages(client, channel_id, limit=10):
    """
    Fetches the latest messages from a channel.

    :param client: DiscordClient instance
    :param channel_id: ID of the channel to fetch messages from
    :param limit: Maximum number of messages to fetch (default is 10)
    :return: List of Message objects representing the fetched messages
    """
    async with client.session.get(
        f"{client.api_url}/channels/{channel_id}/messages?limit={limit}"
    ) as response:
        if response.status == 200:
            data = await response.json()
            return [Message(msg["id"], msg["content"], msg["author"]["username"]) for msg in data]
        else:
            raise ValueError(f"Failed to fetch channel messages: {response.status}")

async def get_user_messages(client, user_id, limit=10):
    """
    Fetches the latest messages sent by a user.

    :param client: DiscordClient instance
    :param user_id: ID of the user whose messages to fetch
    :param limit: Maximum number of messages to fetch (default is 10)
    :return: List of Message objects sent by the specified user
    """
    async with client.session.get(
        f"{client.api_url}/users/{user_id}/messages?limit={limit}"
    ) as response:
        if response.status == 200:
            data = await response.json()
            return [Message(msg["id"], msg["content"], msg["author"]["username"]) for msg in data]
        else:
            raise ValueError(f"Failed to fetch user messages: {response.status}")

async def get_user_friends(client, user_id):
    """
    Fetches the list of friends for a user.

    :param client: DiscordClient instance
    :param user_id: ID of the user whose friends to fetch
    :return: List of User objects representing the friends of the specified user
    """
    async with client.session.get(
        f"{client.api_url}/users/{user_id}/friends"
    ) as response:
        if response.status == 200:
            data = await response.json()
            return [User(friend["id"], friend["username"], friend["discriminator"], friend["avatar"]) for friend in data]
        else:
            raise ValueError(f"Failed to fetch user friends: {response.status}")

async def create_channel(client, name, channel_type):
    """
    Creates a new channel.

    :param client: DiscordClient instance
    :param name: Name of the new channel
    :param channel_type: Type of the new channel (e.g., "text" or "voice")
    :return: Channel object representing the newly created channel
    """
    async with client.session.post(
        f"{client.api_url}/channels",
        data={"name": name, "type": channel_type}
    ) as response:
        if response.status == 201:
            data = await response.json()
            return Channel(data["id"], data["name"], data["type"])
        else:
            raise ValueError(f"Failed to create channel: {response.status}")
