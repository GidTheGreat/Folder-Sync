#!/usr/bin/env  python3

""""
syncer - synchronize folders between environments.

Designed for workflows where code is edited in one environment
(e.g., Android) and executed in another (e.g., proot).
"""

import os
import logging
import threading
from inotify_simple import INotify,flags
import time
from collections import defaultdict
import asyncio
import sys
import subprocess
import argparse


def parse_init():
    """initialize args processing and help for module"""
    parser = argparse.ArgumentParser(
        prog ="syncer",
        description=("Synchronize files between " 
        "two environments.\n"
       "Example: edit code on Android and run"
        "it inside a proot distro. "
        "NB:IF NO ARGUMENTS ARE SPECIFIED ENSURE YOU "
        "HAVE A FILE CALLED 'sdst.py'(LOWERCASE) WITH "
        "TWO VARIABLES EXACTLY LIKE THIS"
       "src=PATH,dst=PATH,PATHS MUST LEAD TO FOLDERS" ))
    #____OPTIONS____
    parser.add_argument("-i", "--interval", type=int,
    metavar="SECONDS", default=5,
    help="interval between synchronization cycles" )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--local", 
    action="store_const", dest="mode", const="local",
    help="perform local synchronization only")

    group.add_argument("-c", "--cloud",
    action="store_const", dest="mode", const="cloud",
    help="perform local and cloud synchronization only")

    parser.set_defaults(mode="local")

    parser.add_argument("-v", "--verbose", 
    action="store_true",help="detailed logs")


    parser.add_argument("source", nargs="*",
    help= "path to the directory where files are being edited")

    parser.add_argument("destination", nargs="*",
    help= "path to the dirextory where files are executed")

    parser.epilog = """
    Examples:
      syncer -i 5 -l ~/project /proot/project\n
        syncer -i 10 -c ~/project /proot/project
        """
    return parser
def path_util(path):
     """normalize paths so no relative path"""
     parsed_path= os.path.abspath(os.path.expanduser(path))
     return parsed_path
     
def create_source_dest():
    """load saved paths"""
    from sdst import src,dst

    source_path= path_util(src)
    dest_path = path_util(dst)
    return source_path, dest_path

class FileFlux():
  """Track files in directory for flux"""
  def __init__(self,source,destination,verbose=False):
    if verbose:
      self.level = logging.DEBUG
    else:
      self.level = logging.WARNING
    logging.basicConfig(format='%(asctime)s %(message)s',level=self.level)
    self.inotify = INotify() #init tracker object
    self.path = source #path of dir to be trackex
    self.dest = destination
    self.tracked_dirs = {} # paths tracked with watch descriptor attached
    self.running_thread = None
    self.new_save = False
    self.lock = threading.Lock()
    self.event_timers = defaultdict(str)
  
  
  def record_close(self):
    with self.lock:
      self.new_save = True
      logging.info("closed file")
      sync_info =  subprocess.check_output(f"rsync -av {self.path} {self.dest}",text=True,shell=True)
      logging.debug("Change detected syncing")
      logging.debug(sync_info)
      
  def handle_events(self,events):
    for event in events:
        logging.debug(f"{event.name},{flags.from_mask(event.mask)}")
        
        if event.mask & flags.CLOSE_WRITE:
          logging.info(f"Change detected")
          #coalesce signals so we get one notification
          with self.lock:
            old = self.event_timers.get(event.name)
            if old:
              old.cancel()
          
          t = threading.Timer(1,self.record_close)
          
          self.event_timers[event.name] = t
          t.start()
          
                    
        elif event.mask & flags.CREATE and event.mask & flags.ISDIR:
          logging.debug(f"New dir detected:{event.name}\n Adding Tracker")
          self.add_tracker()
    
  def start_watcher(self):
    """Start a thread to watch for file flux"""
    if self.running_thread:
      logging.debug("Running event watcher active")
      return
    try:
      event_thread = threading.Thread(target=self.event_thread,daemon = True)
      event_thread.start()
      self.running_thread = event_thread
      event_thread.join()
    except Exception as e:
      logging.error(e)
    
  def add_tracker(self):
    """Add tracker and get watch descriptor for each dir and its contents"""
    for dir, sub_dir, file in os.walk(self.path):
      #self.path_util(dir,file)
      if dir not in self.tracked_dirs:
        try:
          wd = self.inotify.add_watch(dir,flags.CREATE | flags.DELETE | flags.MODIFY | flags.CLOSE_WRITE | flags.ATTRIB | flags.MOVED_FROM | flags.MOVED_TO)
          logging.info(f"Tracking changes in :{dir}")
          self.tracked_dirs[dir] = wd
        except Exception as e:
          logging.error("Failed to add tracker  to dir:{dir}")
  
  def event_thread(self):
    """Start tracking file change events"""
    self.add_tracker()
    while True:
      events = self.inotify.read()
      self.handle_events(events)
      
                
if  __name__ == "__main__":
  parser=parse_init()
  args =parser.parse_args()
  if not args.source or not args.destination:
    source_path,destination_path =create_source_dest()
    source_dir = source_path
    dest_dir = destination_path

  else:
    source_dir = args.source[0]
    dest_dir = args.destination[0]
    
  fileflux = FileFlux(source_dir,dest_dir,args.verbose)
  fileflux.start_watcher()
  


      
      
      
      
    
  
    

