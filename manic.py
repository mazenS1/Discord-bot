import discord
from discord.ext import commands
import os
import yt_dlp
import asyncio
from dotenv import load_dotenv

def run_bot():
    load_dotenv()
    TOKEN = "token"

    intents = discord.Intents.default()
    intents.message_content= True
    client = commands.Bot(command_prefix="!",intents=intents)

    queues = {}
    voice_clients ={}
    yt_dlp_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dlp_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

    async def play_next(ctx):
        if queues[ctx.guild.id] != []:
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link)
    
    @client.command(name="play")
    async def play(ctx, *,link):
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild] = voice_client
        except Exception as e:
            print(e)
        try:
            
            loop = asyncio.get_event_loop()
            
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))
            song = data["url"]
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            voice_clients[ctx.guild].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        except Exception as e:
            print(e)

    @client.command(name="clear queue")
    async def clear_queue(ctx):
        if ctx.guild in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared")
        else:
            await ctx.send("No queue to clear")
            
    @client.command(name="pause")
    async def pause(ctx):
        try:
            voice_clients[ctx.guild].pause()
        except Exception as e:
            print(e)
    @client.command(name="leave")
    async def leave(ctx):
        try:
            await voice_clients[ctx.guild].disconnect()
            del voice_clients[ctx.guild]
        except Exception as e:
            print(e)
    @client.command(name="resume")
    async def resume(ctx):
        try:
            voice_clients[ctx.guild].resume()
        except Exception as e:
            print(e)
    @client.command(name="queue")
    async def queue(ctx,url):
        if ctx.guild not in queues:
            queues[ctx.guild.id] = []
        queues[ctx.guild.id].append(url)
        await ctx.send("Song added to queue")

            
    client.run(TOKEN)
