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

def _stream_json_array(file_obj, chunk_size=1024 * 1024, progress_cb=None):
    decoder = json.JSONDecoder()
    buffer = ""
    in_array = False
    eof = False
    total_read = 0
    need_more = True
    while True:
        if not eof and (need_more or len(buffer) < chunk_size):
            data = file_obj.read(chunk_size)
            if data == "":
                eof = True
            else:
                buffer += data
                total_read += len(data)
                if progress_cb:
                    progress_cb(total_read)
            need_more = False
        if not in_array:
            idx = buffer.find("[")
            if idx == -1:
                if eof:
                    return
                continue
            buffer = buffer[idx + 1:]
            in_array = True
        buffer = buffer.lstrip()
        if buffer.startswith("]"):
            return
        if buffer.startswith(","):
            buffer = buffer[1:]
            continue
        try:
            obj, idx = decoder.raw_decode(buffer)
        except json.JSONDecodeError:
            if eof:
                raise
            need_more = True
            continue
        yield obj
        buffer = buffer[idx:]

def _iter_systems(path):
    # Use utf-8-sig to tolerate BOMs if present
    file_size = os.path.getsize(path)
    last_pct = -1
    last_ts = time.time()
    def progress(bytes_read):
        nonlocal last_pct, last_ts
        if file_size <= 0:
            return
        pct = int(bytes_read * 100 / file_size)
        now = time.time()
        if pct != last_pct and (pct == 100 or now - last_ts >= 0.5):
            print("\rLoading JSON: {:3d}%".format(pct), end="", flush=True)
            last_pct = pct
            last_ts = now
    with open(path, "r", encoding="utf-8-sig") as f:
        for obj in _stream_json_array(f, progress_cb=progress):
            yield obj
    if file_size > 0:
        print("\rLoading JSON: 100%")
        print()

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
        print('Streaming JSON file.')
        answer = []
        system_iter = _iter_systems(SysDataFile)
        use_tqdm = False
        try:
            from tqdm import tqdm
            system_iter = tqdm(system_iter, desc="Processing systems", unit="sys", mininterval=0.5)
            use_tqdm = True
        except ImportError:
            processed = 0
            last_ts = time.time()
            def _progress_iter(it):
                nonlocal processed, last_ts
                for item in it:
                    processed += 1
                    now = time.time()
                    if now - last_ts >= 1.0:
                        print("\rProcessing systems: {}".format(processed), end="", flush=True)
                        last_ts = now
                    yield item
                print("\rProcessing systems: {} (done)".format(processed))
                print()
            system_iter = _progress_iter(system_iter)
        for system in system_iter:
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
        if use_tqdm:
            system_iter.close()
                    
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
    downloaded = False
    use_existing = False
    if os.path.isfile(SysDataFilezip):
        use_existing_zip = input("Existing zip file found. Press y to use it and skip download, or Enter to download latest.\n")
        if use_existing_zip.lower() == 'y':
            use_existing = True

    if use_existing:
        print('Using existing zip file. Skipping download.')
    else:
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
        downloaded = True
        print('Zip file downloaded.')
    print('Extracting zip file.')

    #path_to_file_to_be_extracted

    ip = SysDataFilezip

    #output file to be filled

    # Stream-decompress to avoid loading the whole file into memory
    with gzip.open(ip, "rb") as ip_byte, open(SysDataFile, "wb") as op:
        shutil.copyfileobj(ip_byte, op, length=1024 * 1024)
    print('Saving extracted zip file as JSON file.')
    dir_path = os.path.dirname(os.path.realpath(SysDataFilezip))
    zippath = os.path.join(dir_path, SysDataFilezip)
    if downloaded:
        os.remove(zippath) #delete zipped file
        print('Zip file deleted.')
    else:
        print('Existing zip file kept.')

if __name__ == "__main__":
    MultiSys()
