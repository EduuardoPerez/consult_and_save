# consult-and-save

Consult a url, get the data and save it in a MySQL database.

## About

This project is for made consult to a url, get the data and save in a MySQL database, if the url doesn't response
it's going to save a default message.

The database data to connect, the url, the time to wait the response and the default message it's going to be
save it in configuration files.

## Setup

```
Create the MyQSQL database
Create a virtual enviroment
Configurate the variables in the ./config/config.ini file
Activate the virtual enviroment
Install:
    pip install -r requirements.txt
Run:
    python main.py
```
