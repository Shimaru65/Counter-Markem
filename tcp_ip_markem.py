import socket
import sys
import time
import datetime
import pymssql

# Variables
stacknumber = 0

while True:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('ip_address', 1912)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)

    try:
        newdate = datetime.datetime.now()
        # Send data
        #sock.sendall(b"devices|lookup|X60FLine1-4|getbatchcount\r\n")
        sock.sendall(b" some data\r\n")
        data = sock.recv(16)
        # send enter
        sock.sendall(b"\r\n")
        data2 = sock.recv(16)
        # cut /r/n
        x = data2[0:-2]
        # split to list
        y = str(x).split('|')
        # cut ' to get real number
        counter = y[2][0:-1]
        if y[0] == "b'OK" and int(counter) > 0:
            if stacknumber > 0:
                #real counter
                counter2 =  int(counter) - int(stacknumber)
                stacknumber = int(counter)
                
                # date part
                d1 = newdate.day
                m1 = newdate.month
                y1 = newdate.year
                h1 = newdate.hour
                i1 = newdate.minute
                
                # SQL QUERY
                try:
                    conn = pymssql.connect("ip address","username","password","database")
                    cur = conn.cursor()
                    cur.execute("INSERT Table (value) VALUES (type_value)",
                    (data)
                    conn.commit()
                    conn.close()
                except TypeError as e:
                    print(e)
                    conn.close()           
                
            else: 
                stacknumber = int(counter)
        else:
            print(sys.stderr, 'something went wrong "%s"' % y[0])
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()
        time.sleep(60)