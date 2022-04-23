#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Adafruit_MAX31865.h>
#include <Adafruit_MPU6050.h>

Adafruit_MAX31865 thermo_left = Adafruit_MAX31865(8, 7, 6, 5);
Adafruit_MAX31865 thermo_right = Adafruit_MAX31865(0, 1, 2, 3);

#define RREF      430.0
#define RNOMINAL  100.0

#define SPEC_TRG_1         A7 //A0
#define SPEC_ST_1          12 //A1 
#define SPEC_CLK_1         11 //A2
#define SPEC_VIDEO_1       A9 //A3

#define SPEC_TRG_2         A0 // A6
#define SPEC_ST_2          A1 // A7
#define SPEC_CLK_2         A2 // A8
#define SPEC_VIDEO_2       A3 // A9

#define SPEC_CHANNELS    289 // Define the number of channels for the spectrometer
uint16_t data_1[SPEC_CHANNELS]; // Define an array for the data read by the spectrometer
uint16_t data_2[SPEC_CHANNELS]; // Define an array for the data read by the spectrometer
int multipliers[SPEC_CHANNELS] = {0}; // Define an array for the coefficients of the simpson's rule

float const coeff = ((850.0 - 340.0)/(SPEC_CHANNELS - 1)/3); // Initial coefficient for the simpson's rule

float result_1 = 0.0; // Result of the integral
float result_2 = 0.0; // Result of the integral

float left_temp = 0.0;
float right_temp = 0.0;

Adafruit_MPU6050 mpu;

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

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  } 

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  Serial.begin(115200);
  while (!Serial){
    delay(10);
  }  

  thermo_left.begin(MAX31865_3WIRE);
  thermo_right.begin(MAX31865_3WIRE);

  pinMode(SPEC_CLK_1, OUTPUT);
  pinMode(SPEC_ST_1, OUTPUT);
  pinMode(SPEC_CLK_2, OUTPUT);
  pinMode(SPEC_ST_2, OUTPUT);

  digitalWrite(SPEC_CLK_1, HIGH); // Set SPEC_CLK High
  digitalWrite(SPEC_ST_1, LOW); // Set SPEC_ST Low
  digitalWrite(SPEC_CLK_2, HIGH); // Set SPEC_CLK High
  digitalWrite(SPEC_ST_2, LOW); // Set SPEC_ST Low

}



void readSpectrometer_2(){ // This is from the spec sheet of the spectrometer

  int delayTime = 1; // delay time

  // Start clock cycle and set start pulse to signal start
  digitalWrite(SPEC_CLK_2, LOW);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK_2, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK_2, LOW);
  digitalWrite(SPEC_ST_2, HIGH);
  delayMicroseconds(delayTime);

  //Sample for a period of time
  for(int i = 0; i < 15; i++){

      digitalWrite(SPEC_CLK_2, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_2, LOW);
      delayMicroseconds(delayTime);

  }

  //Set SPEC_ST to low
  digitalWrite(SPEC_ST_2, LOW);

  //Sample for a period of time
  for(int i = 0; i < 85; i++){

      digitalWrite(SPEC_CLK_2, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_2, LOW);
      delayMicroseconds(delayTime);

  }

  //One more clock pulse before the actual read
  digitalWrite(SPEC_CLK_2, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK_2, LOW);
  delayMicroseconds(delayTime);

  //Read from SPEC_VIDEO
  for(int i = 0; i < SPEC_CHANNELS; i++){

      data_2[i] = analogRead(SPEC_VIDEO_2);

      digitalWrite(SPEC_CLK_2, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_2, LOW);
      delayMicroseconds(delayTime);

  }

  //Set SPEC_ST to high
  digitalWrite(SPEC_ST_2, HIGH);

  //Sample for a small amount of time
  for(int i = 0; i < 7; i++){

      digitalWrite(SPEC_CLK_2, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_2, LOW);
      delayMicroseconds(delayTime);

  }

  digitalWrite(SPEC_CLK_2, HIGH);
  delayMicroseconds(delayTime);

}

void readSpectrometer_1(){ // This is from the spec sheet of the spectrometer

  int delayTime = 1; // delay time

  // Start clock cycle and set start pulse to signal start
  digitalWrite(SPEC_CLK_1, LOW);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK_1, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK_1, LOW);
  digitalWrite(SPEC_ST_1, HIGH);
  delayMicroseconds(delayTime);

  //Sample for a period of time
  for(int i = 0; i < 15; i++){

      digitalWrite(SPEC_CLK_1, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_1, LOW);
      delayMicroseconds(delayTime);

  }

  //Set SPEC_ST to low
  digitalWrite(SPEC_ST_1, LOW);

  //Sample for a period of time
  for(int i = 0; i < 85; i++){

      digitalWrite(SPEC_CLK_1, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_1, LOW);
      delayMicroseconds(delayTime);

  }

  //One more clock pulse before the actual read
  digitalWrite(SPEC_CLK_1, HIGH);
  delayMicroseconds(delayTime);
  digitalWrite(SPEC_CLK_1, LOW);
  delayMicroseconds(delayTime);

  //Read from SPEC_VIDEO
  for(int i = 0; i < SPEC_CHANNELS; i++){

      data_1[i] = analogRead(SPEC_VIDEO_1);

      digitalWrite(SPEC_CLK_1, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_1, LOW);
      delayMicroseconds(delayTime);

  }

  //Set SPEC_ST to high
  digitalWrite(SPEC_ST_1, HIGH);

  //Sample for a small amount of time
  for(int i = 0; i < 7; i++){

      digitalWrite(SPEC_CLK_1, HIGH);
      delayMicroseconds(delayTime);
      digitalWrite(SPEC_CLK_1, LOW);
      delayMicroseconds(delayTime);

  }

  digitalWrite(SPEC_CLK_1, HIGH);
  delayMicroseconds(delayTime);

}

float return_temperature(bool choice){

  float temp = 0.0;
  
  if (choice){
    temp = thermo_left.temperature(RNOMINAL, RREF);
  } else {
    temp = thermo_right.temperature(RNOMINAL, RREF);
  }

  return temp;
  
}


void printData(){ // Print the SPEC_CHANNELS data, then print the current time, the current color, and the number of channels.

  for (int i = 0; i < SPEC_CHANNELS; i++){

//    data_matrix(i) = data[i];
    Serial.print(data_1[i]);
    Serial.print(',');

  }

  for (int i = 0; i < SPEC_CHANNELS; i++){

//    data_matrix(i) = data[i];
    Serial.print(data_2[i]);
    Serial.print(',');

  }

  left_temp = return_temperature(true);
  right_temp = return_temperature(false);

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  Serial.print(result_1); // -9
  Serial.print(',');
  Serial.print(result_2); // -8 
  Serial.print(',');
  Serial.print(millis()); // -7
  Serial.print(',');
  Serial.print(SPEC_CHANNELS); // -6
  Serial.print(',');
  Serial.print(left_temp); // -5
  Serial.print(',');
  Serial.print(right_temp); // -4
  Serial.print(",");
  Serial.print(a.acceleration.x); // -3
  Serial.print(",");
  Serial.print(a.acceleration.y); // -2
  Serial.print(",");
  Serial.print(a.acceleration.z); // -1

  Serial.print("\n");
}

void calcIntLoop(){
  
  result_1 = 0;

  for(int i = 0; i < SPEC_CHANNELS; i++){ // Calculate each value for the simpson's rule.
    result_1 += multipliers[i] * data_1[i];
  }

  result_1 = coeff*result_1;

  result_2 = 0;

  for(int i = 0; i < SPEC_CHANNELS; i++){ // Calculate each value for the simpson's rule.
    result_2 += multipliers[i] * data_2[i];
  }

  result_2 = coeff*result_2;
}



void loop(){
  readSpectrometer_1();
  readSpectrometer_2();
  calcIntLoop();
  printData();
  delay(200);  

}
