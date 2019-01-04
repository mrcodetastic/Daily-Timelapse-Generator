#!/usr/bin/env python

# Be a good citizen and don't pollute the namespace: http://stackoverflow.com/questions/17255737/importing-variables-from-another-file
import config; 

# Connect to the database
# https://docs.python.org/3/library/sqlite3.html#accessing-columns-by-name-instead-of-by-index
# http://pythoncentral.io/advanced-sqlite-usage-in-python/
import sqlite3

# Connect to database, run query, close immediately. 
# http://stackoverflow.com/questions/9561832/what-if-i-dont-close-the-database-connection-in-python-sqlite
def query (sql):
    con = sqlite3.connect(config.application_directory + 'timelapse.db')
    con.row_factory = sqlite3.Row
    with con:
        cur = con.cursor()
        cur.execute(sql)
        res = cur.fetchall()
    if con:
        con.close()
    return res
	
def execute (sql, values):
    con = sqlite3.connect(config.application_directory + 'timelapse.db')
    con.row_factory = sqlite3.Row
    with con:
        cur = con.cursor()
        cur.execute(sql, values)
        res = cur.fetchall()
    if con:
        con.close()
    return res
	
    