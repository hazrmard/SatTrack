/*
 * ------------------------------
 *   MultipleSerialServoControl
 * ------------------------------
 *
 * Uses the Arduino Serial library
 *  (http://arduino.cc/en/Reference/Serial)
 * and the Arduino Servo library
 *  (http://arduino.cc/en/Reference/Servo)
 * to control multiple servos from a PC using a USB cable.
 *
 * Dependencies:
 *   Arduino 0017 or higher
 *     (http://www.arduino.cc/en/Main/Software)
 *   
 * Created:  23 December 2009
 * Author:   Brian D. Wendt (http://principialabs.com/)
 * 
 * Modified:    Fall/Spring 2015/16
 * Modified by: Ibrahim Ahmed (http://iahmed.me)
 *   
 * Version:  1.1
 * License:  GPLv3
 *   (http://www.fsf.org/licensing/)
 *
 */

// Import the Arduino Servo library
#include <Servo.h> 

// Create array of servos
Servo servos[6];

// Common servo setup values
int minPulse = 900;   // minimum servo position, us (microseconds)
int maxPulse = 2100;  // maximum servo position, us

// User input for servo and position
int userInput[4];    // raw input from serial buffer, 4 bytes
char startbyte;       // start byte, begin reading input
char mode;            // 'a' for angle, 'm' for pulse width in us
int servo;           // which servo to pulse?
int pos;             // servo angle 0-180
int i;               // iterator

// LED on Pin 13 for digital on/off demo
int ledPin = 13;
int pinState = LOW;

void linkServos(int from, int to) 
{

  // Attach each Servo object to a digital pin
  servos[0].attach(9, from, to);
  servos[1].attach(3, from, to);
  servos[2].attach(4, from, to);
  servos[3].attach(5, from, to);
  servos[4].attach(10, from, to);
  servos[5].attach(11, from, to);
  
}

void detachServos(Servo s[]) {
  for (int i=0; i<6; i++) {
    s[i].detach();
  }
}

void setup() 
{ 
  
  linkServos(minPulse, maxPulse);

  // LED on Pin 13 for digital on/off demo
  pinMode(ledPin, OUTPUT);

  // Open the serial connection, 9600 baud
  Serial.begin(9600);
} 

void loop() 
// Serial input is of the format s<motor #>a<angle> e.g
//s1a45
//s2a180
{ 
  // Wait for serial input (min 3 bytes in buffer)
  if (Serial.available()>0) {
    // Read the first byte
    startbyte = Serial.read();
    
    if (startbyte == 's') {        // command mode
      
      servo = Serial.parseInt();
      mode = Serial.read();
      pos = Serial.parseInt();
      Serial.print('s');
      Serial.print(String(servo));
      Serial.print(mode);
      
      if (mode == 'a') {           // move by angle
        
        // NOTE: from servo.h, angles have to be < 200 otherwise
        // interpreted as pulse width.
        servos[servo-1].write(pos);
        Serial.println(servos[servo-1].read());  // returns angle 0-180
        
      } 
      
      else if (mode == 'm') {    // move by pulse width in us
        
        servos[servo-1].writeMicroseconds(pos);
        Serial.println(servos[servo-1].readMicroseconds());  // read pulse width in us
        
      }
    }
    
    else if (startbyte == 'x') {
      
      // 'x' begins setup for servos: x<minPulse>_<maxPulse>
      int from = Serial.parseInt();
      Serial.read();
      int to = Serial.parseInt();
      detachServos(servos);
      linkServos(from, to);
      Serial.print("Reset:");
      Serial.print(String(from));
      Serial.print("-");
      Serial.println(String(to));
      
    }
    
    else if (startbyte == 'q') {    // signal end
        
        Serial.println("Ending serial.");
        Serial.end();
        
    }
  }
}

