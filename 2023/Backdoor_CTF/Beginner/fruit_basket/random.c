#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main () {
   int i, n;
   
   n = 51;
   
   /* Intializes random number generator */
   long int t = time(0) + 5;
   
   printf("%d\n", t);
   srand(t);

   for( i = 0 ; i < n ; i++ ) {
      printf("%d ", rand() % 10);
   }
   printf("\n");

   while (1) {
       if (time(0) == t-1) {
	   printf("Start");
	   break;
       }
   }
   

   return(0);
}
