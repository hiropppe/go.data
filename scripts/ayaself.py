#!/usr/bin/env python

import lxml.html
import os
import urllib
import sys
import tarfile
import traceback

save_dir = sys.argv[1]

root = lxml.html.parse("http://www.yss-aya.com/ayaself/ayaself.html").getroot()
for a in root.cssselect('a'):
    try:
        href = a.get('href')
        if href.endswith('.tar.bz2'):
            save_path = os.path.join(save_dir, os.path.basename(href))
            if not os.path.exists(save_path):
                print("Downloading {:s}".format(href))
                urllib.urlretrieve(os.path.join("http://www.yss-aya.com/ayaself/", href), save_path)
    except KeyboardInterrupt:
        break
    except:
        err, msg, _ = sys.exc_info()
        sys.stderr.write("{} {}\n".format(err, msg))
        sys.stderr.write(traceback.format_exc())
