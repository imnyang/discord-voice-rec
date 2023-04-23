import discord
import os, random
from discord.types.embed import Embed # default module
from datetime import datetime, timezone, timedelta
from typing import List
from dotenv import load_dotenv
from discord.ext import tasks
load_dotenv() # load all the variables from the env file

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

def get_time():
    KST = timezone(timedelta(hours=9))
    time_record = datetime.now(KST)
    time_record_str = time_record.strftime('%Y%m%d-%H%M%S')
    return time_record_str

async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()  # Disconnect from the voice channel.
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    log = bot.get_channel(1099653708121378876)
    await log.send(f"{get_time()}까지 녹음을 완료했습니다. 통화방에 있었던 사용자 리스트 : {', '.join(recorded_users)}입니다. 녹음은 새 사용자가 들어온 시점부터 새로운 녹음 파일을 생성합니다.", files=files)  # Send a message with the accumulated files.

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if before.channel is None and after.channel:
        # User has connected to a VoiceChannel
        channel = after.channel
        # Code here...
        log = bot.get_channel(1099653708121378876)
        channels = ['bot-befehle']
        voice = bot.get_channel(1093509402977382494)

        if not voice.members:
            return

        global vc
        vc = await voice.connect()  # Connect to the voice channel the author is in.

        vc.start_recording(
            discord.sinks.WaveSink(),  # The sink type to use.
            once_done,  # What to do once done.
            voice  # The channel to disconnect from.
        )
        time_record_str = get_time()
        await log.send(f"{time_record_str}에 녹음 시작")

        print("join")

    if voice_state is None:
        # Exiting if the bot it's not connected to a voice channel
        return

    if len(voice_state.channel.members) == 1:
        vc.stop_recording()

bot.run(os.getenv('TOKEN')) # run the bot with the token
