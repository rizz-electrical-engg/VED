import asyncio
import os
from pyrogram import Client, filters
from .. import data, video_mimetype
from ..utils.database.add_user import AddUserToDatabase
from ..utils.database.database import Database
from ..utils.helper import check_chat
from ..utils.tasks import handle_tasks

# Retrieve the database URI and name from environment variables or configuration
DATABASE_URI = os.getenv('DATABASE_URI', 'mongodb+srv://dhimanrajat:Y8IAGI0lVrMhjvkU@cluster0.mytkgu6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'encoderbo')

db = Database(DATABASE_URI, DATABASE_NAME)

@Client.on_message(filters.incoming & (filters.video | filters.document))
async def encode_video(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    if message.document:
        if not message.document.mime_type in video_mimetype:
            return
    data.append(message)
    if len(data) == 1:
        user_id = message.from_user.id
        custom_watermark = await db.get_custom_watermark(user_id)
        await handle_tasks(message, 'tg', custom_watermark)
    else:
        await message.reply("📔 Waiting for queue...")
    await asyncio.sleep(1)

@Client.on_message(filters.command('ddl'))
async def url_encode(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    data.append(message)
    if len(message.text.split()) == 1:
        await message.reply_text("Usage: /ddl [url] | [filename]")
        data.remove(data[0])
        return
    if len(data) == 1:
        await handle_tasks(message, 'url')
    else:
        await message.reply("📔 Waiting for queue...")
    await asyncio.sleep(1)

@Client.on_message(filters.command('batch'))
async def batch_encode(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    data.append(message)
    if len(message.text.split()) == 1:
        await message.reply_text("Usage: /batch [url]")
        data.remove(data[0])
        return
    if len(data) == 1:
        await handle_tasks(message, 'batch')
    else:
        await message.reply("📔 Waiting for queue...")
    await asyncio.sleep(1)
