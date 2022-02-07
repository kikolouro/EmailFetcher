import mysql.connector
from decouple import UndefinedValueError, config
import json


def dataHandler():
    mydb = mysql.connector.connect(
        host=config("DBHOST"),
        user=config("DBUSER"),
        password=config("DBPW"),
        database=config("DB"),
        autocommit=True
    )
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("select items.name, value from history_log JOIN items on items.itemid = history_log.itemid JOIN hosts_groups on items.hostid = hosts_groups.hostid where clock > UNIX_TIMESTAMP(NOW() - INTERVAL 4 HOUR) and value like '%ERROR%' and groupid = 17")
    myresult = mycursor.fetchall()
    obj = {}
    for result in myresult:
        if result[0] not in obj:
            
            obj[result[0]] = {}
            obj[result[0]]["count"] = 0
            obj[result[0]]["errors"] = []
        obj[result[0]]["count"] += 1
        obj[result[0]]["errors"].append(result[1].decode('utf-8'))
    #print(obj)
    return obj
