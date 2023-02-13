import mysql.connector

dbconnect = mysql.connector.connect(
    host='localhost',
    port='3306',
    user='root',
    password='',
    database='test'
)

mycursor = dbconnect.cursor()

def selectquery():
    mycursor.execute('SELECT * FROM students')
    mydata = mycursor.fetchall()
    return str(mydata)

def insertquery():
    insertquery = 'INSERT INTO students(firstname, lastname, age) VALUES(%s, %s, %s)'
    #values = ('Cecil', 'Boye', 31)
    values = ('David', 'van Meel', 24)
    mycursor.execute(insertquery, values)
    dbconnect.commit()
    return 'values inserted in database'

def wherequery(param):
    mycursor.execute('SELECT * FROM students WHERE age = %s', (param,))
    mydata = mycursor.fetchall()
    return str(mydata)