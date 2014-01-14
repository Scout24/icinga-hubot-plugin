"""
Usage:
  icinga2hubot ( -c file )

Options:
  -h --help                         Show this screen.
  -c, --config FILE                 Configuration file.

"""
import ConfigParser
import os
import sys
import urllib
import urllib2

from docopt import docopt

MANDATORY_CONFIG = 'url'
ICINGA_OS_VARIABLE_PREFIX = 'ICINGA_'


def _post_to_url(url, data):
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(url, encoded_data)
    urllib2.urlopen(request)


def _parse_config_file(config_file):
    config_parser = ConfigParser.ConfigParser()
    config_parser.readfp(config_file)
    config = dict(config_parser.items('settings'))
    if not config.get(MANDATORY_CONFIG):
        raise ValueError('config file is missing: %s' % MANDATORY_CONFIG)
    return config


def _read_config_from_file(config_filename):
    with open(config_filename) as config_file:
        return _parse_config_file(config_file)


def _read_icinga_data_from_environ():
    icinga_data = {}
    for os_variable in os.environ.iterkeys():
        os_variable_value = os.environ.get(os_variable)
        if os_variable.startswith(ICINGA_OS_VARIABLE_PREFIX) and os.environ.get(os_variable):
            icinga_data[os_variable] = os_variable_value

    return icinga_data


def _create_configuration(argv):
    args = docopt(__doc__, argv=argv)
    return _read_config_from_file(args['--config'])


def _run(argv=None):
    config = _create_configuration(argv)
    icinga_data = _read_icinga_data_from_environ()
    _post_to_url(config['url'], icinga_data)


if __name__ == '__main__':
    try:
        _run()
    except Exception as e:
        print("An error occurred while handling even: %s" % e)
        sys.exit(1)
