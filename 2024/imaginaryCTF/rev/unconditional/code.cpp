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