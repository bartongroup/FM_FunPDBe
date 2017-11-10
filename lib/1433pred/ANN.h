/*********************************************************
  ANN.h
  --------------------------------------------------------
  generated at Fri Sep 12 14:39:07 2014
  by snns2c ( Bernward Kett 1995 ) 
*********************************************************/

extern int ANN(float *in, float *out, int init);

static struct {
  int NoOfInput;    /* Number of Input Units  */
  int NoOfOutput;   /* Number of Output Units */
  int(* propFunc)(float *, float*, int);
} ANNREC = {200,1,ANN};
