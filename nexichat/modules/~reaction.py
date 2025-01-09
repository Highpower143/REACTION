import random
from pyrogram import Client, filters
from pyrogram.types import Message
from nexichat import nexichat

# List of emojis to choose from
emojis = ["🕊️", "💕", "💔", "🫠", "😘", "🥀", "🌺", "❤️‍🔥", "🐱", "💟", "💥", "😚", "💯", "🫣", "❤️", "💞"]

@nexichat.on_message(filters.incoming)
async def react_to_messages(client: Client, message: Message):
    try:
        # Choose a random emoji from the list
        random_emoji = random.choice(emojis)
        await message.react(random_emoji)
    except Exception as e:
        print(f"Failed to react to message: {e}")
