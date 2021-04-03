import os.path
import os, sys
from opcua import Client
import time
from datetime import datetime
import csv
import xml.etree.ElementTree as ET
import mysql.connector

def settings_reader(xml_file, file_path_log):

    log_writer("0x10", file_path_log)
    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    run = True

    url = ""
    file_path = ""
    waittime = 0
    xml_path_bausteinlist = ""
    sqluser = ''
    sqlpassword = ''
    sqlhost = ''
    sqldatabase = ''
    sqltablename = ''

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

        if sqluser == '':
            if child.tag == "SqlUser":
                sqluser = child.text
                continue
        elif sqluser != '':
            pass
        else:
            log_writer("0x14", file_path_log)
            run = False

        if sqlpassword == '':
            if child.tag == "SqlPassword":
                sqlpassword = child.text
                continue
        elif sqlpassword != '':
            pass
        else:
            log_writer("0x15", file_path_log)
            run = False
        
        if sqlhost == '':
            if child.tag == "SqlHost":
                sqlhost = child.text
                continue
        elif sqlhost != '':
            pass
        else:
            log_writer("0x16", file_path_log)
            run = False

        if sqldatabase == '':
            if child.tag == "SqlDatabase":
                sqldatabase = child.text
                continue
        elif sqldatabase != '':
            pass
        else:
            log_writer("0x17", file_path_log)
            run = False

        if sqltablename == '':
            if child.tag == "SqlTableName":
                sqltablename = child.text
                continue
        elif sqltablename != '':
            pass
        else:
            log_writer("0x18", file_path_log)
            run = False

    return run, url, file_path, waittime, xml_path_bausteinlist, sqluser, sqlpassword, sqlhost, sqldatabase, sqltablename

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
    
    if check_csv_puffer(file_path):
        read_csv_puffer(file_path)
    
    if check_sql_connection(sqluser, sqlpassword, sqlhost, sqldatabase) == False:
        try:
            write_to_db(sqluser, sqlpassword, sqlhost, sqldatabase, sqltablename, crosstab)
            log_writer('0x21', file_path_log)
        except:
            write_to_csv(crosstab, file_path)
            log_writer('0x02', file_path_log)
    else:
        write_to_csv(crosstab, file_path)
        log_writer('0x02', file_path_log)
    
    print(str(Timestamp)+" [DEBUG]\tZeile in Datei geschrieben")

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
    elif DebugCode == '0x14':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': SqlUser-Tag nicht gefunden."     
    elif DebugCode == '0x15':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': SqlPassword-Tag nicht gefunden."
    elif DebugCode == '0x16':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': SqlHost-Tag nicht gefunden." 
    elif DebugCode == '0x17':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': SqlDatabase-Tag nicht gefunden."
    elif DebugCode == '0x18':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler in 'GeneralSettings.xml': SqlTableName-Tag nicht gefunden."
    elif DebugCode == '0x19':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tFehler beim Verbinden mit der MySQL-Datenbank."
    elif DebugCode == '0x20':
        WriteToLog = str(Timestamp)+"\t[ERROR]\tBeim Schreiben in die Datenbank ist ein unerwarteter Fehler aufgetreten."
    elif DebugCode == '0x21':
        WriteToLog = str(Timestamp)+"\t[INFO]\tZeile in Datenbank geschrieben."

    with open(file_path_log, 'a', newline='', encoding="utf-8") as logfile:
            logfile.write(WriteToLog + '\n')


def check_sql_connection(sqluser, sqlpassword, sqlhost, sqldatabase):
    error = False
    try:
        testing = mysql.connector.connect(user=sqluser, password=sqlpassword, host=sqlhost, database=sqldatabase)
        
        testing.close()
    except mysql.connector.Error as err:
        error =  True
        print(err)
        log_writer("0x19", file_path_log, err)
        return error
    
    return error

def write_to_db(sqluser, sqlpassword, sqlhost, sqldatabase, sqltablename, crosstab):
    error = False
    tstempel = datetime.strptime(crosstab[0], "%d.%m.%Y %H:%M:%S")
    Zeitstempel = str(tstempel.date()) + " " + str(tstempel.time())

    sql = ("INSERT INTO `{}`.`{}` (`Zeitstempel`, `Abgas`, `VW_Kessel`, `VW_SP_oben`, `VW_SP_unten`, `VW_Garage`, `VW_Brauchwasser`, `VW_Vorlauf`, `VW_Rücklauf`, `VW_Wohnung`, `VW_Verteiler`, `VW_AT`, `VW_Büro`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');").format(sqldatabase, sqltablename, Zeitstempel, crosstab[1], crosstab[2], crosstab[3], crosstab[4], crosstab[5], crosstab[6], crosstab[7], crosstab[8], crosstab[9], crosstab[10], crosstab[11], crosstab[12])

    try:
        cnx = mysql.connector.connect(user=sqluser, password=sqlpassword, host=sqlhost, database=sqldatabase)

        cursor = cnx.cursor()
        cursor.execute(sql)
        cnx.commit()

        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        error = True
        print(err)
        log_writer("0x20", file_path_log)
    return error

def check_csv_puffer(file_path):
    error = True
    if os.path.getsize(file_path) == 0:
        error = False
        return error
    else:
        pass 
    return error

def read_csv_puffer(file_path):
    sqlerror = False
    with open(file_path, "r", encoding="UTF-8") as csv:
        for row in csv:
            buffertab = []
            buffertab.append(row.split(";")[0]),
            buffertab.append(row.split(";")[1]), 
            buffertab.append(row.split(";")[2]),
            buffertab.append(row.split(";")[3]),
            buffertab.append(row.split(";")[4]),
            buffertab.append(row.split(";")[5]),
            buffertab.append(row.split(";")[6]),
            buffertab.append(row.split(";")[7]),
            buffertab.append(row.split(";")[8]),
            buffertab.append(row.split(";")[9]),
            buffertab.append(row.split(";")[10]),
            buffertab.append(row.split(";")[11]),
            buffertab.append(row.split(";")[12].split("\n")[0])

            #print(buffertab)
            if sqlerror == False:
                if check_sql_connection(sqluser, sqlpassword, sqlhost, sqldatabase) == False:
                    try:
                        write_to_db(sqluser, sqlpassword, sqlhost, sqldatabase, sqltablename, buffertab)
                        log_writer('0x21', file_path_log)
                        sqlerror = False
                        #open(file_path, 'w').close()
                    except:
                        sqlerror = True
                        pass
                else:
                    sqlerror = True
                    pass
            else:

                break
    if sqlerror == False:        
        open(file_path, 'w').close()
    else:
        pass

#url = settings_reader(xml_path_generalsettings)[1]
#url = "opc.tcp://127.0.0.1:4840"

# Baustein_Liste = ["Abgas", "VW_Kessel", "VW_SP_oben", "VW_SP_unten", "VW_Garage", "VW_Brauchwasser", "VW_Vorlauf", "VW_Rücklauf", "VW_Wohnung", "VW_Verteiler", "VW_AT", "VW_Büro"]

# Baustein_Liste = ["2"]
# file_path = os.path.join(os.path.dirname(__file__), 'csv', 'export_Abgas.csv')
file_path_log = os.path.join(os.path.dirname(__file__), 'log', 'latestlog.log')
xml_path_generalsettings = os.path.join(os.path.dirname(__file__), 'settings', 'GeneralSettings.xml')

# Initiiere GeneralSettings.xml

test_path = '/root/workspace/OPC/csv/test.csv'

run, url, file_path, waittime, xml_path_bausteinlist, sqluser, sqlpassword, sqlhost, sqldatabase, sqltablename = settings_reader(xml_path_generalsettings, file_path_log)
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

### Das Schreiben des CSV-Headers ist Veraltet. Es werden nur noch Werte in die CSV-Datei geschrieben als Puffer für eine fehlende MySQL-Verbindung.
#    if os.path.isfile(file_path) == True:
#        # file exist
#        pass
#    else:
#        write_header(baustein_dict)

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
