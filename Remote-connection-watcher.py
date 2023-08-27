# Remote connection watcher
## Python script for monitoring remote connections
##### By DFT
##### 2023-08-27

import curses
import socket
import threading
import psutil
import time
import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_FILE = "keyModuleInfo.txt"

LOOP = False

SLEEP = 2000  # Milliseconds

AUTO_SAVE_TIMER = 180  # Seconds

REMOTE_IPS = []

DNS_REV = []

DNS_LOOKUP = []


def cpu_info():
    saida = "\nCPU usage: " + str(psutil.cpu_percent(interval=1)) + \
            "\n\nMemory usage: " + str(psutil.virtual_memory()) + \
            "\n\nDisk usage: " + str(psutil.disk_partitions()) + \
            "\n\nNetwork: " + str(psutil.net_io_counters()) + "\n"
    return saida


def save_data():
    # Dumping the data to log
    global LOG_FILE
    try:
        with open(LOG_FILE, "a") as fp:
            fp.write("\n" + "-" * 80 + "\n")
            fp.write("Remote IP list\t\t\t" + "Count: " + str(len(REMOTE_IPS)) + "\t\t" + datetime.datetime.now().strftime(DATE_FORMAT) + "\n")
            for r in REMOTE_IPS:
                fp.write(str(r) + "\n")
            fp.write("\n" + "-" * 80 + "\n")
            fp.write("Remote IP DNS Reverse\t\t\t" + "Count: " + str(len(DNS_REV)) + "\t\t" + datetime.datetime.now().strftime(DATE_FORMAT) + "\n")
            for r in DNS_REV:
                fp.write(str(r) + "\n")
    except Exception as e:
        print(e)


def read_connections():
    global REMOTE_IPS
    saida = str("REMOTE\t\t\t\t\tSTATE\t\t\t\tPID\n")
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        pid = conn.pid or "-"
        try:
            process = psutil.Process(conn.pid)
            process_name = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            process_name = "N/A"

        remote_address = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
        status = conn.status
        if remote_address != "-" and conn.raddr.ip != "127.0.0.1":
            if remote_address not in REMOTE_IPS:
                REMOTE_IPS.append(remote_address)
            saida = saida + str(str(remote_address) + "\t\t\t" + str(status) + "\t\t\t" + str(pid) + " " + process_name + "\n")
    return saida


def help_info():
    saida = "\t\t\t\t------------------\n\t\t\t\t   SCRIPT USAGE " \
        + "\n\t\t\t\t------------------" + "\n\n\n" \
        + "\n\t" + "(h) Show script usage." \
        + "\n\t" + "(t) Show terminal number of lines" \
        + "\n\t" + "(T) Define SLEEP time" \
        + "\n\t" + "(C) Show actual connections" \
        + "\n\t" + "(R) Show remote IP list" \
        + "\n\t" + "(W) Save data to file keyModuleInfo.txt" \
        + "\n\t" + "(D) Process DNS entries of remote IP list" \
        + "\n\t" + "(S) Switch LOOP state" \
        + "\n\t" + "(i) Show cpu_info" \
        + "\n\t" + "(Q) Quit"
    return saida


def dns_info():
    global REMOTE_IPS, DNS_REV, DNS_LOOKUP

    try:
        saida = ""

        for (i, ip) in enumerate(REMOTE_IPS):

            ip_address = str(ip.split(":")[0])

            if ip_address not in DNS_LOOKUP:

                rev_dns = get_reverse_dns(ip_address)

                DNS_LOOKUP.append(ip_address)

                if rev_dns != "Reverse DNS not found":
                    DNS_REV.append(rev_dns)

                if i < 25: 
                    saida += "\n" + "-" * 80 + "\nIP: " + ip_address + "\n" + str(rev_dns)
                
    except Exception as e:
        saida = str(e)

    return saida


def get_reverse_dns(ip_address):
    try:
        host_name = socket.gethostbyaddr(ip_address)
        return host_name
    except socket.herror:
        return "Reverse DNS not found"


def auto_save(terminal_screen):
    # Auto save loop
    global LOOP, AUTO_SAVE_TIMER
    while True:
        LOOP = False
        terminal_screen.addstr("\nAuto saving data... Please wait")
        terminal_screen.refresh()
        terminal_screen.addstr("\nReverse DNS checking.")
        terminal_screen.refresh()
        # Checking the reverse DNS info before write the logs
        dns_info()
        terminal_screen.addstr("\nWriting file...")
        terminal_screen.refresh()
        # Saving the data
        save_data()
        LOOP = True
        terminal_screen.addstr("Done!\n")
        terminal_screen.refresh()
        time.sleep(AUTO_SAVE_TIMER)


def main(terminal_screen):
    global SLEEP, LOOP, DATE_FORMAT, REMOTE_IPS

    terminal_screen.clear()
    terminal_screen.timeout(SLEEP)
    terminal_screen.addstr("Script in execution. Press 'q' to leave or 'h' to show script usage.\n")
    
    timer_thread = threading.Thread(target=auto_save, args=(terminal_screen,))
    timer_thread.daemon = True
    timer_thread.start()

    while True:
        key = terminal_screen.getch()

        if key == ord('q'):
            # Quit
            terminal_screen.addstr("\nExiting...\n")
            terminal_screen.refresh()
            break

        if key == ord('h'):
            # Help
            LOOP = False
            terminal_screen.clear()
            help_message = help_info().split("\n")
            for (i, row) in enumerate(help_message[:25]):
                terminal_screen.addstr(row + "\n")
            terminal_screen.refresh()

        if key == ord('S'):
            # Switch LOOP state
            terminal_screen.clear()
            terminal_screen.addstr("\nSwitching loop state: " + str(LOOP))
            LOOP = not LOOP
            terminal_screen.addstr(" -> " + str(LOOP) + "\n")
            terminal_screen.refresh()

        if key == ord('W'):
            # Save data to file keyModuleInfo.txt
            terminal_screen.addstr("\nSaving the data to the output file keyModuleInfo.txt\n")
            terminal_screen.refresh()
            save_data()
            terminal_screen.addstr("\nDone! Data saved.\n\t\t\tPress `S` to continue looping.")
            terminal_screen.refresh()

        if key == ord('t'):
            # Print terminal number of lines
            terminal_screen.addstr("\nTerminal number of lines: " + str(curses.LINES) + "\n")
            terminal_screen.refresh()

        if key == ord('D'):
            # Process DNS entries of remote IP list
            terminal_screen.clear()
            terminal_screen.addstr("\nProcessing DNS entries of remote IP list with size: " + str(len(REMOTE_IPS)) + ". Wait...\n")
            terminal_screen.refresh()
            for (i, row) in enumerate(dns_info().split("\n")[:20]):
                terminal_screen.addstr(str(row) + "\n")
            terminal_screen.addstr("\n\n\t\t\tPress `S` to continue looping.")
            terminal_screen.refresh()

        if key == ord('T'):
            # Define SLEEP time
            terminal_screen.timeout(-1)
            try:
                curses.echo()
                terminal_screen.addstr(f"\nActual SLEEP value: {SLEEP}\nEnter new SLEEP time: ")
                SLEEP = int(terminal_screen.getstr().decode("utf-8"))
                terminal_screen.addstr(f"\nNew SLEEP time: {SLEEP}\n")
            except Exception as e:
                terminal_screen.addstr("\nException. " + str(e) + "\n")
            curses.noecho()
            terminal_screen.timeout(SLEEP)
            terminal_screen.refresh()

        if key == ord('i'):
            # Print cpu_info
            terminal_screen.clear()
            terminal_screen.addstr(cpu_info())
            terminal_screen.refresh()

        if key == ord('R'):
            # Print REMOTE_IPS
            terminal_screen.clear()
            terminal_screen.addstr("REMOTE IP LIST\n---------------")
            for i, row in enumerate(REMOTE_IPS[:25]):
                terminal_screen.addstr("\n" + row)
            terminal_screen.addstr("\n\n\t\t\tPress `S` to continue looping.")
            terminal_screen.refresh()
            LOOP = False

        if key == ord('C') or LOOP:
            # Print actual connections
            terminal_screen.clear()
            terminal_screen.addstr(datetime.datetime.now().strftime(DATE_FORMAT) + " \tSLEEP: " + str(SLEEP) + "ms\t\tREMOTE IPS: " + str(len(REMOTE_IPS)) + "\n")
            result = read_connections().split('\n')
            for i, row in enumerate(result[:25]):
                terminal_screen.addstr("\n" + row)
            terminal_screen.refresh()


if __name__ == "__main__":
    curses.wrapper(main)