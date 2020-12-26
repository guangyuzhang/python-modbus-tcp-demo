import sys
from datetime import datetime

from modbus_tk import modbus_tcp
import telnetlib
import time
import config
import mysql.connector
def main():

    connector = None
    cursor = None

    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        print('Usage: python3 main.py HOST PORT ')
        return

    try:
        telnetlib.Telnet(host, int(port), 10)
        print("Succeeded to telnet %s:%s ", host, port)
    except Exception as e:
        print("Failed to telnet %s:%s : %s  ", host, port, str(e))
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
        connector = mysql.connector.connect(**config.modbus_tcp_db)
        cursor = connector.cursor()
        master = modbus_tcp.TcpMaster(host=host, port=int(port), timeout_in_sec=5.0)
        master.set_timeout(5.0)
        print("Connected to %s:%s ", host, port)
        while True:
            print("read registers...")
            # point_id : 0
            r0 = master.execute(slave=1, function_code=3, starting_address=0, quantity_of_x=2, data_format='>l')
            print("r0 = " + str(r0))
            # point_id : 1
            r1 = master.execute(slave=1, function_code=3, starting_address=2, quantity_of_x=2, data_format='>l')
            print("r1 = " + str(r1))
            # point_id : 2
            r2 = master.execute(slave=1, function_code=3, starting_address=4, quantity_of_x=2, data_format='>l')
            print("r2 = " + str(r2))
            # point_id : 3
            r3 = master.execute(slave=1, function_code=3, starting_address=6, quantity_of_x=2, data_format='>l')
            print("r3 = " + str(r3))
            # point_id : 4
            r4 = master.execute(slave=1, function_code=3, starting_address=8, quantity_of_x=2, data_format='>l')
            print("r4 = " + str(r4))
            list = [r0, r1, r2, r3, r4]
            # todo: save point_id, datetime and value to database
            for point_id in range(0, 5):
                sql = "insert into modbus (point_id,value,datetime) values (%s,%s,%s)"
                val = (point_id, list[point_id][0], datetime.today())
                cursor.execute(sql, val)
            connector.commit()
            time.sleep(config.interval_in_seconds)
    except Exception as e:
        print(str(e))
    finally:
        master.close()
        cursor.close()
        connector.close()




if __name__ == "__main__":
    main()
