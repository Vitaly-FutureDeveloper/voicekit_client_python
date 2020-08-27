from tinkoff_voicekit_client import ClientSTT

import configparser
import datetime
import os.path
import psycopg2


keysObj = configparser.ConfigParser()
keysObj.read('../keys.ini')

API_KEY = keysObj["keys"]["api-key"]
SECRET_KEY = keysObj["keys"]["secret-key"]

client = ClientSTT(API_KEY, SECRET_KEY)

audio_config = {
    "encoding": "LINEAR16",
    "sample_rate_hertz": 8000,
    "num_channels": 1
}

mock_arr = {
    "audio": "../audio/4.wav",
    "tel": 84654522,
    "db": 1,
    "stage": 1
}
"""
def db_insert(obj):
    dbconn = psycopg2.connect( host='localhost', user='postgres', password='123456', dbname='voicelogs' )
    cursor = dbconn.cursor()
    cursor.execute("INSERT INTO calls(id, timestamp, date, time, option, tel, audio_duration, audio_result) VALUES ('12', 1598188211, '12.12.2020', '15:00', 'SDSADSA', '4343', 'SDLIAUSDGBUSIADBA BSABD IASB', 'SD')")
    dbconn.commit()
    dbconn.close()
"""
def parse_dict_first(response):
    text = response[0]['alternatives'][0]['transcript']
    array_words = text.split()
    if 'автоответчик' in array_words:
        return 0
    else:
        return 1

def parse_dict_second(response):
    text = response[0]['alternatives'][0]['transcript']
    array_words = text.split()
    print(array_words)
    if 'неудобно' in array_words or 'нет' in array_words:
        return 0
    elif 'говорите' in array_words or 'да' in array_words or 'конечно' in array_words:
        return 1

def log_writter(response, mock_arr):
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    date = now.strftime("%Y-%m-%d")

    file_log = "logfiles\callslog.log"

    if mock_arr["stage"] == 1:
        count_id = 1
        if parse_dict_first(response):
            option = "Человек"
        else:
            option = "Автоответчик"
    else:
        count_id = 0
        if parse_dict_second(response):
            option = "Положительно"
        else:
            option = "Отрицательно"

    if not os.path.isfile(file_log):
        f = open(file_log, 'w')
        f.write("000000" + '\n\n')
        f.close()

    f = open(file_log, 'r')
    id = int(f.readline()) + count_id
    list_file = f.readlines()
    list_file[0] = str(id) + '\n\n'
    f.close()

    f = open(file_log, 'w')
    for index in list_file:
       f.write(index)
    f.close()

    objToFile = {
        "date": date,
        "time": time,
        "id": str(id),
        "option": option,
        "tel": str(mock_arr["tel"]),
        "audio_duration": response[0]['end_time'],
        "audio_result": str(response[0]['alternatives'][0]['transcript'])
    }

    f = open(file_log, 'a')
    f.write('Дата: ' + objToFile["date"] + '\n')
    f.write('Время: ' + objToFile["time"] + '\n')
    f.write('Уникальный id: ' + objToFile["id"] + '\n')
    f.write('Результат действия: ' + objToFile["option"] + '\n')
    f.write('Номер телефона: ' + objToFile["tel"] + '\n')
    f.write('Длительность аудио: ' + objToFile["audio_duration"] + '\n')
    f.write('Результат распознавания: ' + objToFile["audio_result"] + '\n\n')
    f.close()

    dbconn = psycopg2.connect( host='localhost', user='postgres', password='123456', dbname='voicelogs' )
    cursor = dbconn.cursor()
    cursor.execute("INSERT INTO calls(id, date, time, option, tel, audio_duration, audio_result) VALUES (%s,%s,%s,%s,%s,%s,%s)" % (objToFile["id"],"'"+objToFile["date"]+"'","'"+objToFile["time"]+"'","'"+objToFile["option"]+"'",objToFile["tel"],"'"+objToFile["audio_duration"]+"'","'"+objToFile["audio_result"]+"'"))
    #cursor.execute("INSERT INTO calls(id, date, time, option, tel, audio_duration, audio_result) VALUES ("objToFile['id'], '12.12.2020', '15:00', 'SDSADSA', '4343', 'SDLIAUSDGBUSIADBA BSABD IASB', 'SD')")
    dbconn.commit()
    dbconn.close()



# recognise method call
response = client.recognize(mock_arr["audio"], audio_config)

print(response[0]['alternatives'][0]['transcript'])
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d")
print(date)
if mock_arr["stage"] == 1:
    print(parse_dict_first(response))
    log_writter(response, mock_arr)
else:
    print(parse_dict_second(response, mock_arr))
    log_writter(response)