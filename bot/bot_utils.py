import discord

def should_ignore(message, bot):
    """
    on_message events by default process any message the bot gets, whether
    via DM or in a public channel. There's varying reasons why we should
    ignore some of those messages. This method can be used to filter things.
    """

    # Ignore messages from ourselves
    if message.author == bot.user:
        return True

    # Ignore command messages
    if message.content.startswith(bot.command_prefix):
        return True

    # Ignore DMs
    if message.channel.type == discord.ChannelType.private:
        return True

    return False
