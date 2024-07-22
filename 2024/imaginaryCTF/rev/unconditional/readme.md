# Rev/Unconditional

## Description

Can you reverse this flag mangler? The output is b4,31,8e,02,af,1c,5d,23,98,7d,a3,1e,b0,3c,b3,c4,a6,06,58,28,19,7d,a3,c0,85,31,68,0a,bc,03,5d,3d,0b

The input only contains lowercase letters, numbers, underscore, and braces .

Attachments: [chal](chal)

## Challenge Overview

First when we try to run the program it simply gives us this output.

`37,3d,8e,0c,96,1f,d9,7d,a1,31,93,13,85,3e,ad,05,f6,00,c5,35,c5,45,63,00,85,0c,34,08,44,14,45,00,63,`

Using Ida we can obtain the psuedocode (was actually given to me by a teammate) and start analyzing that.

```cpp
#include <iostream>
using namespace std;
int main() {
    string flag = "nothing_here_lmao";
    int table1[] = {82, 100, 113, 81, 84, 118};
    int table2[] = {1, 3, 4, 2, 6, 5};
    int counter1 = 0, counter2 = 0;
    for (int i = 0; i < flag.size(); i++) {
        char v3 = flag[i];
        bool v1, v4;
        v4 = (i & 1 != 0);
        v1 = v3 > 0x60 && v3 <= 'z';
        flag[i] = ((((int)v3 >> table2[counter2]) | (v3 << (8 - table2[counter2]))) * v1
            + !v1 * (((v3 << 6) | (v3 >> 2)) ^ table1[counter1]))
           * ((i & 1) == 0)
           + ((v3 ^ table1[counter1]) * v1 + !v1 * ((4 * v3) | (v3 >> 6))) * ((i & 1) != 0);
        counter1=(v4+counter1)%6;
        counter2=(v4+counter2)%6;
        printf("%02x ,",(uint8_t)int(flag[i]));
    }
    return 0;
}
```

So the program basically carries out various operations on the flag and then gives hex numbers as the output. But the exploit here was that we could do a character by character bruteforce to figure out the flag. Hence if we set the `flag="ictf{"` then the program would return `b4,31,8e,02,af` which are the first hex numbers given in the description.

The description gives us the output when the actual flag is set. Thus we could use this bruteforce the flag character by character.

## Exploit

exploit.cpp

```cpp
#include <iostream>
using namespace std;
int calculateFlag(string flag, int newFlag[]) {
    int table1[] = {82, 100, 113, 81, 84, 118};
    int table2[] = {1, 3, 4, 2, 6, 5};
    int counter1 = 0, counter2 = 0;
    for (int i = 0; i < flag.size(); i++) {
        char v3 = flag[i];
        bool v1, v4;
        v4 = (i & 1 != 0);
        v1 = v3 > 0x60 && v3 <= 'z';
        flag[i] = ((((int)v3 >> table2[counter2]) | (v3 << (8 - table2[counter2]))) * v1
            + !v1 * (((v3 << 6) | (v3 >> 2)) ^ table1[counter1]))
           * ((i & 1) == 0)
           + ((v3 ^ table1[counter1]) * v1 + !v1 * ((4 * v3) | (v3 >> 6))) * ((i & 1) != 0);
        counter1=(v4+counter1)%6;
        counter2=(v4+counter2)%6;
        // printf("%02x ,",(uint8_t)int(flag[i]));
        newFlag[i] = (uint8_t)int(flag[i]);
    }
    return 0;
}

int main() {
    int flag[33];
    int correct[] = {180, 49, 142, 2, 175, 28, 93, 35, 152, 125, 163, 30, 176, 60, 179, 196, 166, 6, 88, 40, 25, 125, 163, 192, 133, 49, 104, 10, 188, 3, 93, 61, 11};
    
    string correctFlag="ictf{";
    string characters="1234567890_}?!abcdefghijkjlmnopqrstuvwxyz";
    int current = 6;
    while (current<50) {
        for (int i=0; i<characters.length(); i++) {
            int found = 1;
            string tempFlag = correctFlag + characters[i];
            calculateFlag(tempFlag, flag);
            for (int j=0; j<current; j++) {
                if (flag[j] != correct[j]){
                    found = 0;
                }
            }

            if (found == 1) {
                correctFlag = tempFlag;
                cout<<correctFlag<<endl;
                break;
            }
        }
    current++;
    }
    return 0;
}
```

This gives us our flag `ictf{m0r3_than_1_way5_t0_c0n7r0l}`.