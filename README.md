# Syncer

Syncer is a lightweight file synchronization tool for development workflows where code is edited in one environment (e.g. Android) and executed in another (e.g. proot/Linux). It watches filesystem changes using inotify and automatically syncs directories using rsync.

---

## Features

- Real-time directory monitoring via inotify
- Automatic rsync-based synchronization on file changes
- Debounced event handling to prevent redundant syncs
- Recursive directory tracking
- CLI configuration with fallback config file support
- Verbose logging mode for debugging

---

## Requirements

- Python 3.8+
- Linux (inotify support required)
- rsync installed
- Python dependency:

 ## Installation
 ``` bash
 git clone https://github.com/your-username/syncer.git
 cd syncer
 chmod +x syncer.py
```
 ## Usage
 ### Direct Mode
 ``` bash
 python syncer.py /path/to/source /path/to/destination
```
### Config File Mode
- For persistence  so you don't  keep defining  the paths,you can have a config file and name it
  ``` bash
  sdst.py
  ```
  - Then define paths as variables as below
    ``` bash
    src = "/path/to/source"
    dst = "/path/to/destination"
    ```

## Future Improvements 
- Cloud sync support (SSH/S3/etc.)
- Bidirectional sync
- Ignore/include rules
- Conflict resolution system
- Config file standardization (TOML/JSON)
- System service support
  
## Example Workflow
- Edit code on mobile or external environment
- Syncer detects changes
- Automatically syncs to execution environment
- Run updated code immediately
