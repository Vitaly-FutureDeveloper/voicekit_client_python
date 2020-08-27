#coding: utf-8
"""
Created on 28.08.2020

:author: Vitali
Тестовое задание для CIO | X-lab |
"""

from tinkoff_voicekit_client import ClientSTT

import configparser
import datetime
import os.path
import psycopg2


#Parser file keys
keysObj = configparser.ConfigParser()
keysObj.read('../keys.ini')
#Parser file keys

API_KEY = keysObj["keys"]["api-key"]
SECRET_KEY = keysObj["keys"]["secret-key"]

#DB connect constants
DB_NAME = "voicelogs"
USER = "postgres"
PASSWORD = "123456"
HOST = "localhost"

audio_config = {
    "encoding": "LINEAR16",
    "sample_rate_hertz": 8000,
    "num_channels": 1
}

mock_arr = {
    "audio": "../audio/4.wav",
    "tel": "84654522",
    "db": "1",
    "stage": "1"
}

def strtofloat(strin):
    return float(strin[:-1])
"""
    arr = list(map(str, strin))
    result = [0]
    i = 0
    for index in arr:
        if index.isdigit() or ".":
            result[i] = index
            i += 1
    return result.join()
"""
def err_logger(error):
    """
    :param: [string] error
    :return: void
    """
    file_log = "logfiles\errorslog.log"

    if not os.path.isfile(file_log):
        f = open(file_log, 'w')
        f.close()

    f = open(file_log, 'a')
    f.write(error + '\n\n')
    f.close()

def parse_dict_first(response):
    """
    :param[Object] response:
    :return: boolean
    """
    text = response[0]['alternatives'][0]['transcript']
    array_words = text.split()
    if 'автоответчик' in array_words:
        return 0
    else:
        return 1

def parse_dict_second(response):
    """
    :param[Object] response:
    :return: boolean
    """
    text = response[0]['alternatives'][0]['transcript']
    array_words = text.split()

    if 'неудобно' in array_words or 'нет' in array_words:
        return 0
    elif 'говорите' in array_words or 'да' in array_words or 'конечно' in array_words:
        return 1

def log_writter(response, mock_arr, parce_result):
    """
    :param[Object] response:
    :param[Object] mock_arr:
    :param[Object] boolean:
    :return: void
    """
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")
    date = now.strftime("%Y-%m-%d")

    file_log = "logfiles\callslog.log"

    if mock_arr["stage"] == "1":
        count_id = 1
        if parce_result:
            option = "человек"
        else:
            option = "автоответчик"
    else:
        count_id = 0
        if parce_result:
            option = "положительно"
        else:
            option = "отрицательно"

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

    float_duration = strtofloat(objToFile["audio_duration"])

    if mock_arr["db"] == "1":
        dbconn = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)
        cursor = dbconn.cursor()
        cursor.execute("INSERT INTO call(id, date, time, option, tel, audio_duration, audio_result) VALUES (%s,%s,%s,%s,%s,%s,%s)" % (objToFile["id"],"'"+objToFile["date"]+"'","'"+objToFile["time"]+"'","'"+objToFile["option"]+"'",objToFile["tel"],float_duration,"'"+objToFile["audio_result"]+"'"))
        dbconn.commit()
        dbconn.close()



#UI - User Interfase
mock_arr["audio"] = input("Пожалуйста, введите путь к аудио файлу: ")
mock_arr["tel"] = input("Номер телефона: ")
mock_arr["db"] = input("Нужно ли записывать в базу данных 1 - да, 0 - нет: ")
mock_arr["stage"] = input("Проход 1 или 2: ")
#UI - User Interfase

#Connect tinkoff_voicekit_client
client = ClientSTT(API_KEY, SECRET_KEY)

# recognise method call
response = client.recognize(mock_arr["audio"], audio_config)

if mock_arr["stage"] == "1":
    parse_first = parse_dict_first(response)
    print(parse_first)
    log_writter(response, mock_arr, parse_first)
else:
    parse_second = parse_dict_second(response)
    print(parse_second)
    log_writter(response, mock_arr, parse_second)
    #delete audio file after 2 stage
    try:
        os.remove(mock_arr["audio"])
    except OSError as e:
        err_logger("Ошибка удаления файла: %s : %s" % (file_path, e.strerror))