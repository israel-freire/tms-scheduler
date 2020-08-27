# tms-scheduler
> Python script that adds SAP transport requests to import queue according to date.

## Motivation:
Where I work the SAP Change Request Management is strict and the requests are manually inserted in the Production System import queue. As some requests are approved to be moved to production only in a future date, I need a tool to improve control over this.

## What this script does:
This script has two main functions:
    maintains a control file with requests numbers and dates;
    parses the control file and insert in the import queue the requests which have the current date.

## How to use:
Scheduling this script to run everyday it will check whether there are any request with the current date in the control file and will add it to the import queue of the SAP system.

## Syntax:
```sh
py agendador.py [action]

[action]

--process   Processes the control file and inserts the requests in the import queue.

--insert    Starts a dialog to add new requests to the control file.

Running the script without specifying an action will bring you a menu asking what to do.
```
