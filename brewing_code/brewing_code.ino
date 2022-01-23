// Tentacle T1 Mk2 Arduino Sketch
// Author: Joshua Donaldson

/* 
+----------------------------+
| Sensor Addresses           |
+===========+====+=====+=====+
| Fermenter | DO |  pH | RTD |
+-----------+----+-----+-----+
| F1        | 96 |  99 | 102 |
+-----------+----+-----+-----+
| F2        | 97 | 100 | 103 |
+-----------+----+-----+-----+
| F3        | 98 | 101 | 104 |
+-----------+----+-----+-----+
*/

#include <Wire.h> //enable I2C.
#include <errno.h>

enum errors { 
  SUCCESS,
  FAIL,
  NOT_READY,
  NO_DATA
};

const int EZO_ANSWER_LENGTH = 32;
char ezo_answer[EZO_ANSWER_LENGTH]; // A 32 byte character array to hold incoming data from the sensors

String message = "";
char inByte;

// Fermenter Status
bool F1;
bool F2;
bool F3;

// Relay Pins
int P1 = 7;
int P2 = 8;
int P3 = 9;

int pumps [] = {P1, P2, P3 };

errors i2c_error; // error-byte to store result of Wire.transmissionEnd()
unsigned long next_receive_time;

void setup(){

  Serial.begin(9600); // Set the hardware serial port to 9600
  Wire.begin();       // enable I2C port.

  // Setup Relay Pins
  pinMode(P1, OUTPUT);
  pinMode(P2, OUTPUT);
  pinMode(P3, OUTPUT);

  // Write all Pins to High (Pump Off)
  digitalWrite(P1, HIGH);
  digitalWrite(P2, HIGH);
  digitalWrite(P3, HIGH);

  delay(1000);
  while (!Serial.available()){} //wait for message to get sent
  while (Serial.available()) {                         
    inByte = Serial.read(); 
    message.concat(inByte); 
    delay(100);             
  }

  Serial.print(message); //send message
  Serial.print('\n');    //add <CR>

  message.remove(0); //delete message

  F1 = get_fermenter_status();
  F2 = get_fermenter_status();
  F3 = get_fermenter_status();
}

void loop(){

  delay(100);
  message = Serial.readStringUntil('\n');


  if (message == "F"){
    if (F1) {
      get_reading(96);
      get_reading(99);
      get_reading(102);
    }

    if (F2) {
      get_reading(97);
      get_reading(100);
      get_reading(103);
    }

    if (F3) {
      get_reading(98);
      get_reading(101);
      get_reading(104);
    }

    Serial.println();
  }
    
  if (message == "PT1"){
    pump_on(P1);
  }
    
  
  if (message == "PT2"){
    pump_on(P2);
  }
  
  if (message == "PT3"){
    pump_on(P3);
  }
  
  if (message == "PF1"){
    pump_off(P1);
  }
    
  if (message == "PF2"){
    pump_off(P2);
  }
  
  if (message == "PF3"){
    pump_off(P3);
  }

  message.remove(0); //delete message
}

// request answer from an EZO device
void get_reading(const int address){

  Wire.beginTransmission(address);
  Wire.write("r");
  Wire.endTransmission();

  delay(900);

  byte sensor_bytes_received = 0;
  byte code = 0;
  byte in_char = 0;

  memset(ezo_answer, 0, EZO_ANSWER_LENGTH); // clear sensordata array;

  Wire.requestFrom(address, EZO_ANSWER_LENGTH - 1, 1);
  code = Wire.read();

  while (Wire.available()) {
    in_char = Wire.read();

    if (in_char == 0) {
      break;
    }
    else {
      ezo_answer[sensor_bytes_received] = in_char;
      sensor_bytes_received++;
    }
  }

  switch (code) {
    case 1:
      i2c_error = SUCCESS;
      Serial.print(ezo_answer);
      Serial.print(" ");
      break;

    case 2:
      i2c_error = FAIL;
      break;

    case 254:
      i2c_error = NOT_READY;
      break;

    case 255:
      i2c_error = NO_DATA;
      break;
  }
}

bool get_fermenter_status(){  
  while (!Serial.available()){} 
  inByte = Serial.read();
  if (inByte != '0') {
    return true;
  } else {
    return false;
  }
}

void pump_on(int pump){
  digitalWrite(pump, LOW);
}

void pump_off(int pump){
  digitalWrite(pump, HIGH);
}
