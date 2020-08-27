#! python3
# scheduler.py
#
# Motivation:
# Where I work the SAP Change Request Management is strict and the requests are manually inserted in the Production System import queue.
# As some requests are approved to be moved to production only in a future date, I need a tool to improve control over this.
#
# What this script does:
# This script has two main functions: maintains a control file with requests numbers and dates;
# parses the control file and insert in the import queue the requests which have the current date.
#
# How to use:
# py agendador.py [action]
# 
# [action]    --process   Processes the control file and inserts the requests in the import queue.
#             --insert    Starts a dialog to add new requests to the control file.
# 
# Running the script without specifying an action will bring you a menu asking what to do.

import os
import shutil
import datetime
import sys

# Constants
controlFile = 'requestscontrol.txt' # Name of the control file
dirTrans = 'D:\\usr\\sap\\trans' # SAP trans directory
sidSAP = 'NEP' # SAP SID
clientSAP = '300' # SAP client
transProfile = 'TP_DOMAIN_NED.PFL' # SAP transport profile
dateFormat = '%d/%m/%Y' # Date format

def addtocontrol(reqNum,reqDate):
    # Extract cofile name from request number.
    fName = reqNum[3:10]+'.'+reqNum[0:3]
    fPath = os.path.join(dirTrans,'cofiles',fName)
    # Exit if cofile does not exist.
    if not os.path.exists(fPath):
        return 'COFILE_ERROR'
    # Read the control file.
    rFile = open(controlFile,'r')
    rContent = rFile.readlines()
    rFile.close()
    rLine = ''
    # Check whether the request is already in the control file.
    for i in range(len(rContent)):
        rLine = rContent[i]
        if reqNum == rLine[0:10]:
            return 'REQ_DUPLICATED'
    # Add request and date to the control file.
    rFile = open(controlFile,'a')
    rFile.write(reqNum+' '+reqDate+'\n')
    rFile.close()
    return True

def addtoqueue():
    # Read the control file.
    rFile = open(controlFile,'r')
    rContent = rFile.readlines()
    rFile.close()
    rNum = ''
    tList = []
    newContent = []
    # Add requests to be inserted in the queue to a list.
    for i in range(len(rContent)):
        rLine = rContent[i]
        if dToday == rLine[11:21]:
            rNum = rLine[0:10]
            tList = tList + [rNum]
        else:
            # Add requests with future dates in a list.
            newContent = newContent + [rLine]
    # If there are requests to be inserted in the queue: create a backup of the control file; write new control
    # with only the requests with future dates.
    if len(tList) > 0:
        shutil.copy(controlFile,controlFile+'.bak')        
        rFile = open(controlFile,'w')
        rFile.writelines(newContent)
        rFile.close()
    tStamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    cont = 0
    print('Running tp to insert the requests in the queue...')
    for n in range(len(tList)):
        print('Addind request '+tList[n])
        # Call tp to insert the requests in the queue. Output is saved in a logfile.
        profilePath = os.path.join(dirTrans,'bin',transProfile)
        tCommand = 'tp ADDTOBUFFER '+tList[n]+' '+sidSAP+' client='+clientSAP+' pf='+profilePath 
        os.system(tCommand+' >> '+tStamp+'.log')
        cont += 1
    print('Finished.')    
    print('There were '+str(len(tList))+' requests for today in control file.')
    print(str(cont)+' requests were inserted in the import queue.')

def validate(dText):
    # Check whether the entered date is in a valid format and that it is not in the past.
    try:
        if dText == datetime.datetime.strptime(dText, dateFormat).strftime(dateFormat):
            if datetime.datetime.strptime(dText, dateFormat).date() > datetime.datetime.strptime(dToday, dateFormat).date():
                return True
    except ValueError:
        return False

def manualinsert():
    rDate =''
    while not validate(rDate):
        print('Date to insert in the queue:')
        rDate = input()
    rList = []
    while True:
        print('Request number ("nothing" to end):')
        rNum = input()
        if rNum =='':
            break
        rList = rList + [rNum]

    print('Adding requests to the control file...')
    errors = 0
    result = ''
    for i in range(len(rList)):
        result = addtocontrol(rList[i],rDate)
        if result == True:
            print('Request '+rList[i]+' added to control file.')
        else:
            if result == 'REQ_DUPLICATED':
                print('ERROR, request '+rList[i]+' already in control file.')
            if result == 'COFILE_ERROR':
                print('ERROR in COFILE. Is the request released? Request '+rList[i]+' not added to control file.')
            errors += 1
    print('Finished with '+str(errors)+' errors.')

# Main routine
dToday = datetime.date.today().strftime(dateFormat)
if len(sys.argv) == 1: # Run if no argument was passed from command line
    print('******************************************************************')
    print('*** SCHEDULER TO INSERT TRANSPORT REQUESTS IN THE IMPORT QUEUE ***')
    print('*** SAP System ID: '+sidSAP+'      Client: '+clientSAP+'                        ***')
    print('******************************************************************')
    print('1 - Add new requests to the control file')
    print('2 - Process the control file and insert the requests in the import queue')
    print('q - Quit')
    cmd = input()
    if cmd == '1':
        manualinsert()
    if cmd == '2':
        addtoqueue()
    os.system('pause')
else:
    if str(sys.argv[1]) == '--insert': # Check if argument --insert was passed from command line
        manualinsert()
    if str(sys.argv[1]) == '--process': # Check if argument --process was passed from command line
        addtoqueue()
