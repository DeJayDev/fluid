from yt_dlp.utils import UnsupportedError

from disco.bot import Plugin
from disco.bot.command import CommandError
from disco.types.permissions import Permissions
from disco.util.sanitize import S
from disco.voice import YoutubeDLInput, BufferedOpusEncoderPlayable
from disco.voice.player import Player


class FluidPlugin(Plugin):

    def load(self, ctx):
        # Telecom: self.guilds: list[VoiceConnection] = {}
        self.guilds: list[Player] = {}

    def get_player(self, guild_id) -> Player:
        if guild_id not in self.guilds:
            raise CommandError("I'm not currently playing music here.")
        return self.guilds.get(guild_id)

    def remove_player(self, guild_id) -> Player:
        if guild_id in self.guilds:
            player = self.guilds.pop(guild_id)
            player.client.disconnect()
            return player

    def _join_voice(self, state, guild_id):
        client = state.channel.connect()
        self.guilds[guild_id] = Player(client)
        self.guilds[guild_id].complete.wait()

    @Plugin.listen('Ready')
    def on_ready(self, event):
        self.log.info('Fluid connected to GW v{}'.format(event.version))

    @Plugin.listen('MessageCreate')
    def on_message(self, event):
        if event.author.bot:
            return  # don't care

    # TODO: If the bot is the last one in the voice channel, leave the channel.
    # Requires some work in Disco to know how many people are in a voice channel at any given time.
    # Here's some Copilot code that may actually work after a VoiceChannel provides members:
    # 
    # @Plugin.listen('VoiceStateUpdate')
    # def on_voice_state_update(self, event):
    #     if event.guild.id not in self.guilds:
    #         return
    #     if event.member.id == self.client.user.id:
    #         return
    #     if event.channel_id != self.guilds[event.guild.id].channel.id:
    #         return
    #     if event.member.voice.channel.members.count == 1:
    #         self.guilds[event.guild.id].channel.disconnect()

    @Plugin.command('ping')
    def on_ping(self, event):
        event.channel.send_message('pong')

    @Plugin.command('join')
    def on_join(self, event):
        state = event.guild.get_member(event.author).get_voice_state()
        if not state:
            return event.msg.reply('You must be connected to voice to use this command.')

        if event.guild.id in self.guilds:
            bot_voice_state = event.guild.get_voice_state(self.state.me.id)

            # Fail if the user and bot are in the same channel
            if state.channel.id == bot_voice_state.channel.id:
                return event.msg.reply('I am already in your channel.')
            # If the user has admin permissions, then we can move the bot to the user's channel
            if event.member.permissions.can(Permissions.ADMINISTRATOR):
                # Get and remove the current player
                self.get_player(event.guild.id).disconnect()
                del self.guilds[event.guild.id]
                # Recreate the player
                self._join_voice(state, event.guild.id)
                return event.msg.reply('Moved to your channel, as you are an Admin')
            else:
                return event.msg.reply(
                    'You must be an Admin to move me. Join me instead? {}'.format(bot_voice_state.channel.mention))

        try:
            event.channel.send_message('Joined {}'.format(state.channel.mention))

            # Telecom: self.guilds[event.guild.id] = VoiceConnection(self.client, guild_id=event.guild.id, enable_events=False)
            self._join_voice(state, event.guild.id)
            self.client.api.guilds_members_modify(event.guild.id, self.state.me.id, deaf=True)

        except Exception as e:
            return event.msg.reply('Failed to connect to voice: `{}`'.format(e))

    @Plugin.command('play', '<song:str...>')
    def on_play(self, event, song):
        if event.member.get_voice_state().channel is None: # TODO: If the bot IS in a channel, invite the user to join it.
            return event.msg.reply('You must be connected to voice to use this command.')
        try:
            # Telecom: playable = YoutubeDLPlayable.from_url(song)
            #playable = YoutubeDLInput(song)
            playable = YoutubeDLInput(song)
            stream = playable.pipe(BufferedOpusEncoderPlayable)
        except UnsupportedError as e:
            return event.msg.reply(S('Failed to play: `{}`'.format(e)))

        # Telecom: self.get_player(event.guild.id).play(next(playable))
        self.get_player(event.guild.id).queue.append(stream)
        event.channel.send_message(S('Added `{}` to the queue.'.format(song)))

    @Plugin.command('pause')
    def on_pause(self, event):
        self.get_player(event.guild.id).pause()

    @Plugin.command('resume')
    def on_resume(self, event):
        self.get_player(event.guild.id).resume()

    @Plugin.command('leave')
    def on_leave(self, event):
        player = self.get_player(event.guild.id)
        player.disconnect()
        event.channel.send_message('Left {}'.format(player.client.channel.mention))

    @Plugin.command('skip')
    def on_skip(self, event):
        self.get_player(event.guild.id).skip()

    @Plugin.command('disconnect')
    def on_disconnect(self, event):
        self.get_player(event.guild.id).disconnect()
        self.remove_player(event.guild.id)

    @Plugin.command('kill')
    def on_kill(self, event):
        self.get_player(event.guild.id).disconnect()
        self.get_player(event.guild.id).client.ws.sock.shutdown()
