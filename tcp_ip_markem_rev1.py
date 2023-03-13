import socket
import sys
import time
import datetime
import pymssql

# Variables
stacknumber = 0

def dbconnect():
    # Set database connection parameters
    server = '192.168.16.30'
    user = 'sa'
    password = 'Eur@Admin'
    database = 'Markem'

    # Connect to the database
    conn = pymssql.connect(server=server, user=user, password=password, database=database)

    # Return the connection object
    return conn
    

while True:
    # name machine , ip , port, name table , machine code
    thislist = ["tcp_ip_gummy_5B_02", "192.168.17.250", 1912 , "tb_Gummy5B_02" , "X40Gummy5B-02"]
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the timeout for the connection attempt
    sock.settimeout(1)
    # Set server to connect with
    server_address = (thislist[1], thislist[2])
    #print status
    print(thislist[0] + ': checking if server is ready to connect...')
    #check if it can connect or not 
    result = sock.connect_ex(server_address)
    #0 = yes, you server is ready to connect
    if result == 0:
        print(thislist[0] + ': server is ready to connect, connecting to %s port %s' % server_address)
        
        try:
            #get new date
            newdate = datetime.datetime.now()
            # Create string of code 
            textsend = "devices|lookup|" + thislist[4] + "|getbatchcount\r\n"
            #Convert it to bytes type 
            res = bytes(textsend, 'utf-8')
            #Send it to target machine
            sock.sendall(res)
            #Receive data back
            data = sock.recv(16)
            #Send enter
            sock.sendall(b"\r\n")
            #Receive data back again?
            data2 = sock.recv(16)
            #Cut /r/n
            x = data2[0:-2]
            #Split data to list
            y = str(x).split('|')
            #Cut ' to get real number
            counter = y[2][0:-1]
            #check if this data is OK or not 
            if y[0] == "b'OK" and int(counter) > 0:
                #Check if stacknumber is greater than zero
                if stacknumber > 0:
                    #Real counter
                    counter2 =  int(counter) - int(stacknumber)
                    #Check counter negative value. some data gave negative values set it to original number of counter
                    if int(counter2) < 0:
                        counter2 = int(counter)
                    #Set stacknumber to present counter
                    stacknumber = int(counter)
                    # date part
                    d1 = newdate.day
                    m1 = newdate.month
                    y1 = newdate.year
                    h1 = newdate.hour
                    i1 = newdate.minute
                    #SQL QUERY TO MACHINE TABLE
                    try:
                        conn = dbconnect()
                        cur = conn.cursor()
                        cur.execute("INSERT " + thislist[3] + " (h1,i1,d1,m1,y1,counter) VALUES (%d, %d, %d, %d, %d, %d)",
                        (h1,i1,d1,m1,y1,int(counter2)))
                        conn.commit()
                        conn.close()
                        print(thislist[0] + ' : sql commit success : "%s"' % newdate)
                    except TypeError as e:
                        print(e)
                        conn.close()           

                else: 
                    #If stacknumber less than zero then set it to present counter
                    stacknumber = int(counter)
            else:
                #SQL QUERY ERROR LOG
                try:
                    conn = dbconnect()
                    cur = conn.cursor()
                    cur.execute("INSERT Log_error (machine,reason) VALUES (%d, %d)",
                    (thislist[0],"something went wrong : " + y[0] + " counter : " + int(counter)))
                    conn.commit()
                    conn.close()
                    print(thislist[0] + ': something went wrong "%s"' % y[0])
                except TypeError as e:
                    print(e)
                    conn.close()       

        finally:
            sock.close()
            time.sleep(60)
    else:
        #SQL QUERY ERROR LOG
        try:
            conn = dbconnect()
            cur = conn.cursor()
            cur.execute("INSERT Log_error (machine,reason) VALUES (%d, %d)",
            (thislist[0],"machine is not ready to connect"))
            conn.commit()
            conn.close()
            print(thislist[0] + ': server ' + thislist[1] + '  is not ready to connect')
        except TypeError as e:
            print(e)
            conn.close()    
        time.sleep(60)