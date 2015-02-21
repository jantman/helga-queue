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
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

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
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_pop_nonint_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_pop(None, None, None, 'qname', ['foo'])
        assert result == "ERROR - foo is not a valid index (int)"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_insert_no_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_insert(None, None, None, 'qname', ['foo', 'bar', 'baz'])
        assert result == "ERROR - first argument to insert must be an integer index"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_insert(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_insert(None, None, None, 'qname', ['2', 'foo', 'bar', 'baz'])
        assert result == "Inserted into queue qname at index 2: 'foo bar baz'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'one', 'foo bar baz', 'two'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_insert_past_end(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_insert(None, None, None, 'qname', ['6', 'foo', 'bar', 'baz'])
        assert result == "ERROR - queue qname only has 3 elements, cannot insert at index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_prepend(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_prepend(None, None, None, 'qname', ['foo', 'bar', 'baz'])
        assert result == "Prepended to queue qname: 'foo bar baz'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['foo bar baz', 'zero', 'one', 'two'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_last(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_last(None, None, None, 'qname', [])
        assert result == "Last item in queue qname (length 3): 'two'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_last_empty(self, mock_set, mock_get):
        mock_get.return_value = []
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_last(None, None, None, 'qname', [])
        assert result == "Queue qname is empty."
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_empty(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_empty(None, None, None, 'qname', ['everything'])
        assert result == "Deleted all items from queue qname"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', [])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_empty_already(self, mock_set, mock_get):
        mock_get.return_value = []
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_empty(None, None, None, 'qname', ['everything'])
        assert result == "Queue qname is already empty"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_empty_noarg(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_empty(None, None, None, 'qname', [])
        assert result == "ERROR - to empty queue, use 'queue empty everything'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_get(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_get(None, None, None, 'qname', ['2'])
        assert result == "Queue qname item 2: 'two'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_get_empty(self, mock_set, mock_get):
        mock_get.return_value = []
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_get(None, None, None, 'qname', ['2'])
        assert result == "Queue qname is empty"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_get_pastend(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_get(None, None, None, 'qname', ['6'])
        assert result == "ERROR - queue qname only has 3 elements, cannot get index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_get_no_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_get(None, None, None, 'qname', [])
        assert result == "Queue qname item 0: 'zero'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_get_nonint_index(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_get(None, None, None, 'qname', ['foo'])
        assert result == "ERROR - index must be an integer; 'foo' is invalid"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_jump(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_jump(None, None, None, 'qname', ['2'])
        assert result == "Queue qname item 2 moved to front"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['two', 'zero', 'one'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_jump_noarg(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_jump(None, None, None, 'qname', [])
        assert result == "ERROR - 'jump' requires index to move to front"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_jump_past_end(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_jump(None, None, None, 'qname', ['6'])
        assert result == "ERROR - queue qname only has 3 elements, cannot jump index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_jump_nonint(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_jump(None, None, None, 'qname', ['foo'])
        assert result == "ERROR - index nust be an integer; 'foo' is invalid"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_demote(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_demote(None, None, None, 'qname', ['1'])
        assert result == "Queue qname item 1 demoted"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'two', 'one'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_demote_noarg(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_demote(None, None, None, 'qname', [])
        assert result == "Queue qname item 0 demoted"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['one', 'zero', 'two'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_demote_nonint(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_demote(None, None, None, 'qname', ['foo'])
        assert result == "ERROR - index must be an integer; 'foo' is invalid"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_demote_pastend(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_demote(None, None, None, 'qname', ['6'])
        assert result == "ERROR - queue qname only has 3 items; cannot demote index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_makelast(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_makelast(None, None, None, 'qname', ['1'])
        assert result == "Queue qname item 1 moved to end"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'two', 'one'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_makelast_noarg(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_makelast(None, None, None, 'qname', [])
        assert result == "Queue qname item 0 moved to end"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['one', 'two', 'zero'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_makelast_nonint(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_makelast(None, None, None, 'qname', ['foo'])
        assert result == "ERROR - index must be an integer; 'foo' is invalid"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_makelast_pastend(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_makelast(None, None, None, 'qname', ['6'])
        assert result == "ERROR - queue qname only has 3 items; cannot move index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_move(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['0', '2'])
        assert result == "Queue qname item 0 moved to position 2"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['one', 'two', 'zero'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_move_from_pastend(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['6', '2'])
        assert result == "ERROR - queue qname only has 3 items; cannot move index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_move_to_pastend(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['0', '6'])
        assert result == "ERROR - queue qname only has 3 items; cannot move to index 6"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_nonint(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['foo', '2'])
        assert result == "ERROR - index must be an integer; 'foo' is invalid"
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['1', 'bar'])
        assert result == "ERROR - index must be an integer; 'bar' is invalid"
        assert mock_get.mock_calls == []
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_move2(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'three', 'four', 'five']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['1', '5'])
        assert result == "Queue qname item 0 moved to position 2"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'two', 'three', 'four', 'five', 'one'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_move3(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'three', 'four', 'five']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_move(None, None, None, 'qname', ['4', '1'])
        assert result == "Queue qname item 0 moved to position 2"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == [call('qname', ['zero', 'four', 'one', 'two', 'three', 'five'])]

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_find_str(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'three', 'four', 'five']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_find(None, None, None, 'qname', ['two'])
        assert result == "Queue qname (len=6) item 'two' is at index 2"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_find_str_notfound(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'three', 'four', 'five']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_find(None, None, None, 'qname', ['foo'])
        assert result == "Queue qname (len=6) does not contain 'foo'"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_find_substr(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'three', 'four', 'five']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_find(None, None, None, 'qname', ['fiv'])
        assert result == "Queue qname (len=6) contains 'fiv' in item 'five' is at index 5"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_find_str_multiple(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'three', 'four', 'two']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_find(None, None, None, 'qname', ['two'])
        raise NotImplementedError()
        assert result == "Queue qname (len=6) item 'two' is at index 2"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._get_queue')
    @patch('helga_queue.plugin._set_queue')
    def test_handle_find_substr_multiple(self, mock_set, mock_get):
        mock_get.return_value = ['zero', 'one', 'two', 'notfour', 'four', 'five']
        mock_set.return_value = 'setreturn'
        result = helga_queue.plugin.handle_find(None, None, None, 'qname', ['four'])
        raise NotImplementedError()
        assert result == "Queue qname (len=6) item 'two' is at index 2"
        assert mock_get.mock_calls == [call('qname')]
        assert mock_set.mock_calls == []

    @patch('helga_queue.plugin._commands_dict')
    def test_help(self, mock_cd):
        def func1():
            """doc for func1"""
            return None

        def func2():
            """doc for func2"""
            return True

        expected = "USAGE: queue [queue name] [subcommand] [args [...]]\n" + \
                   "Subcommands:\n" + \
                   "func1 - doc for func1\n" + \
                   "func2 - doc for func2\n" + \
                   "another2 - doc for func2\n"
        mock_cd.return_value = {'func1': func1, 'func2': func2, 'another2': func2}
        mock_client = Mock()
        res = helga_queue.plugin.handle_help(mock_client, 'chan', 'mynick', None, [])
        assert mock_client.mock_calls == [
            call.me('chname', 'whispers to mynick'),
            call.msg('mynick', expected)
        ]
