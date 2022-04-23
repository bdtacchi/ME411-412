
#include <Adafruit_Sensor.h>
#include <Wire.h>
// #include <BasicLinearAlgebra.h> The matrix method takes up too much memory.

//using namespace BLA;

#define SPEC_TRG         A0
#define SPEC_ST          A1 
#define SPEC_CLK         A2
#define SPEC_VIDEO       A3

#define SPEC_CHANNELS    289 // New Spec Channel
uint16_t data[SPEC_CHANNELS];
int multipliers[SPEC_CHANNELS] = {0};

int redpin   = 11; //select the pin for the red LED
int greenpin = 10; // select the pin for the green LED
int bluepin  = 6; // select the pin for the  blue LED

long int seconds = 0;
long int total_seconds = 0;

String color;

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
//
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

  analogWrite(11, 143); // Violet
  analogWrite(10, 0);
  analogWrite(bluepin, 255);
  color = String('violet');

  Serial.println(SPEC_CHANNELS);
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

  Serial.print("\n");
}

void printChange(){

  for (int i = 0; i < SPEC_CHANNELS; i++){

    Serial.print(i+1);
    Serial.print(',');

  }

  Serial.print("\n");
}

//void calcIntMatrix(){
//  BLA::Matrix<1,1> result = multipliers_matrix * data_matrix;
//  Serial.println(result(0,0));
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

void loop(){

  if ((seconds < 10000)&&(color != String('violet'))){
    analogWrite(11, 143); // Violet
    analogWrite(10, 0);
    analogWrite(bluepin, 255);
    printChange();
    color = String('violet');
  } else if ((seconds >= 10000)&&(seconds < 20000)&&(color != String('blue'))){
    analogWrite(11, 0); // Blue
    analogWrite(10, 0);
    analogWrite(bluepin, 255);
    printChange();
    color = String('blue');
  } else if ((seconds >= 20000)&&(seconds < 30000)&&(color != String('cyan'))){
    analogWrite(11, 0); // Cyan
    analogWrite(10, 255);
    analogWrite(bluepin, 255);
    printChange();
    color = String('cyan');
  } else if ((seconds >= 30000)&&(seconds < 40000)&&(color != String('green'))){
    analogWrite(11, 0); // Green
    analogWrite(10, 128);
    analogWrite(bluepin, 0);
    printChange();
    color = String('green');
  } else if ((seconds >= 40000)&&(seconds < 50000)&&(color != String('yellow'))){
    analogWrite(11, 255); // Yellow
    analogWrite(10, 255);
    analogWrite(bluepin, 0);
    printChange();
    color = String('yellow');
  } else if ((seconds >= 50000)&&(seconds < 60000)&&(color != String('orange'))){
    analogWrite(11, 255); // Orange
    analogWrite(10, 165);
    analogWrite(bluepin, 0);
    printChange();
    color = String('orange');
  } else if ((seconds >= 60000)&&(seconds < 70000)&&(color != String('red'))){
    analogWrite(11, 255); // Red
    analogWrite(10, 0);
    analogWrite(bluepin, 0);
    printChange();
    color = String('red');
  } else if (seconds >= 70000){
    seconds = 0;
  }

  readSpectrometer();
  calcIntLoop();
  printData();
  delay(10);  
  total_seconds += 140;
  seconds += 140;

}
