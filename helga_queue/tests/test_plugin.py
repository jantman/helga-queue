from mock import patch, call, Mock
import helga_queue.plugin


class TestPlugin:

    def test_commands_dict(self):
        d = helga_queue.plugin._commands_dict()
        assert 'append' in d
        assert callable(d['append'])
        assert d['append'].__name__ == 'handle_append'
        for funcname in d:
            assert d['append'].__name__.startswith('handle_')

    @patch('helga_queue.plugin.db', new=None)
    def test_queue_plugin_no_db(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['arg1', 'arg2'])
        assert res == "ERROR: MongoDB connection is None - check configuration."

    @patch('helga_queue.plugin._commands_dict')
    def test_queue_plugin(self, mock_cd):
        mock_append = Mock()
        mock_append.return_value = 'mockappendreturn'
        mock_cd.return_value = {'append': mock_append}
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['append', 'foo', 'bar'])
        assert mock_append.called is True
        assert mock_append.mock_calls == [call(None, 'chan', 'mynick', 'mynick', ['foo', 'bar'])]
        assert res == 'mockappendreturn'

    @patch('helga_queue.plugin._commands_dict')
    def test_queue_plugin_no_args(self, mock_cd):
        mock_list = Mock()
        mock_list.return_value = 'mocklistreturn'
        mock_cd.return_value = {'list': mock_list}
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', [])
        assert mock_list.mock_calls == [call(None, 'chan', 'mynick', 'mynick', [])]
        assert res == 'mocklistreturn'

    def test_queue_plugin_unknown_cmd(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['notacommand'])
        assert res == "queue subcommand 'notacommand' not known - please use 'queue help' for available commands"

    @patch('helga_queue.plugin._commands_dict')
    def test_queue_plugin_queuename(self, mock_cd):
        mock_append = Mock()
        mock_append.return_value = 'mockappendreturn'
        mock_cd.return_value = {'append': mock_append}
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['somequeue', 'append', 'foo', 'bar'])
        assert mock_append.called is True
        assert mock_append.mock_calls == [call(None, 'chan', 'mynick', 'somequeue', ['foo', 'bar'])]
        assert res == 'mockappendreturn'

    @patch('helga_queue.plugin._commands_dict')
    def test_queue_plugin_queuename_no_args(self, mock_cd):
        mock_list = Mock()
        mock_list.return_value = 'mocklistreturn'
        mock_cd.return_value = {'list': mock_list}
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['somequeue'])
        assert res == "queue subcommand 'somequeue' not known - please use 'queue help' for available commands"

    def test_queue_plugin_queuename_unknown_cmd(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['somequeue', 'notacommand'])
        assert res == "queue subcommand 'somequeue' not known - please use 'queue help' for available commands"

    def test_queue_repr(self):
        queue = ['zero', 'one', 'two', 'three']
        expected = 'Contents of queue "qname":\n0. zero\n1. one\n2. two\n3. three\n'
        result = helga_queue.plugin._queue_repr('qname', queue)
        assert result == expected

    def test_queue_repr_empty(self):
        expected = 'Queue "qname" is empty.'
        result = helga_queue.plugin._queue_repr('qname', [])
        assert result == expected

    @patch('helga_queue.plugin.db')
    def test_get_queue(self, mock_db):
        mock_db.helga_queue.find_one.return_value = {'_id': 'qname', 'queue': ['zero', 'one', 'two']}
        result = helga_queue.plugin._get_queue('qname')
        assert result == ['zero', 'one', 'two']
        assert mock_db.mock_calls == [call.helga_queue.find_one({'_id': 'qname'})]

    @patch('helga_queue.plugin.db')
    def test_get_queue_none(self, mock_db):
        mock_db.helga_queue.find_one.return_value = None
        result = helga_queue.plugin._get_queue('qname')
        assert result == []
        assert mock_db.mock_calls == [call.helga_queue.find_one({'_id': 'qname'})]

    @patch('helga_queue.plugin.db')
    def test_set_queue(self, mock_db):
        mock_db.helga_queue.save.return_value = True
        result = helga_queue.plugin._set_queue('qname', ['zero', 'one', 'two'])
        assert result == "queue 'qname' updated"
        assert mock_db.mock_calls == [call.helga_queue.save({'_id': 'qname', 'queue': ['zero', 'one', 'two']})]

    @patch('helga_queue.plugin.db')
    def test_set_queue_error(self, mock_db):
        mock_db.helga_queue.save.side_effect = RuntimeError()
        result = helga_queue.plugin._set_queue('qname', ['zero', 'one', 'two'])
        assert mock_db.mock_calls == [call.helga_queue.save({'_id': 'qname', 'queue': ['zero', 'one', 'two']})]
        assert result == "ERROR - update to queue 'qname' failed"

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_append(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_append(None, None, None, 'qname', ['foo', 'bar', 'baz'])
        assert result == 'setreturn'
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'one', 'two', 'foo bar baz'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_len(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_len(None, None, None, 'qname', [])
        assert result == '3 items in queue qname'

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_next(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_next(None, None, None, 'qname', [])
        assert result == 'Next item in queue qname: zero'

    @patch('helga_queue.plugin._queue_repr')
    @patch('helga_queue.plugin._get_queue')
    def test_handle_list_inchannel(self, mock_get, mock_repr):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_client = Mock()
        mock_repr.return_value = 'myqrepr'
        helga_queue.plugin.handle_list(mock_client, 'chname', 'mynick', 'qname', [])
        assert mock_client.mock_calls == [
            call.me('chname', 'whispers to mynick all 3 items in queue'),
            call.msg('mynick', 'myqrepr')
        ]
        assert mock_repr.mock_calls == [call('qname', ['zero', 'one', 'two'])]

    @patch('helga_queue.plugin._queue_repr')
    @patch('helga_queue.plugin._get_queue')
    def test_handle_list_inpm(self, mock_get, mock_repr):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_client = Mock()
        mock_repr.return_value = 'myqrepr'
        helga_queue.plugin.handle_list(mock_client, 'mynick', 'mynick', 'qname', [])
        assert mock_client.mock_calls == [
            call.msg('mynick', 'myqrepr')
        ]
        assert mock_repr.mock_calls == [call('qname', ['zero', 'one', 'two'])]

    @patch('helga_queue.plugin._queue_repr')
    @patch('helga_queue.plugin._get_queue')
    def test_handle_show(self, mock_get, mock_repr):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_client = Mock()
        mock_repr.return_value = 'myqrepr'
        result = helga_queue.plugin.handle_show(mock_client, 'chname', 'mynick', 'qname', [])
        assert mock_client.mock_calls == []
        assert mock_repr.mock_calls == [call('qname', ['zero', 'one', 'two'])]
        assert result == 'myqrepr'

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_pop(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_pop(None, None, None, 'qname', [])
        assert result == "Popped item 0 from queue qname: 'zero'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['one', 'two'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_pop_empty(self, mock_set, mock_get):
        mock_get.return_value = []
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_pop(None, None, None, 'qname', [])
        assert result == 'Queue qname is empty.'

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_pop_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_pop(None, None, None, 'qname', ['1'])
        assert result == "Popped item 1 from queue qname: 'one'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'two'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_pop_invalid_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_pop(None, None, None, 'qname', [8])
        assert result == 'ERROR - there are only 3 items in queue qname'

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_pop_nonint_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_pop(None, None, None, 'qname', ['foo'])
        assert result == "ERROR - foo is not a valid index (int)"

    def test_help(self):
        # need to figure out some __doc__-based help for subcommands
        raise NotImplementedError()
    """
    Remaining:
    prepend
    insert(i=0)
    find(str)
    last - show last item in queue
    get(i=0)
    empty - delete everything
    push - alias to append
    jump(i=1) bring i to the front
    demote(i=0) push i back one place
    makelast(i=0) push i to the back of the queue
    """
