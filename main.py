import sys
from modbus_tk import modbus_tcp
import telnetlib
import time
import config
import mysql.connector

def main():
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        print('Usage: python3 main.py HOST PORT ')
        return

    try:
        telnetlib.Telnet(host, int(port), 10)
        print("Succeeded to telnet {}:{} ".format(host, port))
    except Exception as e:
        print("Failed to telnet {}:{} : {}  ".format(host, port, str(e)))
        return

    """
    Functions to convert between Python values and C structs.
    Python bytes objects are used to hold the data representing the C struct
    and also as format strings (explained below) to describe the layout of data
    in the C struct.

    The optional first format char indicates byte order, size and alignment:
      @: native order, size & alignment (default)
      =: native order, std. size & alignment
      <: little-endian, std. size & alignment
      >: big-endian, std. size & alignment
      !: same as >

    The remaining chars indicate types of args and must match exactly;
    these can be preceded by a decimal repeat count:
      x: pad byte (no data); c:char; b:signed byte; B:unsigned byte;
      ?: _Bool (requires C99; if not available, char is used instead)
      h:short; H:unsigned short; i:int; I:unsigned int;
      l:long; L:unsigned long; f:float; d:double.
    Special cases (preceding decimal count indicates length):
      s:string (array of char); p: pascal string (with count byte).
    Special cases (only available in native format):
      n:ssize_t; N:size_t;
      P:an integer type that is wide enough to hold a pointer.
    Special case (not in native mode unless 'long long' in platform C):
      q:long long; Q:unsigned long long
    Whitespace between formats is ignored.

    The variable struct.error is an exception raised on errors.
    """
    try:
        master = modbus_tcp.TcpMaster(host=host, port=int(port), timeout_in_sec=5.0)
        master.set_timeout(5.0)
        print("Connected to {}:{} ".format(host, port))
        cnx = mysql.connector.connect(**config.modbus_tcp_db)
        cursor = cnx.cursor()
        while True:
            print("read registers...")
            # point_id : 0
            r0 = master.execute(slave=1, function_code=3, starting_address=0, quantity_of_x=2, data_format='>l')
            t0 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            v0 = r0[0]
            print("r0 = " + str(v0) + ",时间为：" + str(t0))
            # point_id : 1
            r1 = master.execute(slave=1, function_code=3, starting_address=2, quantity_of_x=2, data_format='>l')
            t1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            v1 = r1[0]
            print("r1 = " + str(v1) + ",时间为：" + str(t0))
            # point_id : 2
            r2 = master.execute(slave=1, function_code=3, starting_address=4, quantity_of_x=2, data_format='>l')
            t2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            v2 = r2[0]
            print("r2 = " + str(v2) + ",时间为：" + str(t0))
            # point_id : 3
            r3 = master.execute(slave=1, function_code=3, starting_address=6, quantity_of_x=2, data_format='>l')
            t3 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            v3 = r3[0]
            print("r3 = " + str(v3) + ",时间为：" + str(t0))
            # point_id : 4
            r4 = master.execute(slave=1, function_code=3, starting_address=8, quantity_of_x=2, data_format='>l')
            t4 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            v4 = r4[0]
            print("r4 = " + str(v4) + ",时间为：" + str(t0))

            # todo: save point_id, datetime and value to database
            insert = ('INSERT INTO point '
                      '(point_id,datetime,value) '
                      'VALUES(%s,%s,%s)')
            insert_data = [(0, t0, v0), (1, t1, v1), (2, t2, v2), (3, t3, v3), (4, t4, v4)]
            cursor.executemany(insert, insert_data)
            cnx.commit()

            time.sleep(config.interval_in_seconds)
    except Exception as e:
        print(str(e))
    finally:
        master.close()
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


if __name__ == "__main__":
    main()
