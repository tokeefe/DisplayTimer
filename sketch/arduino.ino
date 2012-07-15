#include <stdlib.h>

int pin = 0;
char out[16];
boolean start = false;

void setup()
{
  Serial.begin(115200);
}

void loop()
{
  if(Serial.available())
  {
    if(Serial.read() == 255)
      start = true;
  }
  
  if(start)
  {
    sprintf(out, "%i,%u\n", analogRead(pin), millis());
    Serial.print(out);
  }
}
