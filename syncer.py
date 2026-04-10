#!/usr/bin/env  python3

""""
syncer - synchronize folders between environments.

Designed for workflows where code is edited in one environment
(e.g., Android) and executed in another (e.g., proot).
"""

import os
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
    
def get_mtimes(files_present,source_dir,dest_dir,
file_mtimes,init=False,v=False):
    """gets mtimes on each call"""
    
    for file in files_present:
        file_path = os.path.join(source_dir,file)
       
        if init:
            file_mtimes[file] = os.stat(file_path).st_mtime #get mtime and store it
            if v:
                print(f"Succesfully accessed and  stored "
                f"initial modification time of file:'{file}'")
        else:
                
                if file_mtimes[file] != os.stat(file_path).st_mtime:
                    
                    file_mtimes[file] = os.stat(file_path).st_mtime
                    sync_info =  subprocess.check_output(f"rsync -av {source_dir} {dest_dir}",
                    text=True,shell=True)
                    if v:
                        print("Change detected syncing")
                        print(sync_info)
                
async def periodic_checker(files_present,source_dir,dest_dir,file_mtimes,
v,interval=5):
    
    while True:
          get_mtimes(files_present,source_dir,dest_dir,file_mtimes,init=False,v=v)
          if v:
             print("sleeping until next interval")
          await asyncio.sleep(interval)
    
async def main():
        #initial modification time
        parser=parse_init()
        args =parser.parse_args()
        source_dir = None #path of where i edit files
        dest_dir = None #path of where i run files
        file_mtimes = {}
        
        if not args.source or not args.destination:
            source_path,destination_path = create_source_dest()
            source_dir = source_path
            dest_dir = destination_path

        else:
            source_dir = args.source[0]
            dest_dir = args.destination[0]
            
        #list of files present
        files_present = os.listdir(source_dir)
        if args.verbose:
            print(f"Syncing started in mode:'{args.mode}'"
            "watching for file "
            f"changes in:'{source_dir}' and syncing those "
            f"changes in:'{dest_dir}', "
            f"sync interval is:'{args.interval}' seconds"
            f"files to be monitored:'{files_present}'")
        
        
        
        get_mtimes(files_present,source_dir,dest_dir,
        file_mtimes,init=True,v=args.verbose)
        await asyncio.create_task(periodic_checker(files_present
        ,source_dir,dest_dir,file_mtimes,args.verbose,interval=args.interval))
      
if __name__ == "__main__"  :
      asyncio.run(main())  
      
      
    
  
    

