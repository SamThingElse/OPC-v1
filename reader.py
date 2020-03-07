import os.path
import os, sys
from opcua import Client
import time
from datetime import datetime
import csv
import xml.etree.ElementTree as ET

def settings_reader(xml_file, file_path_log):

    log_writer("0x10", file_path_log)
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    run = True

    url = ""
    file_path = ""
    waittime = 0
    xml_path_bausteinlist = ""

    for child in root:
        # print(child.tag, child.text) # Debug
        if url == '':
            if child.tag == "url":
                url = child.text
                continue
        elif url != '':
                pass
        else:
            log_writer("0x06", file_path_log)
            run = False

        if file_path == '':
            if child.tag == "DateipfadCSV":
                file_path = child.text
                continue
        elif file_path != '':
            pass
        else:
            log_writer("0x07", file_path_log)
            run = False

        if waittime == 0:    
            if child.tag == "WaitTime":
                waittime = child.text
                continue
        elif waittime != 0:
            pass
        else:
            log_writer("0x08", file_path_log)
            run = False

        if xml_path_bausteinlist == "":    
            if child.tag == "DateipfadBausteinliste":
                xml_path_bausteinlist = child.text
                continue
        elif xml_path_bausteinlist != "":
            pass
        else:
            log_writer("0x11", file_path_log)
            run = False    

    return run, url, file_path, waittime, xml_path_bausteinlist

def bausteinlist_reader(xml_file, file_path_log):

    log_writer("0x12", file_path_log)
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    run = True

    id = 0
    name = ""
    node = ""

    baustein_dict = {}

    for child in root:
        for element in child:
            if element.tag == "id":
                id = element.text
            elif element.tag == "Name":
                name = element.text
            elif element.tag == "Node":
                node = element.text
            else:
                pass
            
        baustein_dict.update( {name : node} )

    log_writer("0x13", file_path_log, id)

#    for element in baustein_dict:
#        print(element)

#    for element in baustein_dict:
#        print(baustein_dict[element])

    return run, baustein_dict

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

def OPC_reader(baustein_dict):
    # now = datetime.now()
    Timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    crosstab = []

    crosstab.append(Timestamp)
    client = open_connection(url)


    for element in baustein_dict:
        # print(baustein_dict[element]) # debug
        # print(element) # debug
        # print(baustein_dict[element]+element) # debug

        Temp = client.get_node(baustein_dict[element]+element)
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

def log_writer(DebugCode, file_path_log, n=0):
    Timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if DebugCode == '0x01':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler bei der Ausführung. Eventuell besteht keine Verbindung zum Ziel."
    elif DebugCode == '0x02':
        WriteToLog = str(Timestamp)+"\t[INFO]\tZeile in Datei geschrieben."
    elif DebugCode == '0x03':
        WriteToLog = str(Timestamp)+"\t[INFO]\tVerbindung getrennt."
    elif DebugCode == '0x04':
        WriteToLog = str(Timestamp)+"\t[INFO]\tHeader in CSV geschrieben."
    elif DebugCode == '0x05':
        WriteToLog = str(Timestamp)+"\t[INFO]\tClient Connected."
    elif DebugCode == '0x06':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': URL-Tag nicht gefunden."
    elif DebugCode == '0x07':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': dateipfadcsv-Tag nicht gefunden."
    elif DebugCode == '0x08':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': Waittime-Tag nicht gefunden."
    elif DebugCode == '0x09':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tProgramm wurde aufgrund eines Fehlers abgebrochen."
    elif DebugCode == '0x10':
        WriteToLog = str(Timestamp)+"\t[INFO]\t'GeneralSettings.xml' wird gelesen."
    elif DebugCode == '0x11':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': Bausteinpfad-Tag nicht gefunden."
    elif DebugCode == '0x12':
        WriteToLog = str(Timestamp)+"\t[INFO]\t'BausteinListe.xml' wird gelesen."
    elif DebugCode == '0x13':
        WriteToLog = str(Timestamp)+"\t[INFO]\tEs wurden {0} Bausteine gelesen.".format(n)        

    with open(file_path_log, 'a', newline='', encoding="utf-8") as logfile:
            logfile.write(WriteToLog + '\n')


#url = settings_reader(xml_path_generalsettings)[1]
#url = "opc.tcp://127.0.0.1:4840"

# Baustein_Liste = ["Abgas", "VW_Kessel", "VW_SP_oben", "VW_SP_unten", "VW_Garage", "VW_Brauchwasser", "VW_Vorlauf", "VW_Rücklauf", "VW_Wohnung", "VW_Verteiler", "VW_AT", "VW_Büro"]

# Baustein_Liste = ["2"]
# file_path = os.path.join(os.path.dirname(__file__), 'csv', 'export_Abgas.csv')
file_path_log = os.path.join(os.path.dirname(__file__), 'log', 'latestlog.log')
xml_path_generalsettings = os.path.join(os.path.dirname(__file__), 'settings', 'GeneralSettings.xml')

# Initiiere GeneralSettings.xml

run, url, file_path, waittime, xml_path_bausteinlist = settings_reader(xml_path_generalsettings, file_path_log)
# file_path = os.path.join(os.path.dirname(__file__), 'csv', filename)

run, baustein_dict = bausteinlist_reader(xml_path_bausteinlist, file_path_log)

## Runtime
while run == True:
    
    wait = waittime
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
        write_header(baustein_dict)

    try:
        OPC_reader(baustein_dict)
    except:
        print("Fehler bei der Ausführung. Eventuell besteht keine Verbindung zum Ziel. Es wird in " + str(waittime) + " Sekunden erneut versucht.")

        log_writer('0x01', file_path_log)

        #time.sleep(5)
        pass
    

    print("\n")
    #time.sleep(5)

    for element in range(0,int(wait)):
        if wait == 1:
            print("Warte "+str(wait)+" Sekunde...")
        else: 
            print("Warte "+str(wait)+" Sekunden...")
        wait = int(wait) - 1
        time.sleep(1)

## Runtime Ende

if run == False:
    print("Programm wurde aufgrund eines Fehlers abgebrochen. Siehe Log-Datei für mehr Details.")
    log_writer("0x09", file_path_log)