//Author: Liam Kelly

#include <Servo.h>
Servo servo1;
Servo servo2;
int pos1 = 90;
int pos2 = 90;
int counter;
int angle;


int minPulse = 600;
int maxPulse = 2400;

void setup() {

  Serial.begin(9600);
  servo1.attach(9, minPulse, maxPulse);
  servo2.attach(5);
  servo1.write(pos1);
  servo2.write(pos2);

  Serial.write('1');
  counter = 0;
  
}

void loop() {
/*
  if(counter > 5000) {
    Serial.write('1');
    counter = 0;
  }*/

  
  if(Serial.available()) {
    
    while(Serial.peek() == 'O')
    {
      Serial.read();
      Serial.println("received");
      angle = Serial.parseInt();
      Serial.println(String(angle));
      pos1 = int(map(angle, 0, 360, 50, 140));
      Serial.println(String(pos1));
      servo1.write(pos1);
      
    }
    
    /*
    while(Serial.peek() == 'u')
    {
      Serial.read();
      pos1++;
      servo1.write(pos1);
      Serial.println(String(pos1));
    }
    while(Serial.peek() == 'd')
    {
      Serial.read();
      pos1-=1;
      servo1.write(pos1);
      Serial.println(String(pos1));
    }
  }
*/


    
  

  }}


  
