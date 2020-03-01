from cx_Freeze import setup, Executable
import sys
 
print("Von welcher Datei willst du eine Anwendung erstellen?")
datei = input("Eingabe: ")

base=None
 
setup(version = "1.0",
      description = "OPC Reader Projekt Hausen",
      name = "Reader",
      options = {"build_exe": {"packages": ["os"]}},
      executables = [Executable(datei, base=base)])
 
print("Fertig!")