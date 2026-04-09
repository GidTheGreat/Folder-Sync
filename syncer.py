#!/usr/bin/env  python3

""" sync a folder i edit on android with the project root in proot whenever i modify it"""

import os
import asyncio
import sys
import subprocess

def get_mtimes(files_present,android_dir,file_mtimes,init=False):
    """gets mtimes on each call"""
    
    for file in files_present:
        file_path = os.path.join(android_dir,file)
       
        if init:
            file_mtimes[file] = os.stat(file_path).st_mtime #get mtime and store it
        else:
                if file_mtimes[file] != os.stat(file_path).st_mtime:
                    file_mtimes[file] = os.stat(file_path).st_mtime
                    print("copying changed files")
                    subprocess.run("rsync -av /storage/emulated/0/workspace/src ~/viteR",shell=True)
                
async def periodic_checker(files_present,android_dir,file_mtimes):
    
    while True:
          
          get_mtimes(files_present,android_dir,file_mtimes)
          print("sleeping until next interval")
          await asyncio.sleep(5)
    
async def main():
        #initial modification time
        print(sys.argv)
        file_mtimes = {}
        
        #path of shared dir where i edit files
        android_dir = "/storage/emulated/0/workspace/src"
        
        #list of files present
        files_present = os.listdir(android_dir)
        
        get_mtimes(files_present,android_dir,file_mtimes,init=True)
        print(file_mtimes)
        await asyncio.create_task(periodic_checker(files_present,android_dir,file_mtimes))
      
      

      
      
if __name__ == "__main__"  :
      asyncio.run(main())  
      
      
    
  
    

