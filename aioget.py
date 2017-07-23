#!/usr/bin/env python3

import os
import asyncio
import aiohttp
import aiofiles
import datetime
import argparse

from urllib.parse import unquote
from time import time
from blessings import Terminal
from functools import wraps


__version__ = '0.2.1'
term = Terminal()
wrap = dict()


def limit(number):
    ''' This decorator uses Semaphores to limit the number
    of concurrent coroutines running at the same time
    '''
    
    sem = asyncio.Semaphore(number)
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args):
            async with sem:
                return await func(*args)
        return wrapped
    return wrapper

SUFFIXES = {1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']}

def approximate_size(size, a_kilobyte_is_1024_bytes=True):
    '''
    Humansize.py from Dive into Python3
    Mark Pilgrim - http://www.diveintopython3.net/
    
    Returns human-readable filesizes
    '''

    size = float(size)
    assert size >= 0

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000
    for suffix in SUFFIXES[multiple]:
        size /= multiple
        if size < multiple:
            return '{0:.1f}{1}'.format(size, suffix)

    raise ValueError('number too large')

@limit(4)
async def download(session, link):   
    global term
    global wrap
    
    filename = os.path.basename(unquote(link))
    eta = 'unknown '
    bytes_so_far = 0
    AVAIL_WIDTH = (term.width - len(filename)) - 58 
    
    async with session.get(link) as resp:
        async with aiofiles.open(filename, 'wb') as fh:
            try:
                total_size = int(resp.headers['CONTENT-LENGTH'])
            except (ValueError, KeyError, TypeError):
                total_size = 'unknown'
            
            # Below are the registers to calculate network transfer rate
            time_register = time()
            speed = 0.0
            speed_list = []
            bytes_register = 0.0
            eta = 'unknown '
            
            # Loop that reads in chunks, calculates speed and 
            # print the progress
            while True:
                chunk = await resp.content.read(4096)
                if not chunk:
                    break
                
                # Update Download Speed every 1 second
                if time() - time_register > 0.5:
                    speed = (bytes_so_far - bytes_register) / \
                        (time() - time_register)
                    speed_list.append(speed)

                # Set register properly for future use
                    time_register = time()
                    bytes_register = bytes_so_far

                # Estimative of remaining download time
                    if total_size != 'unknown' and len(speed_list) == 3:
                        speed_mean = sum(speed_list) / 3
                        eta_sec = int((total_size - bytes_so_far) / speed_mean)
                        eta = str(datetime.timedelta(seconds=eta_sec))
                        speed_list = []

                bytes_so_far += len(chunk)
                percent = int(bytes_so_far * 100 / total_size)
                current = approximate_size(bytes_so_far).center(9)
                total = approximate_size(total_size).center(9)
                shaded = int(float(bytes_so_far) / total_size * AVAIL_WIDTH)                
                
                await fh.write(chunk)
                with term.location(0, wrap[filename]), term.hidden_cursor():
                    print("{0} {1}% [{2}{3}{4}] {5}/{6} {7} eta{8}".format(filename,
                                                      str(percent).center(4),
                                                      '=' * (shaded - 1),
                                                      '>',
                                                      ' ' * (AVAIL_WIDTH - shaded),
                                                      current,
                                                      total,
                                                      (approximate_size(speed) + '/s').center(11),
                                                      eta.center(10)))

                
async def run(args):
    tasks = []
    global wrap
    
    # Wrapper for finding which line to print progress
    wrap = {os.path.basename(unquote(filename)): i for i, filename in enumerate(args) }

    async with aiohttp.ClientSession() as session:
        for link in args:
            task = asyncio.ensure_future(download(session, link))
            tasks.append(task)
        
        responses = asyncio.gather(*tasks)
        await responses

    
def main():
    p = argparse.ArgumentParser(prog='aioget', description="Downloads concurrently a list of files")
    p.add_argument("urls", help="Download links", nargs='*')
    p.add_argument("-f", "--from_file", metavar='FILE', type=str, help="Reads urls from a file")
    args = p.parse_args()
    
    if args.from_file:
        with open(args.from_file, 'r') as fh:
            c = fh.readlines()
            links = [ elem.strip() for elem in c ]
    else:
        links = args.urls

    print(term.clear)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(run(links)))

if __name__ == '__main__':
    main()
