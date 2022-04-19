#include <Adafruit_Sensor.h>
#include <Wire.h>

#define SPEC_TRG         A0
#define SPEC_ST          A1 
#define SPEC_CLK         A2
#define SPEC_VIDEO       A3

#define SPEC_CHANNELS    289 // Define the number of channels for the spectrometer
uint16_t data[SPEC_CHANNELS]; // Define an array for the data read by the spectrometer
int multipliers[SPEC_CHANNELS] = {0}; // Define an array for the coefficients of the simpson's rule

float const coeff = ((850.0 - 340.0)/(SPEC_CHANNELS - 1)/3); // Initial coefficient for the simpson's rule

float result = 0.0; // Result of the integral

void setup() {

  int num = 0;

  for(int i = 0; i < SPEC_CHANNELS; i++){ // Create the coefficients for the simpson's rule integral
    if ((i==0) || (i==SPEC_CHANNELS)){ // I = Delta x/3 * ( 1 f(x_0) + 4 f(x_1) + 2 f(x_2) + ... + 2 f(x_{n-2}) + 4 f(x_{n-1}) + f(x_n) )
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

  digitalWrite(SPEC_CLK, HIGH); // Set SPEC_CLK High
  digitalWrite(SPEC_ST, LOW); // Set SPEC_ST Low

  analogReadAveraging(64);

}



void readSpectrometer(){ // This is from the spec sheet of the spectrometer

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

      data[i] = analogRead(SPEC_VIDEO) - 155;

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


void printData(){ // Print the SPEC_CHANNELS data, then print the current time, the current color, and the number of channels.

  for (int i = 0; i < SPEC_CHANNELS; i++){

//    data_matrix(i) = data[i];
    Serial.print(data[i]);
    Serial.print(',');

  }

  Serial.print(result);
  Serial.print(',');
  Serial.print(millis());
  Serial.print(',');
  Serial.print(SPEC_CHANNELS);

  Serial.print("\n");
}

void calcIntLoop(){
  
  result = 0;

  for(int i = 0; i < SPEC_CHANNELS; i++){ // Calculate each value for the simpson's rule.
    result += multipliers[i] * data[i];
  }

  result = coeff*result;
}



void loop(){
  readSpectrometer();
  calcIntLoop();
  printData();
  delay(100);  

}
