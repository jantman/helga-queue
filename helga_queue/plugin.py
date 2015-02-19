"""
Helga Queue plugin

Plugin to enable users to keep and share a short
queue of to-do items.
"""

from helga.plugins import command
from helga.db import db

def _get_queue(name):
    """
    Return the contents of a queue

    :param name: name of the queue
    :type name: string
    :rtype: list or None
    """
    res = db.helga_queue.find_one({'_id': name})
    if res is None:
        return []
    return res['queue']

def _set_queue(name, q, last=''):
    try:
        db.helga_queue.save({'_id': name, 'queue': q, 'last': ''})
        return "Queue '{n}' updated".format(n=name)
    except:
        return "ERROR - update to queue '{n}' failed".format(n=name)

def _queue_add(name, s):
    """ append s to name's queue """
    queue = _get_queue(name)
    queue.append(s)
    return _set_queue(name, queue)

def _queue_repr(nick, q):
    s = 'Contents of queue "{n}":\n'.format(n=nick)
    for idx, item in enumerate(q):
        s += '{idx}. {item}\n'.format(idx=idx, item=item)
    return s

def handle_list(client, channel, nick, queue_name, args):
    q = _get_queue(nick)
    if channel != nick:
        client.me(channel, 'whispers to {0} all {1} items in queue'.format(nick, len(q)))
    client.msg(nick, _queue_repr(nick, q))

def handle_add(client, channel, nick, queue_name, args):
    return _queue_add(nick, ' '.join(args))

def handle_len(client, channel, nick, queue_name, args):
    q = _get_queue(nick)
    return "{i} items in queue {q}".format(i=len(q), q=nick)

def handle_next(client, channel, nick, queue_name, args):
    q = _get_queue(nick)
    return "Next item in queue {q}: {i}".format(i=q[0], q=nick)

@command('queue', help='Keep a simple queue of to-do items. Usage: queue help')
def queue_plugin(client, channel, nick, message, cmd, args):
    """
    Entry point for queue plugin.
    """
    if db is None:
        return "ERROR: MongoDB connection is None - check configuration."
    if len(args) == 0:
        args = ['list']

    # find all of our commands
    commands = {}
    for funcname, fn in globals().iteritems():
        if not funcname.startswith('handle_'):
            continue
        commands[funcname[6:]] = fn

    if len(args) > 1 and args[1] in commands:
        # queue name and subcommand
        queue = args.pop(0)
        cmdname = args.pop(0)
    elif args[0] in commands:
        queue = nick
        cmdname = args.pop(0)
    else:
        return "queue subcommand '{s}' not known - please use 'queue help' for available commands".format(s=args[0])
    res = commands[cmdname](client, channel, nick, queue, args)
    return res
