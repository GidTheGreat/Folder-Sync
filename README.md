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

 ## Usage
  Direct Mode
 python syncer.py /path/to/source /path/to/destination
