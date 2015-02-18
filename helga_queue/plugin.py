"""
Helga Queue plugin

Plugin to enable users to keep and share a short
queue of to-do items.
"""

from helga.plugins import command

@command('queue', help='Keep a simple queue of to-do items. Usage: queue help')
def queue_plugin(client, channel, nick, message, *args):
    """
    Entry point for queue plugin.
    """
    return "hello"
