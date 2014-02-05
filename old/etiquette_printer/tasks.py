# -*- coding: utf-8 -*-

#import subprocess
import time
import socket
import select

PRINTER_PORT = 9100

class TimeoutException(Exception): pass

# LC: using socket, rlpr sucks.
def send_to_printer(data, printer_ip, timeout=5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((printer_ip, 9100))
        output = ""
        while data and timeout > 0:
            t1 = time.time()
            rlst, wlst, elst = select.select([s,], [s,], [], timeout)
            timeout -= (time.time() - t1)
            if s in wlst and data:
                sent = s.send(data)
                data = data[sent:]
            if s in rlst:
                output += s.recv(1024)
    finally:
        try:
            s.close()
        except:
            pass

    if timeout <= 0:
        raise TimeoutException()
    
    return True

if __name__ == "__main__":
    send_to_printer(buffer("A20,20,0,5,1,1,N,\"éTEST\"\nP1\n"), "10.31.254.238")