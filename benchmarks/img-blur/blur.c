/* blur.c */
#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include "mypgm.h"

#define RADIUS 2

void blur( )
{
  /* Initialization of image2[y][x] */
  for (int ya = 0; ya < y_size1; ya++) {
    for (int xa = 0; xa < x_size1; xa++) {
      image2[ya][xa] = image1[ya][xa];
    }
  }

  x_size2 = x_size1;
  y_size2 = y_size1;

  for (int i = RADIUS; i < y_size1 - RADIUS; i++) {
    for (int j = RADIUS; j < x_size1 - RADIUS; j++) {
      double blur = 0.0;
      int total = 0;
      for (int ii = i - RADIUS; ii <= i + RADIUS ; ii++) {
        for (int jj = j - RADIUS; jj <= j + RADIUS ; jj++) {
          blur += image1[ii][jj];
          total++;
        }
      }


      // blur = image1[i][j] + image1[i + 1][j] + image1[i - 1][j] + image1[i][j + 1] + image1[i][j - 1];
      // blur = blur/5;
      image2[i][j] = (unsigned char)(blur/total);
      // printf("%d, %d\n", i, j);
    }
  }
}

int main(int argc, const char** argv)
{
  load_image_data(argv[1]);   /* Input of image1 */
  blur( );   /* Blur is applied to image1 */
  save_image_data();   /* Output of image2 */
  return 0;
}

