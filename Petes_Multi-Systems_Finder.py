#==================================================================================================================================== 
#=============================================Created by CMDR Longman.P.J============================================================
#====================================================================================================================================
import math
import os
import os.path
import sys
import shutil
from time import gmtime, strftime, sleep
from itertools import cycle
import time
import gzip
import json
import requests
import zipfile
import dateutil.parser
import datetime 
#If you get errors on the above imports, run the following from an elevated command prompt: 
# py -m pip install requests

'''
The Unix epoch (or Unix time or POSIX time or Unix timestamp)
is the number of seconds that have elapsed since January 1, 1970
(midnight UTC/GMT), not counting leap seconds.
These values in seconds are held in these variables:
filetime
last_modified
'''
gzip_url_EDSM = "https://edgalaxydata.space/EDSM/dumps/systemsPopulated.json.gz"
gzip_url_Spansh = "https://downloads.spansh.co.uk/galaxy_populated.json.gz"

SysDataFilezip = "systemsPopulated.json.gz"
SysDataFile = "systemsPopulated.json"

def MultiSys():
    #Checks to see if saved file is older than last dump    
    DumpSource = input("Press 1 for EDSM or Enter for Spansh\n")
    if DumpSource == '1':
        gzip_url=(gzip_url_EDSM)
    else :
        gzip_url=(gzip_url_Spansh)
    print(gzip_url)
    cont = input("Press any key to continue") # delete/comment out after test
    response = requests.head(gzip_url)
    last_modified = response.headers.get('Last-Modified') #last dump date/time
    from datetime import datetime
    if last_modified:
        gzip_last_modified = dateutil.parser.parse(last_modified)
        t = datetime.strptime(str(gzip_last_modified)[:19], '%Y-%m-%d %H:%M:%S')
        last_modified = t.timestamp()
        #print(last_modified)
        #cont = input("Press any key to continue") # delete/comment out after test
    check_file = os.path.isfile(SysDataFile)    
    if check_file == True :
        filetime = os.path.getmtime(SysDataFile) # date/time of downloaded file
        tdif = filetime-last_modified
        if tdif <0:
            os.remove(SysDataFile)    
    if check_file == False or tdif <0: 
        #print(tdif)
        #cont = input("Press any key to continue") # delete/comment out after test
        GetFile(gzip_url)    
    clear = lambda: os.system('cls')
    
    #quit_program = input("Press q to quit or Enter to search again - ")
    print('Loading JSON file.')
    file=open(SysDataFile,'r')    
    json_data = open(SysDataFile, "r")
    jsdatar = json_data.read()
    SysData = json.loads(jsdatar)
    print('JSON file loaded.')
    print()
    while True:
        
        print("Multi-System Finder - By: CMDR Longman.P.J")
        print()            
        print("1: Max Federation Factions Systems")
        print("2: Max Empire Factions Systems")
        print("3: Max Anarchy Factions Systems")
        print("4: Max Factions Systems")        
        print()
        iFact = input("Enter the number for your selected search or q to quit:\n")
        if iFact == "q":
            break
        answer = []
        for system in SysData:
            countFaction = 0
            countSearchFactions = 0
            countStations = 0
            sysname = system["name"]
            if "factions" in system: #Ensure key exists in dictionary
                for faction in system["factions"]:
                    if "government" in faction: #Ensure key exists in dictionary
                        if faction["influence"] > 0:
                            countFaction += 1
                            if iFact == "1":
                                if faction["allegiance"] == "Federation"and faction["influence"] > 0:
                                    countSearchFactions += 1                                
                            elif iFact == "2":
                                if faction["allegiance"] == "Empire"and faction["influence"] > 0:
                                    countSearchFactions += 1
                            elif iFact == "3":
                                if faction["government"] == "Anarchy"and faction["influence"] > 0:
                                    countSearchFactions += 1
                            elif iFact == "4":
                                if faction["influence"] > 0:
                                    countSearchFactions += 1
            if iFact == '1' or  iFact == '2':
                if "stations" in system: #Ensure key exists in dictionary
                    if countSearchFactions > 4:
                        for station in system["stations"]:
                            if station["type"] == "Coriolis Starport" or station["type"] == "Orbis Starport":
                                countStations += 1                      
                        if countStations > 0:
                            answer.append([sysname, countSearchFactions, countStations])
            elif iFact == "3":
                if countSearchFactions > 2:
                    if "stations" in system: #Ensure key exists in dictionary
                        for station in system["stations"]:
                            countStations += 1
                    if (countFaction == countSearchFactions or countSearchFactions >4) and countStations > 0:
                        answer.append([sysname, countSearchFactions, countStations])
            elif iFact == "4":
                if countSearchFactions > 7: 
                    if "stations" in system: #Ensure key exists in dictionary                    
                        for station in system["stations"]:
                            countStations += 1
                        if countStations > 0:                    
                            answer.append([sysname, countSearchFactions, countStations])
            if countSearchFactions > 9:
                print()
                print()
                strFacts = "{:<40} {:<10} {:<19}".format("Faction", "Influence", "Updated")
                print (strFacts)
                for faction in system["factions"]:
                    epoch_time = faction["lastUpdate"]
                    strUpdate = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch_time)) 
                    strFacts = "{:<40} {:<10} {:<19}".format(faction["name"], faction["influence"], strUpdate)
                    print (strFacts)
                print()
                print()
                    
        if iFact == '1':
            print ("Federation Faction Systems")
            iSort = 1
        elif iFact == '2':
            print ("Empire Faction Systems")
            iSort = 1
        elif iFact == '3':
            print ("Anarchy Faction Systems")
            iSort = 2
        elif iFact == "4":
            print ("Max Faction Systems")
            iSort = 1
        # sortOrder reverse = False is ascending, reverse = True is descending
        answer.sort(key=lambda i: i[iSort], reverse = True)

        answerString = "{:<30} {:3} {:3}\n".format("System","Fac", "Stn")
        for ans in answer:
            answerString += "{:<30} {:3} {:3}\n".format(ans[0], int(ans[1]), int(ans[2]))
        print (answerString)
            
        quit_program = input("Press q to quit or Enter to search again - ")
        if quit_program != 'q':
            clear()
            continue
        else:
            break        

def GetFile(gzipUrl):
    statusBar = input("Press y to view the download status.\n")
    if statusBar == 'y':        
        from tqdm import tqdm
        print('Downloading latest zip file.') 
        # URL of the file to be downloaded is defined as gzip_url
        # send a HTTP request to the server and save the HTTP response in a response object called response
        response  = requests.get(gzipUrl, stream=True, allow_redirects=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(SysDataFilezip, 'wb') as file, tqdm(
            desc=SysDataFilezip,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
    else:
        print('Downloading latest zip file.') 
        # URL of the file to be downloaded is defined as gzip_url
        res  = requests.get(gzipUrl) # create HTTP response object
        # send a HTTP request to the server and save the HTTP response in a response object called r
        with open(SysDataFilezip,'wb') as f:
            # Saving received content as a file in binary format  
            # write the contents of the response (r.content) to a new file in binary mode.
            f.write(res.content)        
 
    print('Zip file downloaded.')
    print('Extracting zip file.')

    #path_to_file_to_be_extracted

    ip = SysDataFilezip

    #output file to be filled

    op = open(SysDataFile,"w") 

    with gzip.open(ip,"rb") as ip_byte:
        op.write(ip_byte.read().decode("utf-8"))
        ip_byte.close()
    print('Saving extracted zip file as JSON file.')
    dir_path = os.path.dirname(os.path.realpath(SysDataFilezip))
    zippath = dir_path + '\\' + SysDataFilezip
    os.remove(zippath) #delete zipped file
    print('Zip file deleted.')

if __name__ == "__main__":
    MultiSys()
