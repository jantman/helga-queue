from mock import patch, call, Mock
import helga_queue.plugin


class TestPlugin:


    @patch('helga_queue.plugin.db', new=None)
    def test_queue_plugin_no_db(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['arg1', 'arg2'])
        assert res == "ERROR: MongoDB connection is None - check configuration."

    def test_queue_plugin(self):
        with patch('helga_queue.plugin.handle_add', create=True) as mock_add:
            mock_add.return_value = 'mockaddreturn'
            res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['add', 'foo', 'bar'])
        assert mock_add.called is True
        assert mock_add.mock_calls == [call(None, 'chan', 'mynick', 'mynick', ['foo', 'bar'])]
        assert res == 'mockaddreturn'

    @patch('__builtin__.globals')
    def test_queue_plugin_no_args(self, mock_globals):
        mock_list = Mock()
        mock_list.return_value = 'mocklistreturn'
        mock_globals.return_value = {'handle_list': mock_list}
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', [])
        assert mock_list.mock_calls == [call(None, 'chan', 'mynick', 'mynick', [])]
        assert res == 'mocklistreturn'

    def test_queue_plugin_unknown_cmd(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['notacommand'])
        assert res == "queue subcommand 'notacommand' not known - please use 'queue help' for available commands"

    # @TODO: test with queue name
    def test_queue_plugin_queuename(self):
        with patch('helga_queue.plugin.handle_add') as mock_add:
            mock_add.return_value = 'foo'
            res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['myqueue', 'add', 'foo', 'bar'])
        assert mock_add.mock_calls == [call(None, 'chan', 'mynick', 'myqueue', ['foo', 'bar'])]
        assert res == 'foo'

    def test_queue_plugin_queuename_no_args(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['myqueue'])
        assert res == "queue subcommand 'myqueue' not known - please use 'queue help' for available commands"

    def test_queue_plugin_queuename_unknown_cmd(self):
        res = helga_queue.plugin.queue_plugin(None, 'chan', 'mynick', 'mymessage', 'queue', ['notacommand'])
        assert res == "queue subcommand 'notacommand' not known - please use 'queue help' for available commands"
    
    def test_handle_add(self):
        with patch('helga_queue.plugin._queue_add') as mock_qa:
            mock_qa.return_value = 'foo'
            res = helga_queue.plugin.handle_add('client', 'channel', 'nick', 'message', ['foo', 'bar'])
            assert mock_qa.mock_calls == [call('nick', 'foo bar')]
        assert res == "foo"
