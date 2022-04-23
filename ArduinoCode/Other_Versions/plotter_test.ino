
#include <Adafruit_Sensor.h>
#include <Wire.h>
// #include <BasicLinearAlgebra.h> The matrix method takes up too much memory.

//using namespace BLA;

#define SPEC_TRG         A0
#define SPEC_ST          A1 
#define SPEC_CLK         A2
#define SPEC_VIDEO       A3

#define SPEC_CHANNELS    289 // Define the number of channels for the spectrometer
uint16_t data[SPEC_CHANNELS]; // Define an array for the data read by the spectrometer
int multipliers[SPEC_CHANNELS] = {0};

int redpin   = 21; //select the pin for the red LED
int greenpin = 22; // select the pin for the green LED
int bluepin  = 23; // select the pin for the  blue LED

long int seconds = 0;
long int total_seconds = 0;

int colorNum = -1;

float const coeff = ((850.0 - 340.0)/(SPEC_CHANNELS - 1)/3);

float result = 0.0;

//BLA::Matrix<1,289> multipliers_matrix;
//BLA::Matrix<289,1> data_matrix;

void setup() {

  
//  multipliers_matrix.Fill(0);
//  data_matrix.Fill(0); 

//  int num = 0;
//
//  for(int i = 0; i < SPEC_CHANNELS; i++){
//    if ((i==0) || (i==SPEC_CHANNELS)){
//      num = 1;
//    } else if (i % 2 == 1){
//      num = 4;
//    } else if (i % 2 == 0){
//      num = 2;
//    }
//    multipliers_matrix(i) = num;
//  }

int num = 0;

  for(int i = 0; i < SPEC_CHANNELS; i++){
    if ((i==0) || (i==SPEC_CHANNELS)){
      num = 1;
    } else if (i % 2 == 1){
      num = 4;
    } else if (i % 2 == 0){
      num = 2;
    }
    multipliers[i] = num;
  }
  
  Serial.begin(115200);
  while (!Serial){
    delay(10);
  }  

  pinMode(SPEC_CLK, OUTPUT);
  pinMode(SPEC_ST, OUTPUT);

  pinMode(redpin, OUTPUT);
  pinMode(bluepin, OUTPUT);
  pinMode(greenpin, OUTPUT);

  digitalWrite(SPEC_CLK, HIGH); // Set SPEC_CLK High
  digitalWrite(SPEC_ST, LOW); // Set SPEC_ST Low

  analogWrite(redpin, 143); // Violet
  analogWrite(greenpin, 0);
  analogWrite(bluepin, 255);
  colorNum = 0;

  //Serial.println(SPEC_CHANNELS);
  //Serial.print('\n');
}



void readSpectrometer(){

  int delayTime = 1; // delay time

  // Start clock cycle and set start pulse to signal start
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, LOW);
  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delayTime);

  //Sample for a period of time
  for(int i = 0; i < 15; i++){

      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);

  }

  //Set SPEC_ST to low
  digitalWrite(SPEC_ST, LOW);

  //Sample for a period of time
  for(int i = 0; i < 85; i++){

      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);

  }

  //One more clock pulse before the actual read
  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delayTime);

  //Read from SPEC_VIDEO
  for(int i = 0; i < SPEC_CHANNELS; i++){

      data[i] = analogRead(SPEC_VIDEO);

      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);

  }

  //Set SPEC_ST to high
  digitalWrite(SPEC_ST, HIGH);

  //Sample for a small amount of time
  for(int i = 0; i < 7; i++){

      digitalWrite(SPEC_CLK, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK, LOW);
      delayMicroseconds(delayTime);

  }

  digitalWrite(SPEC_CLK, HIGH);
  delayMicroseconds(delayTime);

}

/*
 * The function below prints out data to the terminal or
 * processing plot
 */

 
void printData(){

  for (int i = 0; i < SPEC_CHANNELS; i++){

//    data_matrix(i) = data[i];
    Serial.print(data[i]);
    Serial.print(',');

  }

  Serial.print(result);
  Serial.print(',');
  Serial.print(millis());
  Serial.print(',');
  Serial.print(colorNum);
  Serial.print(',');
  Serial.print(SPEC_CHANNELS);

  Serial.print("\n");
}

//void calcIntMatrix(){
//  result = 0.0;
//  BLA::Matrix<1,1> result_matrix = multipliers_matrix * data_matrix;
//  Serial.print(result_matrix(0));
//  result = result_matrix(0);
//}

void calcIntLoop(){
  
  result = 0;
  int num = 0;

  for(int i = 0; i < SPEC_CHANNELS; i++){
//    if ((i==0) || (i==SPEC_CHANNELS)){
//      num = 1;
//    } else if (i % 2 == 1){
//      num = 4;
//    } else if (i % 2 == 0){
//      num = 2;
//    }
    result += multipliers[i] * data[i];
  }

  result = coeff*result;
}

void changeColor(){
    if (((millis()%80000) < 10000)&&(colorNum != 0)){
    analogWrite(redpin, 143); // Violet
    analogWrite(greenpin, 0);
    analogWrite(bluepin, 255);
    colorNum = 0;
  } else if (((millis()%80000) >= 10000)&&((millis()%80000) < 20000)&&(colorNum != 1)){
    analogWrite(redpin, 0); // Blue
    analogWrite(greenpin, 0);
    analogWrite(bluepin, 255);
    colorNum = 1;
  } else if (((millis()%80000) >= 20000)&&((millis()%80000) < 30000)&&(colorNum != 2)){
    analogWrite(redpin, 0); // Cyan
    analogWrite(greenpin, 255);
    analogWrite(bluepin, 255);
    colorNum = 2;
  } else if (((millis()%80000) >= 30000)&&((millis()%80000) < 40000)&&(colorNum != 3)){
    analogWrite(redpin, 0); // Green
    analogWrite(greenpin, 128);
    analogWrite(bluepin, 0);
    colorNum = 3;
  } else if (((millis()%80000) >= 40000)&&((millis()%80000) < 50000)&&(colorNum != 4)){
    analogWrite(redpin, 255); // Yellow
    analogWrite(greenpin, 255);
    analogWrite(bluepin, 0);
    colorNum = 4;
  } else if (((millis()%80000) >= 50000)&&((millis()%80000) < 60000)&&(colorNum != 5)){
    analogWrite(redpin, 255); // Orange
    analogWrite(greenpin, 165);
    analogWrite(bluepin, 0);
    colorNum = 5;
  } else if (((millis()%80000) >= 60000)&&((millis()%80000) < 70000)&&(colorNum != 6)){
    analogWrite(redpin, 255); // Red
    analogWrite(greenpin, 0);
    analogWrite(bluepin, 0);
    colorNum = 6;
  } else if (((millis()%80000) >= 70000)&&((millis()%80000) < 80000)&&(colorNum != 7)){
    analogWrite(redpin, 0); // Off
    analogWrite(greenpin, 0);
    analogWrite(bluepin, 0);
    colorNum = 7;
  } 
}

void loop(){
  changeColor();
  readSpectrometer();
  calcIntLoop();
  printData();
  delay(100);  

}
