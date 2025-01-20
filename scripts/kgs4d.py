#!/usr/bin/env python

import lxml.html
import os
import urllib
import sys
import traceback

import urllib.request

save_dir = sys.argv[1]

root = lxml.html.parse(urllib.request.urlopen("https://www.u-go.net/gamerecords-4d/")).getroot()
for a in root.cssselect('a'):
    try:
        href = a.get('href')
        if href.endswith('.tar.gz'):
            save_path = os.path.join(save_dir, os.path.basename(href))
            if not os.path.exists(save_path):
                print(f"Downloading {href}")
                urllib.request.urlretrieve(href, save_path)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(type(e).__name__, str(e), file=sys.stderr)
