#include <stdlib.h>

int pin = 0;
char out[16];

void setup()
{
  Serial.begin(115200);
}

void loop()
{
  sprintf(out, "%i,%u\n", analogRead(pin), millis());
  Serial.print(out);
}
