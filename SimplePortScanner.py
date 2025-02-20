import socket  # To communicate with other machines using TCP and UDP protocols
import termcolor
import threading
from queue import Queue
import ipaddress #to validate user inputs
import sys  # for exit
import pyfiglet  # for ASCII art

print_lock = threading.Lock()
q = Queue()

invalid_ip =[]
def checkIP(targets):
	global invalid_ip
	invalid_ip = [] #reset list
	for ip in targets:
		ip = ip.strip()
		try:
			ipaddress.ip_address(ip) #check validity of ipadress
			
		except ValueError:
			invalid_ip.append(ip) #append any invalids
			
	return not bool(invalid_ip)		


# Scan a single port
def ScanPort(ipaddress, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP communication over IPv4
    sock.settimeout(0.5)  # Prevent hanging on connection attempts
    try:
        sock.connect((ipaddress, port))
        with print_lock:
            print(f"[+] Port {port} is open")
    except:
        pass  # Ignore closed ports
    finally:
        sock.close()

# Worker thread function
def Threader(target):
    while True:
        port = q.get()  # Get port number from queue
        ScanPort(target, port)  # Scan that port
        q.task_done()  # Mark as done


def Scan(target, ports):
    print(termcolor.colored(f"\nStarting Scan For {target}", 'blue'))
   
    q = Queue()  # Create a new queue for each IP
   
    # Fill queue with ports
    for i in range(1, ports + 1):
        q.put(i)

    def Threader():
        while not q.empty():
            port = q.get()
            ScanPort(target, port)
            q.task_done()

    threads = []  # List to keep track of threads
   
    # Start worker threads
    for _ in range(30):  # Define 30 threads
        t = threading.Thread(target=Threader)
        t.daemon = True
        t.start()
        threads.append(t)

    q.join()  # Wait for all threads to finish scanning this IP

    # Ensure all threads finish before moving to the next IP
    for t in threads:
        t.join()



ascii_art = pyfiglet.figlet_format("NUSIBA'S" + '\n' + "PORT SCANNER")
print(ascii_art)
print('\n' + "*" * 60)
print()


targets = input("[*] Enter Targets To Scan (split them by ','): ")
split_targets = targets.split(",")
checkIP(split_targets)

if not checkIP(split_targets):
	print(f"Invalid IPs Found: {','.join(invalid_ip)}. Please Enter Valid IP Adresses")
	sys.exit()	
	
else:
	ports = input("[*] Enter How Many Ports You Want To Scan: ")
	try:
		ports = int(ports)
	except ValueError:
		print("Invalid Input")
		sys.exit()
			
	if ports>int(65535):
		print("Invalid Port Number")
		sys.exit()
		
		
if len(split_targets) > 1:
    print(termcolor.colored("[*] Scanning Multiple Targets", 'green'))
    for ip_addr in split_targets:
        Scan(ip_addr.strip(), ports)
else:
    Scan(targets.strip(), ports)

