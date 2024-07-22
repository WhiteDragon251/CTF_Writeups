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

