#!/usr/bin/env python3
import argparse
import sys
import os
import errno
import datetime
import time
import pathlib
import json
import requests


### Variables that need to be set by user
urlscan_api = ''
### urlscan's config directory
urlscan_dir = str(pathlib.Path.home()) + '/.urlscan'


### Stop editing!

## argparse arguments
parser = argparse.ArgumentParser(description="Wrapper for urlscan.io's API")

subparsers = parser.add_subparsers(help='sub-command help')

## Scan parser
parser_scan = subparsers.add_parser('scan', help='scan a url')
parser_scan.add_argument('--url', help='URL(s) to scan', nargs='+', metavar='URL', required='True')
parser_scan.add_argument('-s', '--save', help='save initiated scans with a timestamp to index file for future use', action="store_true")
parser_scan.add_argument('-q', '--quiet', help='suppress output', action="store_true")


## Retrieve parser
parser_retrieve = subparsers.add_parser('retrieve', help='retrieve scan results')
parser_retrieve.add_argument('--uuid', help='UUID(s) to retrieve scans for', nargs='+', metavar='UUID', required='True')
parser_retrieve.add_argument('-d', '--dir', help='directory to save scans to', metavar='DIRECTORY', default='saved_scans')
parser_retrieve.add_argument('-q', '--quiet', help='suppress output', action="store_true")

args = parser.parse_args()


if urlscan_api == '':
    print('Please input valid urlscan_api value in ' + sys.argv[0])
    sys.exit(1)

def submit():
    for target_urls in args.url:
        headers = {
            'Content-Type': 'application/json',
            'API-Key': urlscan_api,
        }

        data = '{"url": "%s"}' % target_urls

        response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, data=data)

        ## end POST request

        r = response.content.decode("utf-8")

        if not args.quiet:
            print(r)

        if args.save:
            current_time = int(time.time())
            human_readable_time = str(datetime.datetime.fromtimestamp(current_time))
            save_history(human_readable_time, str(r))


        time.sleep(3)

def query():
    for target_uuid in args.uuid:
        response = requests.get("https://urlscan.io/api/v1/result/%s" % target_uuid)

        r = response.content.decode("utf-8")

        if not args.quiet:
            print(r)

        if hasattr(args, 'dir'):
            save_to_dir(str(args.dir), target_uuid, str(r))

        time.sleep(3)

def save_history(x, y):
    history_file = urlscan_dir + '/history.txt'

    if not os.path.exists(urlscan_dir):
        os.makedirs(urlscan_dir)

    with open(history_file, 'a') as out:
        out.write(x + '\n' + y + '\n' + '\n')

def save_to_dir(x, y, z):
    if not os.path.exists(x):
        os.makedirs(x)

    save_file_name = x + '/' + y

    path_to_file = pathlib.Path(save_file_name)
    if not path_to_file.is_file():
        with open(save_file_name, 'a') as out:
            out.write(z)

def main():
    if hasattr(args, 'url'):
        submit()

    if hasattr(args, 'uuid'):
        query()


main()
