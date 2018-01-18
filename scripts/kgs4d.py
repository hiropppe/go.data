#!/usr/bin/env python

import lxml.html
import os
import urllib
import sys
import traceback

from urllib2 import urlopen

save_dir = sys.argv[1]

root = lxml.html.parse(urlopen("https://www.u-go.net/gamerecords-4d/")).getroot()
for a in root.cssselect('a'):
    try:
        href = a.get('href')
        if href.endswith('.tar.gz'):
            save_path = os.path.join(save_dir, os.path.basename(href))
            if not os.path.exists(save_path):
                print("Downloading {:s}".format(href))
                urllib.urlretrieve(href, save_path)
    except KeyboardInterrupt:
        break
    except:
        err, msg, _ = sys.exc_info()
        sys.stderr.write("{} {}\n".format(err, msg))
        sys.stderr.write(traceback.format_exc())
