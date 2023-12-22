# not_so_guessy

## Challenge Description

Marshall's grandfather Marvin was a genius. He was able to retrieve 'The Flag' by beating The Guessy Game in the 1970s. It's the 2020s now and the Game has updated ever since and Marshall hasn't been able to beat it. But now he has found his GrandFather's logs and the script to The Guessy Game from the 1970s. Help Marshall beat The Guessy Game and get The Flag.

Attached files: [Public.zip](Public.zip)

Challenge author: L3G10N

## Solution

We are given three files `Guessy_1970.py`, `Guessy_2020.py` and `Marvin's logs.txt`. First let's try reading the `Guessy_1970.py` and `Marvin's log.txt`

`Guessy_1970.py`
```py
Secret_Number = "REDACTED"
Flag = "REDACTED"

coin = {1:'Heads', 0:'Tails'}
wins = 0

print("Welcome to The Guessy Game.")
print("To get The Flag, you have to beat me in Heads and Tails until I admit defeat.")
print("However if you lose once, You Lose.")

while Secret_Number:
    draw = coin[Secret_Number % 2]
    Secret_Number//=2
    print()
    print(f"Wins : {wins}")
    print('Heads or Tails?')
    guess = input()
    if guess == draw:
        wins += 1
        if Secret_Number==0 :
            print('Fine. I give up. You have beaten me.')
            print('Here is your Flag. Take it!')
            print()
            print(Flag)
            print()
            exit()
        print('Okay you guessed right this time. But its not enough to defeat me.')
    else : 
        print("Haha. I knew you didn't have it in you.")
        print("You guessed wrong. Bye byee")
        exit()
    """

```

`Marvin's logs.txt`
```
The Guessy Game:

This Game was a piece of cake. Lucky those People at Guessy Inc. are Idiots. They never change the Secret_Number.
It only took me 30 tries to get every guess right.

I remember my father's stories about our lineage being cursed by this game. That we were damned to choose 0 for eternity.
Anyways, I guess the saviour of this family was finally born. Haha.

Here are the correct Guess for the game:

Heads, Tails, Heads, Tails, Tails, Heads, Tails, Heads, Heads, Heads, Tails, Heads, Tails, Heads, Tails, Heads, Heads, Tails, Heads, Heads, Heads, Heads, Tails, Heads, Tails, Heads, Tails, Heads, Heads, Heads

```

The `Guessy_1970.py` is basically looks like a game in which a coin is flipped and the player is supposed to guess whether its heads or tails. The program first sets a `Secret_Number` and then it carries out the operation `Secret_Number % 2` which returns either `0` or `1` giving `Tails` or `Heads`, respectively. Then an integer division by 2 is carried out on the `Secret_Number` and the result is stored in `Secret_Number`. This loop is carried on until `Secret_Number` becomes equal to `0`. 

Then reading the logs.txt file, we can see the flaw in the code, i.e. the `Secret_Number` is not changed which means if we have the `Secret_Number` we can easily get all the answers right which gives the flag. But the server is using the `Guessy_2020.py` so let's analyze that.

```py
Secret_Number = "REDACTED"
Flag = "REDACTED"

AI = {2:'Scissors', 1:'Paper', 0:'Rock'}
win = {'Rock':'Paper','Paper':'Scissors','Scissors':'Rock'}
draws = 0
wins = 0

print("Welcome to The Guessy Game.")
print("To get The Flag, you have to beat the AI I made in Rock, Paper, Scissors until it can't take the losses and self-destructs.")
print("However if you lose once, You Lose.")
print("Beware! If the AI draws you twice, it will analyse your mind and you will never be able to defeat it ever.")

while Secret_Number:
    hand = AI[Secret_Number % 3]
    Secret_Number//=3
    print()
    print(f"Wins : {wins}, Draws : {draws}")
    print('Rock, Paper, Scissors!')
    guess = input()
    if guess == hand:
        print("Ah, Seems like its a draw.")
        draws += 1
        if draws == 2:
            print("The AI now knows your every move. You will never win.")
            exit()
    elif guess == win[hand]:
        wins += 1
        if Secret_Number==0 :
            print("Fine. You got me. It wasn't an AI it was just a simple Python Code.")
            print('Here is your Flag. Take it!')
            print()
            print(Flag)
            print()
            exit()
        print('Okay you guessed right this time. But its not enough to defeat my AI.')
    else : 
        print("Haha. I knew you didn't have it in you.")
        print("You guessed wrong. Bye byee")
        exit()
```

This program simulates a Rock, Paper, Scissors game. It pretty much works in the same fashion as the `Guessy_1970.py`, if we can figure out the `Secret_Number` then we can get all the correct answers.

So now let's start writing our exploit to figure out the `Secret_Number`. In the `Marvin's logs.txt` file we are given the correct guesses for the 1970 game. We can use this to retrieve the `Secret_Number`. I developed the below given python script to retrieve the `Secret_Number`.

```py
Secret_Number = 0

# correct_moves file
# Heads, Tails, Heads, Tails, Tails, Heads, Tails, Heads, Heads, Heads, Tails, Heads, Tails, Heads, Tails, Heads, Heads, Tails, Heads, Heads, Heads, Heads, Tails, Heads, Tails, Heads, Tails, Heads, Heads, Heads

with open('correct_moves', 'r') as f:
    correct_moves = f.read().strip('\n')

correct_moves = correct_moves.split(', ')
correct_moves = correct_moves[::-1]

coin = {'Heads':1, 'Tails':0}

correct_moves = [ coin[x] for x in correct_moves ]

for i in correct_moves:
    if i == 1:
        Secret_Number = Secret_Number*2 + 1
    elif i == 0:
        Secret_Number = Secret_Number*2

print(f"{Secret_Number=}")
```

The logic is simple, every time the answer is `heads` then the `Secret_Number` must be odd at that point and every time the answer is `tails` then the `Secret_Number` must be even at that point.

The `Secret_Number` obtained is `985508773`. Now all we need are the correct answers to the 2020 game. This can be done using another python script.

```py
Secret_Number = 985508773
Flag = "REDACTED"

AI = {2:'Scissors', 1:'Paper', 0:'Rock'}
win = {'Rock':'Paper','Paper':'Scissors','Scissors':'Rock'}

corrects = []
while Secret_Number:
    hand = AI[Secret_Number % 3]
    Secret_Number//=3
    corrects.append(win[hand])

print(corrects)
with open('correct_answer', 'w') as f:
    for x in corrects:
        f.write(str(x) + ' ')
```

Thus our correct guesses for the 2020 game are

```
Scissors Rock Rock Rock Scissors Rock Paper Paper Paper Rock Paper Scissors Paper Paper Rock Rock Scissors Scissors Rock 
```

Now, we can send this to server (either manually or use some script). I just sent it manually and voila, we have our flag 😎.

Thanks for reading!
