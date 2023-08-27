# Remote connection watcher
## Python script for monitoring remote connections

----
#### Install:
- Make a directory for it; because the generated log file.
- If you are using Windows, you probably need run: pip install windows_curses
- pip install psutil
- That's it and that's all =P

----
#### SCRIPT USAGE
It is based in a loop. 
You can handle the execution by key pressing (Case sensitive)
```
[T] Define SLEEP time
[S] Switch LOOP state
[i] Show cpu_info
[R] Show remote IP list
[C] Show actual connections
[D] Process DNS entries of remote IP list
[W] Save data to file keyModuleInfo.txt
[t] Show terminal number of lines
[Q] Quit
[h] Show script usage
```

----
#### Procedure explained

- Start the script
- press **T**
- type 250
- press **S**
- in another window, open the log file.

The script will basically scan the proc directory for processes that have inet connection. We can use a pretty consistent work code abstracted in psutil library to accomplish this scan with great performatic and with a multi plataform way.


----


##### By DFT
##### 2023-08-27

