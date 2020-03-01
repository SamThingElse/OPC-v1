from opcua import Server
from random import randint
import time
import os
import datetime

server = Server()

url = "opt.tcp://127.0.0.1:4840"
server.set_endpoint(url)

name = "OPCUA_SIMULATION_SERVER"
addspace = server.register_namespace(name)

node = server.get_objects_node()

Param = node.add_object(addspace, "Parameters")

Temp = Param.add_variable(addspace, "Temperature", 0)
Press = Param.add_variable(addspace, "Pressure", 0)
Time = Param.add_variable(addspace, "Time", 0)

Temp.set_writable()
Press.set_writable()
Time.set_writable()

server.start()
print("Server started at {}".format(url))

while True:

    #Temperature = (((os.popen("vcgencmd measure_temp").readlines())[0].split('='))[1].split("'"))[0]
    Temperature = randint(0, 100)
    Pressure = randint(200, 999)
    TIME = datetime.datetime.now()

    print(Temperature,Pressure,TIME)

    Temp.set_value(Temperature)
    Press.set_value(Pressure)
    Time.set_value(TIME)

    time.sleep(2)