# Mastardet Basic Binary and Linux

This was one of the best challenges I have ever solved and this was created by **mastardet (he is great guy and an elite hacker)**. 

If you guys wanna learn more from him, then make sure you check out his [**YouTube channel**](https://www.youtube.com/channel/UC66idcoWzeZ_AsTnYr3L37g/featured) right away, you will surely gather lot of good stuff from there! Alright, let's move towards the challenge then...

## Walkthrough

#### Finding the password

The challenge begins with a binary, that's all we are given. So the first step is obviously to figure out what the binary does.

```
./challenge_linux
```

![password_prompt](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/password_prompt.png)

We are given a prompt saying `root@cyberwizards password:`. Well, looks like a machine and we definitely need a password to get in. 

![ip address](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/ip_address.png)

Once you quit the program, you will notice see an **ip address** come up. I had asked **mastardet (the challenge creator)** about this and he did say me that you don't have to do anything with the ip. So that ip is nothing to be worried and if you even try to `ping` the ip, you will notice you can't do that, so we can't find anything exploitable using this ip address.

So, moving ahead, I tried sending **payloads** thinking I could overflow it, but that didn't work! Ok, so let's try some other stuff out.<br>
Let's try reversing the binay and see what we get.

```
r2 -d ./challenge_linux
```

![radare2](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/radare2.png)

Ok, so this is insane, when we try to print the functions, there are more than 1000 functions and there is no main function. If you all wanna go ahead and try to reverse it then please carry on, but I really don't think you will get any success. And well, when you try going through the binary in `vim` you will see that it is written in `go` which must be why its hard to reverse it. Or you can simply use the file command to see that its written in `go`.

Alright then, let's try out the simpler stuff. Let's just use `strings` and `grep` to get useful information.

```
strings ./challenge_linux | grep -i --color flag
```

![flag_grep](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/flag_grep.png)

This looks interesting, but doesn't seem we can use it at the moment to our advangtage in anyway. So let's move on.

```
strings ./challenge_linux | grep -i --color root
```

![flag_grep](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/root_grep.png)

Can't see anything useful in this one.

```
strings ./challenge_linux | grep -i --color cyberwizards
```

![flag_grep](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/cyberwizards_grep.png)

Alright, so this one took me a while (actually it took me hours to figure out, haha...) but when you look at it closely you can see it!! This must be the password we were looking for. Let's see if it works...

![Machine_promt](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/machine_prompt.png)

Ok great!! The password we found is correct. 

#### Reading the flag in the restricted shell environment

And now we are given a shell and when we run `ls -la`, we can see that the `flag.txt` is right there. 

![ls la](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/ls_la.png)

Alright, let's grab it using `cat`.

![cat_error](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/cat_error.png)

So here comes the twist in the story! I am sure you must have noticed by now that commands like `cat`, `less`, `more`, etc. are not even there. In fact, you can't run most of the commands. Now, some of you might try to `reboot` or `shutdown` and will get this-

![shut_reboot_flag](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/shut_reboot_flag.png)

Sorry mates, but that is not the flag. We need to dig more to find it.

Now, when you will run the `help` command, you will see all the commands available to you. So we have `ls`, `pwd`, `export`, `exit`, `whoami`, `history`, `logout` and `clear`. Among all these, all that seems useful is the `export` command.

![help_command](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/help_command.png)

So I tried running the `export` command and even tried to modify the values of the environment variables such as `$PATH` and `$SHELL` but all that ended up giving me an error.

![export_error](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/export_error.png)

There is another command that's behaving strange. Once you have tried running all the commands from the help menu, you will notice something stragne with the `history` command. It should ideally print all the commands we have entered till now but it just prints the same stuff again and again.

![weird history](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/weird_history.png)

So, when you took a look at the **HINT 4** and **HINT 5** given [here](https://whitedragon251.github.io/cyber_wizards_CTF/), you will immediately understand that you need to work on the `history` and the `export` command. So let's get started.

And obviously, in these situations Google is our best friend!! So I did a lot of googling and then I came across this

![Googling](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/Finding%20What%20to%20do.png)

So, `HISTFILE` is an **environment variable** that specifies the file for `history` command to read from. This looks interesting... So what happens when we set the `HISTFILE` to `/root/flag.txt` :)

![HISTFILE](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/HISTFILE.png)

Alright, great, the command worked!! But still, if we run `history`, that prints the same old stuff.

![history_fail](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/history_not_working.png)

So, I looked up a little more on Google and I finally found this on StackOverflow

[StackOverflow: history command does not show all lines in HISTFILE](https://unix.stackexchange.com/questions/549450/history-command-does-not-show-all-lines-in-histfile)

Ok, so now we know that we need to refresh the history using the `history -r`. Alright, so let's grab that flag hackers!!

![Flag](https://github.com/WhiteDragon251/cyber_wizards_CTF/raw/master/images/flag.png)

Voila!! We have the flag!!
