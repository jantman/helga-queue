"""
Helga Queue plugin

Plugin to enable users to keep and share a short
queue of to-do items.
"""

from helga.plugins import command
from helga.db import db

#######################
# subcommand handlers #
#######################

def handle_list(client, channel, nick, queue_name, args):
    q = _get_queue(queue_name)
    if channel != nick:
        client.me(channel, 'whispers to {0} all {1} items in queue'.format(nick, len(q)))
    client.msg(nick, _queue_repr(queue_name, q))

def handle_show(client, channel, nick, queue_name, args):
    q = _get_queue(queue_name)
    return _queue_repr(queue_name, q)

def handle_pop(client, channel, nick, queue_name, args):
    idx = 0
    if len(args) > 0:
        try:
            idx = int(args[0])
        except ValueError:
            return "ERROR - {a} is not a valid index (int)".format(a=args[0])
    q = _get_queue(queue_name)
    if len(q) == 0:
        return "Queue {n} is empty.".format(n=queue_name)
    if idx >= len(q):
        return "ERROR - there are only {c} items in queue qname".format(c=len(q))
    val = q.pop(idx)
    _set_queue(queue_name, q)
    return "Popped item {i} from queue {n}: '{v}'".format(n=queue_name, v=val, i=idx)

def handle_append(client, channel, nick, queue_name, args):
    queue = _get_queue(queue_name)
    item = ' '.join(args)
    queue.append(item)
    return _set_queue(queue_name, queue)

def handle_len(client, channel, nick, queue_name, args):
    q = _get_queue(nick)
    return "{i} items in queue {q}".format(i=len(q), q=queue_name)

def handle_next(client, channel, nick, queue_name, args):
    q = _get_queue(nick)
    return "Next item in queue {q}: {i}".format(i=q[0], q=queue_name)

######################
# internal functions #
######################

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

def _set_queue(name, q):
    try:
        db.helga_queue.save({'_id': name, 'queue': q})
        return "queue '{n}' updated".format(n=name)
    except:
        return "ERROR - update to queue '{n}' failed".format(n=name)

def _queue_repr(name, q):
    if len(q) == 0:
        return 'Queue "{n}" is empty.'.format(n=name)
    s = 'Contents of queue "{n}":\n'.format(n=name)
    for idx, item in enumerate(q):
        s += '{idx}. {item}\n'.format(idx=idx, item=item)
    return s

def _commands_dict():
    """return a dict of all subcommands to their handler functions"""
    commands = {}
    for funcname, fn in globals().iteritems():
        if not funcname.startswith('handle_'):
            continue
        commands[funcname[7:]] = fn
    return commands

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
    commands = _commands_dict()

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
