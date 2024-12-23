import discord
from discord.ext import commands
import wavelink
import sqlite3
from typing import cast

class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('playlists.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS playlists (
                 user_id INTEGER,
                 playlist_name TEXT,
                 track TEXT)''')


    @commands.command(name='create_playlist')
    async def createplaylist(self, ctx, playlist_name: str):
        user_id = ctx.author.id
        conn = sqlite3.connect('playlists.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM playlists WHERE user_id = ? AND playlist_name = ? LIMIT 1", (user_id, playlist_name))
        if c.fetchone():
            await ctx.send(f'Playlist "{playlist_name}" already exists.')
        else:
            c.execute("INSERT INTO playlists (user_id, playlist_name, track) VALUES (?, ?, ?)", (user_id, playlist_name, None))
            conn.commit()
            await ctx.send(f'Playlist "{playlist_name}" created.')
        conn.close()

    @commands.command(name='add_to_playlist')
    async def addtoplaylist(self, ctx, playlist_name: str, *, track: str):
        user_id = ctx.author.id
        conn = sqlite3.connect('playlists.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM playlists WHERE user_id = ? AND playlist_name = ? LIMIT 1", (user_id, playlist_name))
        if c.fetchone():
            c.execute("INSERT INTO playlists (user_id, playlist_name, track) VALUES (?, ?, ?)", (user_id, playlist_name, track))
            conn.commit()
            await ctx.send(f'Added "{track}" to playlist "{playlist_name}".')
        else:
            await ctx.send(f'Playlist "{playlist_name}" does not exist.')
        conn.close()

    @commands.command(name='view_playlist')
    async def viewplaylist(self, ctx, playlist_name: str):
        user_id = ctx.author.id
        conn = sqlite3.connect('playlists.db')
        c = conn.cursor()
        c.execute("SELECT track FROM playlists WHERE user_id = ? AND playlist_name = ?", (user_id, playlist_name))
        tracks = c.fetchall()
        if tracks:
            track_list = [track[0] for track in tracks if track[0] is not None]
            if track_list:
                await ctx.send(f'Playlist "{playlist_name}":\n' + '\n'.join(track_list))
            else:
                await ctx.send(f'Playlist "{playlist_name}" is empty.')
        else:
            await ctx.send(f'Playlist "{playlist_name}" does not exist.')
        conn.close()

    @commands.command(name='playplaylist')
    async def play_playlist(self, ctx, playlist_name: str):
        user_id = ctx.author.id
        conn = sqlite3.connect('playlists.db')
        c = conn.cursor()
        c.execute("SELECT track FROM playlists WHERE user_id = ? AND playlist_name = ?", (user_id, playlist_name))
        tracks = c.fetchall()
        conn.close()
        if tracks:
            track_list = [track[0] for track in tracks if track[0] is not None]
            if track_list:
                player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
                if not player:
                    if ctx.author.voice:
                        await ctx.send("You are not connected to a voice channel.")
                        return
  
                
                for track in track_list:
                    query = f'ytsearch:{track}'
                    tracks: wavelink.Search = await wavelink.Playable.search(query)
                    if tracks:
                        track = tracks[0]
                        await player.play(track)
                await ctx.send(f'Playing playlist "{playlist_name}".')
            else:
                await ctx.send(f'Playlist "{playlist_name}" is empty.')
        else:
            await ctx.send(f'Playlist "{playlist_name}" does not exist.')

async def setup(bot):
    await bot.add_cog(Playlist(bot))
