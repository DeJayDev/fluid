from disco.bot.plugin import Plugin
from disco.voice.player import Player
from disco.util.sanitize import S


class FluidQueue(Plugin):

    def get_player(self, guild_id) -> Player:
        # We use this trick to get the function from the copy of this file actively used by the bot.
        # bot.plugins[] is a dict of classes mapped by their cls name.
        return self.bot.plugins['FluidPlugin'].get_player(guild_id)

    @Plugin.command('nowplaying', aliases=['np', 'whatsong'])
    def nowplaying(self, event):
        """
        Displays the currently playing song.
        """
        song = self.get_player(event.guild.id).now_playing.source

        event.msg.reply(S(':musical_note: Now playing: `{}`'.format(song.info()['title'])))

    @Plugin.command('queue')
    def queue_command(self, event):
        # Get the queue from the main plugin and print it
        player = self.get_player(event.guild.id)
        # If player.queue is empty, return the value "song"
        if not player.queue:
            # If now_playing is not None, print now_playing
            if player.now_playing:
                event.msg.reply(S(':musical_note: Now playing: `{}`'.format(player.now_playing.source.info()['title'])))
            else:
                event.msg.reply(S(':musical_note: The queue is empty.'))
            return
        else:
            # Loop through the queue and append each song to a string
            queue_string = ''
            for song in player.queue:
                queue_string += '`{}`\n'.format(song.source.info()['title'])
                # Send the string to the user
                event.msg.reply(S(':cd: Up next:\n{}'.format(queue_string)))
