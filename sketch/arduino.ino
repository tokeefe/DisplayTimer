#include <stdlib.h>

int pin = 0;
char out[16];
boolean start = false;
unsigned long int t0;

void setup()
{
  Serial.begin(115200);
  Serial.flush();
  t0 = millis();
}

void loop()
{
  if(start)
  {
    sprintf(out, "%i,%u\n", analogRead(pin), millis());
    Serial.print(out);
    return;
  }
  
  if(Serial.available() > 0)
  {
    start = true;
    Serial.println(255);
  }
}
