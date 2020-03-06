import os.path
import os, sys
from opcua import Client
import time
from datetime import datetime
import csv

def open_connection(url):
    Timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    client = Client(url)
    client.connect()
    print(str(Timestamp)+" [INFO]\tClient Connected")
    log_writer('0x05', file_path_log)
    return client

def write_to_csv(data, file_path):
        with open(file_path, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data)
            # print("INFO: File created.") # just for debug

# Baustein = "VW_AT"
# Baustein = input("Bitte Bausteinname eingeben: ")

def OPC_reader(bausteinliste):
    # now = datetime.now()
    Timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    crosstab = []

    crosstab.append(Timestamp)

    client = open_connection(url)

    for element in bausteinliste:
        Temp = client.get_node("ns=3;s="+element)
        #Temp = client.get_node("ns=2;i="+element)
        Temperature = Temp.get_value()
        Temperature = int(Temperature) / 10

        crosstab.append(Temperature)
    
    write_to_csv(crosstab, file_path)

    print(str(Timestamp)+" [DEBUG]\tZeile in Datei geschrieben")

    log_writer('0x02', file_path_log)
    # print(crosstab)

    client.close_session()
    print(str(Timestamp)+" [INFO]\tVerbindung getrennt")

    log_writer('0x03', file_path_log)

def write_header(liste):
    Timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    header = ["Zeitstempel"]
    for element in liste:
        header.append(element)
    write_to_csv(header, file_path)
    print(str(Timestamp)+" [DEBUG]\tHeader in CSV geschrieben")
    log_writer('0x04', file_path_log)

def log_writer(DebugCode, file_path_log):
    Timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if DebugCode == '0x01':
        WriteToLog = str(Timestamp)+" [ERROR]\tFehler bei der Ausführung. Eventuell besteht keine Verbindung zum Ziel."
    elif DebugCode == '0x02':
        WriteToLog = str(Timestamp)+" [INFO]\tZeile in Datei geschrieben"
    elif DebugCode == '0x03':
        WriteToLog = str(Timestamp)+" [INFO]\tVerbindung getrennt"
    elif DebugCode == '0x04':
        WriteToLog = str(Timestamp)+" [DEBUG]\tHeader in CSV geschrieben"
    elif DebugCode == '0x05':
        WriteToLog = str(Timestamp)+" [INFO]\tClient Connected"

    with open(file_path_log, 'a', newline='', encoding="utf-8") as logfile:
            logfile.write(WriteToLog + '\n')


url = "opc.tcp://192.168.153.31:4870"
#url = "opc.tcp://127.0.0.1:4840"

Baustein_Liste = ["Abgas", "VW_Kessel", "VW_SP_oben", "VW_SP_unten", "VW_Garage", "VW_Brauchwasser", "VW_Vorlauf", "VW_Rücklauf", "VW_Wohnung", "VW_Verteiler", "VW_AT", "VW_Büro"]

# Baustein_Liste = ["2"]
file_path = os.path.join(os.path.dirname(__file__), 'csv', 'export_Abgas.csv')
file_path_log = os.path.join(os.path.dirname(__file__), 'log', 'latestlog.log')

## Runtime
while True:
    
    i = 10
    # clear = lambda: os.system('cls') #on Windows System
    try:
        s = sys.winver
        os.system("cls")
    except:
        os.system("clear")

    #clear()

    if os.path.isfile(file_path) == True:
        # file exist
        pass
    else:
        write_header(Baustein_Liste)

    try:
        OPC_reader(Baustein_Liste)
    except:
        print("Fehler bei der Ausführung. Eventuell besteht keine Verbindung zum Ziel. Es wird in " + str(i) + " Sekunden erneut versucht.")

        log_writer('0x01', file_path_log)

        #time.sleep(5)
        pass
    

    print("\n")
    #time.sleep(5)

    for element in range(0,10):
        if i == 1:
            print("Warte "+str(i)+" Sekunde...")
        else: 
            print("Warte "+str(i)+" Sekunden...")
        i=i-1
        time.sleep(1)

## Runtime Ende