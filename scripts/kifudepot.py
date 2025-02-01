#!/usr/bin/env python3

import lxml.html
import os
import re
import requests
import socket
import sys
import time
import traceback

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError

BASE_URL = 'http://kifudepot.net/'

MAX_PAGE = 2608

page = 1


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3), retry=retry_if_exception_type(requests.exceptions.ConnectionError | requests.exceptions.ConnectTimeout))
def retrieve_sgf(content_url, sgf_name, save_dir):
    date_str = re.findall(r"\d{4}[\_\-]\d{2}[\_\-]\d{2}", sgf_name)
    date_str = date_str[0] if date_str else "0000-00-00"
    date_str = re.sub('[\_\-]', '', date_str)
    save_dir = os.path.join(save_dir, date_str)
    os.makedirs(save_dir, exist_ok=True)
    sgf_path = os.path.join(save_dir, sgf_name)
    if os.path.exists(sgf_path):
        print('SGF already exists: {:s}'.format(sgf_path))
    else:
        print('Downloading {:s}'.format(sgf_name))
    content = requests.get(content_url).content
    root = lxml.html.fromstring(content)
    sgf = root.cssselect('textarea#sgf')[0].text

    with open(sgf_path, 'w') as f:
        f.write(sgf)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3), retry=retry_if_exception_type(requests.exceptions.ConnectionError | requests.exceptions.ConnectTimeout))
def parse_list(page, save_dir):
    list_url = f"http://kifudepot.net/index.php?page={page}"
    print(f"Fetch page: {list_url}")
    content = requests.get(list_url).text
    root = lxml.html.fromstring(content)
    data_list = root.cssselect('table.dataTable tr')
    for rownum in range(1, len(data_list)):
        try:
            data = data_list[rownum]
            content_url = os.path.join(BASE_URL, data.cssselect('td.td_ev a')[0].attrib['href'])
            game_name = data.cssselect('td.td_ev a')[0].text
            black_name = data.cssselect('td.td_pb div')[0].text
            white_name = data.cssselect('td.td_pw div')[0].text
            game_date = data.cssselect('td.td_dt')[0].text
            sgf_name = '_'.join([game_name, black_name, white_name, game_date])
            sgf_name = re.sub(r'[\s\u3000]+', '_', sgf_name) + '.sgf'
            retrieve_sgf(content_url, sgf_name, save_dir)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as exc:
            err, msg = type(exc).__name__, str(exc)
            print(f"{err} {msg}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)


socket.setdefaulttimeout(180)

save_dir = sys.argv[1]

try:
    while page < MAX_PAGE:
        try:
            parse_list(page, save_dir)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as exc:
            err, msg = type(exc).__name__, str(exc)
            print(f"{err} {msg}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            raise exc
        page += 1
except SystemExit:
    pass

