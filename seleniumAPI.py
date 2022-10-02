import asyncio
import time
import json
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By

def sendEmail(to, subject, body):
    gmail_user = 'aspennotifier@gmail.com'
    gmail_password = 'duyguottvgkgbheg'

    sent_from = "Aspen Notifier"

    email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, to, subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)

def get_class_data(username, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0')
    browser = webdriver.Chrome(options = options)
    browser.set_page_load_timeout(30)
    
    browser.get("https://ma-mpsd.myfollett.com/aspen/logon.do")


    formInputs = browser.find_elements(By.CLASS_NAME,"logonInput")
    formInputs[0].send_keys(username)
    formInputs[1].send_keys(password)

    browser.find_element(By.ID,"logonButton").click()
    
    browser.find_element(By.LINK_TEXT,"Academics").click()

    classesData = {
        username: []
    }

    time.sleep(1)
    listCells = browser.find_elements(By.CLASS_NAME,"listCell")

    for cell in listCells:
        tableElements = cell.find_elements(By.TAG_NAME, 'td')

        className = tableElements[2].text
        teacher = tableElements[4].text
        grade = tableElements[6].text

        classData = {
            "name": className,
            "teacher": teacher,
            "grade": grade
        }

        classesData[username].append(classData)
    browser.quit()

    return classesData

def get_grades():
    usernames = ["***"]
    passwords = ["***"]

    fullClassData = {}

    for i in range(0, len(usernames)):
        classData = get_class_data(usernames[i], passwords[i])
        fullClassData[usernames[i]] = classData[usernames[i]]


    jsonData = {}
    with open("classdata.json", "r") as js:
        jsonData = json.load(js)

    for i in range(0, len(usernames)):
        username = usernames[i]
        if jsonData == {} or (not username in jsonData) or jsonData[username] == []:
            print("Empty file")
            #empty file
            with open("classdata.json", "w") as js:
                js.write(json.dumps(fullClassData))

            return
        
        outMessage = f""

        for i in range(0, len(fullClassData[username])):
            old_class = jsonData[username][i]
            new_class = fullClassData[username][i]

            #on term change classes can change, which would trigger this incorrectly
            if old_class["name"] == new_class["name"]:
                if old_class["grade"] != new_class["grade"]:
                    outMessage = outMessage + f"Your {new_class['name']} grade changed from {old_class['grade']} to {new_class['grade']}\n"
        
        if outMessage != "":
            sendEmail(username + "@students.mpsd.org", "Aspen Changes!", outMessage)


    with open("classdata.json", "w") as js:
        js.write(json.dumps(fullClassData))

get_grades()