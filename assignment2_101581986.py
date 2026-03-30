"""
Author: Aanod Mohamed
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""


import socket
import threading
import sqlite3
import os
import platform
import datetime

print("Python Version:", platform.python_version())
print("Operating System:", os.name)


# this dictionary stores the numbers of ports and assigns the services names associated to them 
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

class NetworkTool:
    def __init__(self, target):
        self.__target = target
    # Q3: What is the benefit of using @property and @target.setter?
    # The benifit of using the magic @property getter and @target.setter setter is that it allows us to later acesss target
    # as if it were a public property. 
    # This means you can acess target just typing its property name instead of through another method leading to clean uniform syntax. 

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, target):
        if(target == ""):
            print("Error: Target cannot be empty")
        else:
            self.__target = target 

    def __del__(self):
        print("NetworkTool instance destroyed")

    

# Q1: How does PortScanner reuse code from NetworkTool?
# PortScanner reuses code from NetworkTool by being the child class inheriting the properities and methods of its parent class NetworkTool. 
# PortScanner has access to NetworkTool's  magic getters and setters and their ability to access target as if it were a public property.
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()
      
    def scan_port(self, port):
        # Q4: What would happen without try-except here?
        # What would happen is any error would crash the code without offering the user an explaination or assitance.
        # Now with our try except here we can cleany catch the error so it does not crash the program
        # and output a clear error message explaining what went wrong.
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port)) 
            if result == 0:
                status = "Open"
            else:
                status = "Closed"
            
            if port in common_ports:
                service_name = common_ports[port]
            else:
                service_name = "Unknown"

            self.lock.acquire()
            self.scan_results.append((port, status, service_name))
            self.lock.release()
        except socket.error as e:
            print(f"Error scanning port {port}: {e} ")
        finally:
            sock.close()

    def get_open_ports(self):
        return [result for result in self.scan_results if result[1] == "Open"]
    
# Q2: Why do we use threading instead of scanning one port at a time?
    # We use threading to utilize parallel processing so ports are scanned at once for speed and efficiency. 
    # If we tried scanning 1024 ports without threads the output would come slowly.
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
             thread_Obj = threading.Thread(self.scan_port, args=(port,))
             thread_Obj.start()
             threads.append(thread_Obj)
        for thread in threads:
                thread.join()


def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT,
        port INTEGER,
        status TEXT,
        service TEXT,
        scan_date TEXT
        )""")

        for result in results:
            port, status, service_name = result
            cursor.execute("""INSERT INTO scans (target, port, status, service_name, scan_date) VALUES (?, ?, ?, ?, ?)""", 
            (target, port, status, service_name, str(datetime.datetime.now())))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(e)


def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM scans""")
        rows = cursor.fetchall()
        for row in rows:
            id, target, port, status, service_name, scan_date = row
            print(f"[{scan_date}] {target} : Port {port} ({service_name}) - {status}")
        conn.close()
    except sqlite3.Error:
        print("No past scans found")

# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    try:
        target = input("Please enter a target IP address")
        if target == "":
            target = "127.0.0.1"
        start_port = input("please enter a starting port number from 1 to 1024")
        end_port = input("please enter an ending port number from 1 to 1024 (must be greater or equal to start port)")
        start_port = int(start_port) 
        end_port = int(end_port)
        if start_port >= 1 and start_port <= 1024 and end_port >= start_port and end_port >=1 and end_port <= 1024:
            print("all valid inputs thank you")
        else:
            raise ValueError("Ports must be between 1 and 1024, start port MUST be less than or equal to end port")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


    PortScannerObj = PortScanner(target)
    print(f"Scanning {target} from port {start_port} to {end_port}...")
    PortScannerObj.scan_range(start_port, end_port)
    results = PortScannerObj.get_open_ports()
    print("--------------------- SCAN RESULTS ----------------")
    for result in results:
        port, status, service_name = result
        print(f"Port {port}: {status} ({service_name})")
    print("---------------------------------------------------")
    save_results(target, results)
    scanHistory = input("Would you like to see past scan history? (yes/no): ")
    if scanHistory == "yes":
        load_past_scans()
        print("Scan Complete")
    else:
        print("Scan Complete")


    




# Q5: New Feature Proposal
# Your 2-3 sentence description here...
# Diagram: See diagram_studentID.png in the repository root