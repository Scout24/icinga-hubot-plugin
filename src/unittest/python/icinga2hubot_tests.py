import unittest

import icinga2hubot
from mock import mock_open, patch, ANY, MagicMock


# noinspection PyProtectedMember
class TestIcinga2Hubot(unittest.TestCase):
    ANY_CONFIG_FILE = '/any-config-file'
    ANY_URL = 'any_url'
    ANY_HOSTNAME = 'any_hostname'
    CONFIG_KEY_URL = 'url'
    ANY_POST_DATA = {'any_key': 'any_value'}

    def setUp(self):
        self.argv = ['--config', self.ANY_CONFIG_FILE]

    def tearDown(self):
        pass

    @patch('icinga2hubot._post_to_url')
    @patch('icinga2hubot._create_configuration')
    def test_run_should_create_configuration(self,
                                             mock__create_configuration,
                                             mock__post_to_url):
        icinga2hubot._run(self.argv)

        mock__create_configuration.assert_called_once_with(self.argv)

    @patch('icinga2hubot._post_to_url')
    @patch('icinga2hubot._read_icinga_data_from_environ')
    @patch('icinga2hubot._create_configuration')
    def test_run_should_read_icinga_data_from_environ(self,
                                                      mock__create_configuration,
                                                      mock__read_icinga_data_from_environ,
                                                      mock__post_to_url):
        icinga2hubot._run(self.argv)

        mock__read_icinga_data_from_environ.assert_called_once()

    @patch('icinga2hubot._post_to_url')
    @patch('icinga2hubot._read_icinga_data_from_environ')
    @patch('icinga2hubot._create_configuration')
    def test_run_should_post_data_with_url_from_config_and_data_from_environ(self,
                                                                             mock__create_configuration,
                                                                             mock__read_icinga_data_from_environ,
                                                                             mock__post_to_url):
        environ_data = {}
        mock__create_configuration.return_value = dict([(self.CONFIG_KEY_URL, self.ANY_URL)])
        mock__read_icinga_data_from_environ.return_value = environ_data

        icinga2hubot._run(self.argv)

        mock__post_to_url.assert_called_once_with(self.ANY_URL, environ_data)

    @patch('icinga2hubot.docopt')
    @patch('icinga2hubot._read_config_from_file')
    def test__create_configuration_should_validate_arguments(self,
                                                             mock__read_config_from_file,
                                                             mock_docopt):
        icinga2hubot._create_configuration(self.argv)

        mock_docopt.assert_called_once_with(ANY, argv=self.argv)

    @patch('icinga2hubot.docopt')
    @patch('icinga2hubot._read_config_from_file')
    def test__create_configuration_should_read_config_from_given_filename(self,
                                                                          mock__read_config_from_file,
                                                                          mock_docopt):
        mock_docopt.return_value = {'--config': self.ANY_CONFIG_FILE}

        icinga2hubot._create_configuration(self.argv)

        mock__read_config_from_file.assert_called_once_with(self.ANY_CONFIG_FILE)

    @patch('icinga2hubot._parse_config_file')
    def test__read_config_from_file_should_open_the_given_filename(self,
                                                                   mock__parse_config_file):
        mock_open_ = mock_open()
        with patch('icinga2hubot.open', mock_open_, create=True):
            icinga2hubot._read_config_from_file(self.ANY_CONFIG_FILE)

            mock_open_.assert_called_once_with(self.ANY_CONFIG_FILE)

    @patch('icinga2hubot._parse_config_file')
    def test__read_config_from_file_should_parse_config_file(self,
                                                             mock__parse_config_file):
        mock_open_ = mock_open()
        with patch('icinga2hubot.open', mock_open_, create=True):
            icinga2hubot._read_config_from_file(self.ANY_CONFIG_FILE)

            mock__parse_config_file.assert_called_once_with(mock_open_.return_value)

    @patch('ConfigParser.ConfigParser')
    def test__parse_config_file_should_return_a_dict_of_config_values(self,
                                                                      mock_config_parser_creator):
        mock_config_parser = MagicMock()
        expected_config = dict(url=self.ANY_URL)
        mock_config_parser_creator.return_value = mock_config_parser
        mock_config_parser.items.return_value = [(self.CONFIG_KEY_URL, self.ANY_URL)]

        actual_config = icinga2hubot._parse_config_file(ANY)

        self.assertEqual(expected_config, actual_config)

    @patch('ConfigParser.ConfigParser')
    def test__parse_config_file_should_parse_given_config_file(self,
                                                               mock_config_parser_creator):
        any_config_file = ['any_config_file']
        mock_config_parser = MagicMock()
        mock_config_parser_creator.return_value = mock_config_parser
        mock_config_parser.items.return_value = [(self.CONFIG_KEY_URL, self.ANY_URL)]

        icinga2hubot._parse_config_file(any_config_file)

        mock_config_parser.readfp.assert_called_once_with(any_config_file)

    @patch('ConfigParser.ConfigParser')
    def test__parse_config_file_should_raise_when_config_does_not_contain_an_url(self,
                                                                                 mock_config_parser_creator):
        mock_config_parser = MagicMock()
        mock_config_parser_creator.return_value = mock_config_parser
        mock_config_parser.items.return_value = [('any_key', self.ANY_URL)]

        self.assertRaises(ValueError, icinga2hubot._parse_config_file, ANY)

    @patch('os.environ')
    def test__read_icinga_data_from_env_should_return_a_dict_of_all_icinga_data(self,
                                                                                mock_os_environ):
        mock_os_environ.iterkeys.return_value = ['ICINGA_ANY']
        mock_os_environ.get.return_value = 'any_value'

        actual_icinga_data = icinga2hubot._read_icinga_data_from_environ()

        self.assertEqual({'ICINGA_ANY': 'any_value'}, actual_icinga_data)

    @patch('os.environ')
    def test__read_icinga_data_from_env_should_filter_empty_values_from_result(self,
                                                                               mock_os_environ):
        mock_os_environ.iterkeys.return_value = ['ICINGA_ANY']
        mock_os_environ.get.return_value = ''

        actual_icinga_data = icinga2hubot._read_icinga_data_from_environ()

        self.assertEqual({}, actual_icinga_data)

    @patch('os.environ')
    def test__read_icinga_data_from_env_should_filter_non_icinga_data_from_result(self,
                                                                                  mock_os_environ):
        mock_os_environ.iterkeys.return_value = ['ANY_KEY']
        mock_os_environ.get.return_value = 'any_value'

        actual_icinga_data = icinga2hubot._read_icinga_data_from_environ()

        self.assertEqual({}, actual_icinga_data)

    @patch('urllib.urlencode')
    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test__post_to_url_should_encode_post_data(self,
                                                  mock_url_open,
                                                  mock_request,
                                                  mock_urlencode):
        icinga2hubot._post_to_url(self.ANY_URL, self.ANY_POST_DATA)

        mock_urlencode.assert_called_once_with(self.ANY_POST_DATA)

    @patch('urllib.urlencode')
    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test__post_to_url_should_create_a_request_using_given_url_and_data(self,
                                                                           mock_url_open,
                                                                           mock_request,
                                                                           mock_urlencode):
        any_encoded_data = ['any_encoded_data']
        mock_urlencode.return_value = any_encoded_data

        icinga2hubot._post_to_url(self.ANY_URL, self.ANY_POST_DATA)

        mock_request.assert_called_once_with(self.ANY_URL, any_encoded_data)

    @patch('urllib.urlencode')
    @patch('urllib2.Request')
    @patch('urllib2.urlopen')
    def test__post_to_url_should_create_a_request_using_given_url_and_data(self,
                                                                           mock_url_open,
                                                                           mock_request,
                                                                           mock_urlencode):
        any_request = ['any_request']
        mock_request.return_value = any_request

        icinga2hubot._post_to_url(self.ANY_URL, self.ANY_POST_DATA)

        mock_url_open.assert_called_once_with(any_request)
