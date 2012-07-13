#include <stdlib.h>

// analog pin 0
int pin = 0;

void setup()
{
  Serial.begin(115200);
}

void loop()
{
  int level = analogRead(pin);
  Serial.println(level);
}
