import asyncio
import discord
import yt_dlp
from typing import Optional, List
import functions as function

# Config stuff
config_path = 'config.json'
config = function.load_config(config_path)

# YT-DLP options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class MusicPlayer:
    # These are the 
    def __init__(self, client):
        self.client = client # Discord client reference
        self.voice_client: Optional[discord.VoiceClient] = None # The current connected vc
        self.playlist: List[dict] = [] # List of all vids in the playlist
        self.current_index: int = 0 # Index of current song
        self.is_playing: bool = False # Checks if smth is playing
        self.loop_playlist: bool = True # Determines if playlist repeats after finishing
        self.ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS) # Youtube dl instance for getting info
        
    async def load_playlist(self) -> str:
        try:
            playlist_url = config.get('youtube_playlist_url') # Load the YouTube playlist from config
            if not playlist_url: # Check if a playlist url exists
                return "No playlist URL found in config file"
            
            print(f"Loading playlist from: {playlist_url}") # explains itself
            
            # creates ytdl object to get video ids and titles
            ytdl_flat = yt_dlp.YoutubeDL({
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True
            })
            
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl_flat.extract_info(playlist_url, download=False))
            
            if 'entries' in data:
                self.playlist = []
                for entry in data['entries']:
                    if entry:
                        video_id = entry.get('id')
                        if video_id:
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            song_info = {
                                'title': entry.get('title', 'Unknown'),
                                'webpage_url': video_url,
                                'duration': entry.get('duration', 0)
                            }
                            self.playlist.append(song_info)
                            print(f"Loaded: {song_info['title']}")
                        
                return f"Loaded {len(self.playlist)} songs from playlist."
            else:
                return "Failed to load playlist."
        except Exception as e:
            print(f"Error loading playlist: {e}")
            return f"Error loading playlist: {str(e)}"
    
    async def join_voice(self, message: discord.Message) -> str:
        # Join the user's voice channel
        if message.author.voice is None:
            return "You need to be in a voice channel first."
        
        channel = message.author.voice.channel
        print(f"Attempting to join voice channel: {channel.name}")
        
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.move_to(channel)
                print(f"Moved to {channel.name}")
                return f"Moved to {channel.name}"
            else:
                self.voice_client = await channel.connect()
                print(f"Connected to {channel.name}")
                return f"joined {channel.name}"
        except Exception as e:
            print(f"Error joining voice channel: {e}")
            return f"Failed to join voice channel: {str(e)}"
    
    async def get_stream_url(self, webpage_url: str) -> Optional[str]:
        # Get the actual stream URL for a video
        if not webpage_url:
            print("No webpage URL provided")
            return None
            
        try:
            print(f"Getting stream URL for: {webpage_url}")
            loop = asyncio.get_event_loop()
            ytdl_stream = yt_dlp.YoutubeDL({
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            })
            data = await loop.run_in_executor(None, lambda: ytdl_stream.extract_info(webpage_url, download=False))
            stream_url = data.get('url')
            print(f"Got stream URL: {stream_url[:50]}..." if stream_url else "Failed to get stream URL")
            return stream_url
        except Exception as e:
            print(f"Error getting stream URL for {webpage_url}: {e}")
            return None
    
    async def play_song(self, index: int = None):
        # Play a song from the playlist
        if index is not None:
            self.current_index = index
        
        if not self.playlist:
            print("Playlist is empty")
            return
        
        if not self.voice_client or not self.voice_client.is_connected():
            print("Not connected to voice")
            return
        
        # Handle looping
        if self.current_index >= len(self.playlist):
            if self.loop_playlist:
                self.current_index = 0
            else:
                self.is_playing = False
                return
        
        song = self.playlist[self.current_index]
        print(f"Attempting to play: {song['title']}")
        print(f"Webpage URL: {song['webpage_url']}")
        
        stream_url = await self.get_stream_url(song['webpage_url'])
        
        if not stream_url:
            print(f"Failed to get stream for {song['title']}, skipping...")
            self.current_index += 1
            await self.play_song()
            return
        
        try:
            source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            
            def after_playing(error):
                if error:
                    print(f"Error during playback: {error}")
                self.current_index += 1
                # Schedule next song
                future = asyncio.run_coroutine_threadsafe(self.play_next(), self.client.loop)
                try:
                    future.result()
                except Exception as e:
                    print(f"Error scheduling next song: {e}")
            
            self.voice_client.play(source, after=after_playing)
            self.is_playing = True
            print(f"Now playing: {song['title']}")
        except Exception as e:
            print(f"Error playing song: {e}")
            self.current_index += 1
            await self.play_song()
    
    async def play_next(self):
        # Play the next song in the playlist
        if not self.voice_client or not self.voice_client.is_connected():
            print("Not connected to voice for next song")
            return
        
        # Handle looping
        if self.current_index >= len(self.playlist):
            if self.loop_playlist:
                self.current_index = 0
            else:
                self.is_playing = False
                return
        
        await self.play_song()
    
    async def start(self, message: discord.Message) -> str:
        # Start playing the playlist
        print("Start command received")
        
        if not self.playlist:
            print("Loading playlist...")
            load_result = await self.load_playlist()
            print(f"Load result: {load_result}")
            if "error" in load_result or "failed" in load_result:
                return load_result
        
        print("Joining voice channel...")
        join_result = await self.join_voice(message)
        print(f"Join result: {join_result}")
        if "need to be" in join_result or "failed" in join_result:
            return join_result
        
        print("Starting playback...")
        self.current_index = 0
        await self.play_song()
        return f"started playing playlist from the beginning"
    
    def skip(self) -> str:
        # Skip to next song
        if not self.voice_client or not self.voice_client.is_playing():
            return "nothing is playing right now"
        
        self.voice_client.stop()
        return f"skipped to next song"
    
    def skip_back(self) -> str:
        # Go back to previous song
        if not self.voice_client:
            return "not connected to voice"
        
        self.current_index = max(0, self.current_index - 2)
        if self.voice_client.is_playing():
            self.voice_client.stop()
        return f"going back to previous song"
    
    def pause(self) -> str:
        # Pause playback
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            return "paused"
        return "nothing is playing"
    
    def resume(self) -> str:
        # Resume playback
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            return "resumed"
        return "nothing is paused"
    
    async def stop(self) -> str:
        # Stop and disconnect
        print("Stop command received")
        if self.voice_client:
            self.is_playing = False
            if self.voice_client.is_playing():
                self.voice_client.stop()
            try:
                await self.voice_client.disconnect()
                print("Disconnected from voice")
            except Exception as e:
                print(f"Error disconnecting: {e}")
            self.voice_client = None
            return "stopped and disconnected"
        return "not connected to voice"
    
    def now_playing(self) -> str:
        # Get current song info
        if not self.is_playing or not self.playlist:
            return "nothing is playing right now"
        
        song = self.playlist[self.current_index]
        duration = song.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        
        return f"now playing: {song['title']} ({minutes}:{seconds:02d}) - song {self.current_index + 1}/{len(self.playlist)}"
    
    def queue_info(self) -> str:
        # Get next few songs in queue
        if not self.playlist:
            return "playlist is empty"
        
        next_songs = []
        for i in range(self.current_index + 1, min(self.current_index + 4, len(self.playlist))):
            next_songs.append(f"{i + 1}. {self.playlist[i]['title']}")
        
        if next_songs:
            return "coming up next:\n" + "\n".join(next_songs)
        else:
            return "no more songs in queue (will loop back to start)"

# Global music player instance
music_player: Optional[MusicPlayer] = None

def init_music_player(client):
    # Initialize the music player
    global music_player
    music_player = MusicPlayer(client)
    return music_player