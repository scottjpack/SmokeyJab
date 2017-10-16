#!/usr/bin/env python
"""A provisioning tool for the SmokeyJab framework"""
import argparse
import base64
import logging
import os
import random
import string
import zlib

import sys

BASE_DIR = os.path.abspath(os.path.dirname(__name__))


def time_breakdown(_s):
    _s, s = divmod(int(_s), 60)
    _s, m = divmod(_s, 60)
    _s, h = divmod(_s, 24)
    return (_s, h, m, s)


def compile_modules():
    args = {}
    module_dir = os.path.join(BASE_DIR, 'framework', 'modules')
    module_list = []
    times = []
    for fname in os.listdir(module_dir):
        with open(os.path.join(module_dir, fname)) as f:
            logging.debug('Attempting to load plugins from "{}"'.format(fname))
            module_code = f.read()

            # Test the modules
            _globals = {}
            _locals = {}
            module_args = {}

            try:
                exec (module_code, _globals, _locals)
            except Exception as e:
                logging.error('Problem testing the modules: {}'.format(e))
                sys.exit(1)
            for module_name, module in _locals.items():
                if module_name == 'ModuleBase':
                    continue

                logging.info('Checking class "{}"...'.format(module_name))
                instance = module('')

                # Make sure module version number is implemented
                try:
                    assert isinstance(instance.VERSION, (str, unicode))
                    logging.debug('`-> Module version: v{}'.format(instance.VERSION))
                except (AssertionError, AttributeError):
                    logging.error('`-> Module version not specified')
                    sys.exit(1)

                # Make sure relative_delay is implemented
                try:
                    logging.debug('`-> Relative delay: {}%'.format(instance.relative_delay))
                except NotImplementedError:
                    logging.error('`-> relative_delay not specified for this module')
                    sys.exit(1)

                # Make sure absolute_duration is implemented
                try:
                    logging.debug('`-> Module duration: {} seconds'.format(instance.absolute_duration))
                except NotImplementedError:
                    logging.error('`-> absolute_duration not specified for this module')
                    sys.exit(1)

                # Save time constraints
                times.append((instance.relative_delay, instance.absolute_duration))

                # Check for variables
                t = string.Template(module_code)
                while True:
                    try:
                        t.substitute(module_args)
                    except KeyError as e:
                        (key,) = e.args
                        value = raw_input('Input a value for {}::{}> '.format(module_name, key))
                        module_args[key] = value
                    else:
                        break
                module_code = t.substitute(module_args)

            module_list.append(module_code)
    all_module_code = '\n\n'.join(module_list)

    # Compute engagement duration
    rec_duration = int(max([(100.0*duration)/(100-delay) for delay, duration in times]))
    min_duration = int(max([x for _, x in times]))
    while True:
        logging.warning('Minimum engagement time: {} seconds ({}d {}h {}m {}s)'.format(min_duration, *time_breakdown(min_duration)))
        logging.warning('Recommended engagement time: {} seconds ({}d {}h {}m {}s)'.format(rec_duration, *time_breakdown(rec_duration)))
        total_duration = raw_input('How long (seconds) do you want this engagement to run? ')
        try:
            total_duration = int(total_duration)
            assert total_duration >= min_duration
        except:
            continue
        else:
            ending_times = [(1.0 * delay / 100) * total_duration + duration for delay, duration in times]
            latest_end_time = max(ending_times)
            delay, duration = times[ending_times.index(latest_end_time)]
            execution_window = int(100.0 * (total_duration - duration) / delay)
            total_duration = int(max([(1.0 * delay / 100) * execution_window + duration for delay, duration in times]))
            logging.warning('Engagement is expected to last {} seconds ({}d {}h {}m {}s)'.format(total_duration, *time_breakdown(total_duration)))
            break

    logging.debug('Total size of prepared modules: {} bytes'.format(len(all_module_code)))
    return execution_window, all_module_code


def generate_filename(min_length):
    with open('/usr/share/dict/words') as f:
        wordlist = filter(lambda x: x.isalpha(), f.read().split())
    outfile = random.choice(wordlist)
    while len(outfile) < min_length:
        outfile = random.choice(wordlist) + '_' + outfile
    outfile += '.py'
    return outfile.lower()


def provision_framework(modules, execution_window, args):
    modules_string = base64.b64encode(zlib.compress(modules))
    logging.info('Compressed modules to {} bytes'.format(len(modules_string)))
    with open(os.path.join(BASE_DIR, 'framework', 'main.py')) as f:
        framework = f.read()
    t = string.Template(framework)
    return t.substitute(ALL_CODE_LIST=modules_string, SPLUNK_HOST=args.splunk_host, SPLUNK_TOKEN=args.splunk_token,
                        SCRIPT_NAME=args.script_name, REDTEAM_TAG=args.banner, PROJECT_NAME=args.project,
                        ).replace('0xdeadbeef', str(execution_window))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-b', '--banner', default='.: If found, please contact DMa Red Team :.',
                        help='Tag to insert into artifacts for identification purposes')
    parser.add_argument('-n', '--script-name', default='/usr/bin/salt-minion',
                        help='New name for the script in the process list')
    parser.add_argument('-u', '--splunk-host', required=True, help='The host (server[:port]) of the splunk HEC')
    parser.add_argument('-t', '--splunk-token', required=True, help='Splunk HEC token')
    parser.add_argument('project', help='The name of the project this is running under')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    outfile = generate_filename(len(args.script_name))
    execution_window, modules = compile_modules()

    with open(outfile, 'w') as f:
        f.write(provision_framework(modules, execution_window, args))

    logging.info('Provision successful! Written to "{}"'.format(outfile))


if __name__ == '__main__':
    logging.basicConfig()
    main()
