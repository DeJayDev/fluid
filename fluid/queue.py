
from disco.bot.plugin import Plugin
from disco.voice.player import Player
from disco.util.sanitize import S


class FluidQueue(Plugin):

    def get_player(self, guild_id) -> Player:
        return self.bot.plugins['FluidPlugin'].get_player(guild_id)

    @Plugin.command('nowplaying', aliases=['np', 'whatsong'])
    def nowplaying(self, event):
        """
        Displays the currently playing song.
        """
        event.msg.reply(S(':musical_note: Now playing: `{}`'.format(self.get_player(event.guild.id).now_playing)))

    @Plugin.command('queue')
    def queue_command(self, event):
        # Get the queue from the main plugin and print it
        player = self.bot.plugins['FluidPlugin'].get_player(event.guild.id)
        print(list(player.queue))
