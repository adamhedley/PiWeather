 /*
 Standalone Sketch to use with a Teensy LC and
 the following sensors;
 Sharp Optical Dust Sensor GP2Y1010AU0F
 MICS4514 Gas sensor 
 to capture raw data and pass it on for computing 
 on the RPi.
 ADC reference is 3.3V max - required voltage divider
 for 5V to 3V3
 Vout = Vin * ( R2 / (R1 + R2) )
*/

// Teensy LED 
const int tLED = LED_BUILTIN;
// Reset
int RST = 0; // Set pin to DIO PIN 0 for reset

// Battery Monitering
int batt = 5;         // Set to pin Analogue 5 (pin 19)
float batt_vo = 0;   // Voltage from battery 
float meas_batt = 0; // ADC value


// RPi DIO input to confirm Pi is still alive
int pi_act = 1;    // Set to pin DIO 1
int pi_run = 2;    // Set to pin DIO 2
int act_count = 0; // counter
int pi_count = 0;  // counter

// Optical Dust Sensor Pins  
int Vo = 0; // Set to pin Analog 0 (pin 14)
int LED = 15; // Set to pin DIO 15

// Variables for dust sensor
int samplingTime = 280;  // us
int sleepTime = 10;      // ms
  
float Vo_meas = 0;
float calcVoltage = 0;
float dustDensity = 0;

// Gas Sensor Pins
int PRE = 16; // Set to pin DIO 16
int NOX = 3;  // Set to pin Analog 3 (pin 17)
int RED = 4;  // Set to pin Analog 4 (pin 18)

// Variables for gas sesnor
float nox_meas = 0;
float red_meas = 0;
float nox_v = 0;
float red_v = 0;
float no2 = 0;
float co = 0;
float Rs = 0;
float RsR0 = 0;
float fred = 0;

// Check these vaules on sensor
float nox_R0 = 22100;   // Resistor on NOX
float red_R0 = 46800;   // Resistor on RED

void setup()
{

  // Initilise the digital pins as IO
  pinMode(LED, OUTPUT);   // For controlling the Dust Sensor. Move to other DIO if other analogue sensors are needed.
  pinMode(tLED, OUTPUT);
  pinMode(RST, INPUT);    // Reset
  pinMode(pi_act, INPUT_PULLUP); // Pi Active pi and add pull-up
  pinMode(pi_run, OUTPUT);       // Drive Pi RUN pin LOW to re-start pi
  digitalWrite(pi_run, HIGH);
  // Turn Teensy LED ON for SETUP
  digitalWrite(tLED, HIGH);
  delay(2*1000);
  digitalWrite(tLED, LOW);
  delay(2*1000);
  digitalWrite(tLED, HIGH);
  // Initilises communication to the serial monitor on hoast machine
  Serial.begin(9600);
  delay(500);
  Serial.println("Teensy Serial Communication Setup");

  // Set Dust sensor LED LOW
  digitalWrite(LED, LOW);

  // Preheat gas sensor for x minutes on turn on
  delay(2000);
  Serial.println("Preheating MICS-4514 Sensor");
  digitalWrite(PRE, HIGH);
  int j = 15;
  while (j > 1) {
    j--;
    Serial.print("Pre-Heating time left: ");
    Serial.println(j);
    delay(1000);
  }
  digitalWrite(PRE, LOW);
  Serial.println("Preheating Complete");

}


// Measure Sensors
void loop(){

  // If Pi has shut down for some reason, reboot using RUN reset pin

  // Reset for false trigger of shutdown pin
  pi_count++;
  //Serial.print("act_count ");
  //Serial.print(act_count);
  //Serial.print("    pi_count ");
  //Serial.println(pi_count);
  if (pi_count >= 60) {
    if (digitalRead(pi_act) == HIGH) {
      pi_count = 0;
      act_count = 0;
    }
  }
  // When Pi powers off
  if (digitalRead(pi_act) == LOW) {
    act_count++;
    if (act_count >= 240) {  // Each loop is about 1 second so this should be for 4 minutes
      digitalWrite(tLED,HIGH);
      delay(3*1000);
      digitalWrite(tLED,LOW);
      delay(1*1000);
      digitalWrite(pi_run,LOW);
      //Serial.print("pi_run ");
      //Serial.println(pi_run);
      delay(3*1000);
      digitalWrite(pi_run,HIGH);
      //Serial.print("pi_run ");
      //Serial.println(pi_run);
      act_count = 0;
    }
  }


  // Reset the Teensy via DIO input
  if (digitalRead(RST) == LOW) {
    // Flash LED to signal Reset Acknowledge
    // Speed up LED blink so you know its loaded
    int i = 40;
    Serial.print("Resetting Teensy...");

    while (i > 1) {
      i--;
      digitalWrite(tLED,HIGH);
      delay(i * 2);
      digitalWrite(tLED,LOW);
      delay(i * 2);
    }

    // Performs Reset
    SCB_AIRCR = 0x05FA0004;
  }

  // ************************************************
  // Reading Dust Sensor
  //                                     320 us
  // Drive LED high for 320 us             __  10 ms   __
  // Sample time is ~ 280 us.           __|  |________|  |__
  // Next Read must be after 10 ms


  digitalWrite(LED,HIGH);
  delayMicroseconds(samplingTime);
  Vo_meas = analogRead(Vo); // read the dust value 

  // For debugging
  //Serial.println(" ");
  //Serial.print("Dust Analogue Read ");
  //Serial.println(Vo_meas);
  //Serial.println(" ");
  
  delayMicroseconds(40);
  digitalWrite(LED,LOW);
  delay(sleepTime);
  
  // 0 - 5V mapped to 1 - 1023 integer values
  // Convert to voltage
  calcVoltage = Vo_meas * (5.0 / 1023.0);
  
  // For debugging
  //Serial.print("Calculated voltage ");
  //Serial.println(calcVoltage);
  
  // linear eqaution taken from http://www.howmuchsnow.com/arduino/airquality/
  // Chris Nafis (c) 2012
  dustDensity = 0.172 * calcVoltage - 0.0999;
  // Convert Density from mg to ug
  dustDensity = dustDensity * 1000; 
  if (dustDensity < 0) {
    dustDensity = 0;
  }
 

  // ************************************************
  // Reading Gas Sensor
  //
  // NOx - Nitrogen dioxide N02 = 0.05 - 10 ppm
  // R2 = 22.1 kOhms
  // Rs = 0.8 to 20 kOhms
  // Vo = 2.625 to 4.885 V
  //
  // RED - Carbon monoxide CO   = 1 - 1000 ppm
  // R2 = 46.8 kOhms
  // Rs = 100 - 1500 kOhms
  // Vo 0.151 to 1.594 V
  
  nox_meas = 0;
  red_meas = 0;

  nox_meas = analogRead(NOX);
  delay(10);
  red_meas = analogRead(RED);

  // 0 - 3.3 V mapped to 1 - 1023 integer values
  // Convert to voltage
  nox_v = nox_meas * (3.3 / 1023.0);
  nox_v = nox_v / 0.6666; //Voltage divider (r2 / r1+r2) = 0.6666
  
  red_v = red_meas * (3.3 / 1023.0);

  // For debugging
  //Serial.print("nox_meas ADC A3: ");
  //Serial.println(nox_meas);
  //Serial.print("nox voltage ");
  //Serial.println(nox_v);
  //Serial.print("red_meas ADC A4: ");
  //Serial.println(red_meas);
  //Serial.print("red voltage ");
  //Serial.println(red_v);
  //Serial.println(" ");
  
  // Find Sensor Resistance from nox_val using 5V input and 22 kOhm load resistor
  //Rs = nox_R0 / ((5 / nox_v) -1); 
  //fred = (.000008*Rs - .0194)*1000;
  //Serial.print("Rs Value: ");
  //Serial.println(Rs);
  //Serial.print("No2 2: ");
  //Serial.println(fred);
  //Serial.println(" ");

  // Eequation derived from data found on http://myscope.net/auswertung-der-airpi-gas-sensoren/
  // convert Rs to ppb concentration NO2
  // y = 0.9682x - 0.8108 where y and x are log10

  RsR0 = Rs / nox_R0;
  RsR0 = log10(RsR0);
  no2 = 0.9682 * RsR0;
  no2 = no2 - 0.8108;
  no2 = pow(10,no2);
  //no2 = no2 * 1000; // for ppb
  if (no2 < 0) {
    no2 = 0;
  }
  

  // Find Sensor Resistance from Red_val using 5V input ans 47 kOhm load resistor
  Rs = red_R0 / ((5 / red_v) -1); 

  // Eequation derived from data found on http://myscope.net/auswertung-der-airpi-gas-sensoren/
  // convert Rs to ppm concentration CO
  // y = -1.859x + 0.6201 where y and x are log10
  
  RsR0 = Rs / red_R0;
  RsR0 = log10(RsR0);
  co = -1.859 * RsR0;
  co = co + 0.6201;
  co = pow(10,co);
  if (co < 0) {
    co = 0;
  }
  if (co > 1000) {
    co = 1111;
  }


  // ************************************************
  // Monitor Battery Voltage

  batt_vo = 0;
  meas_batt = analogRead(batt);
  // 0 - 5V mapped to 1 - 1023 integer values
  // Convert to voltage
  batt_vo = meas_batt * (5.0 / 1023.0);

  // ************************************************
  // Print Data to serial port
  
  // " - " used for seperation of serial print on RPi  
  
  // Should print out a line as 
  // <Dust Sensor Data> - <sensor xxx>

  
  // Serial Print Dust Sensor Data    
  //Serial.print("Dust Density: ");
  Serial.print(dustDensity);
  Serial.print(" - ");

  // Serial Print Gas Sensor Data
  //Serial.print("CO ppm: ");
  Serial.print(co);
  Serial.print(" - ");
  //Serial.print("NO2 ppm: ");
  Serial.print(no2);
  Serial.print(" - ");

  // Serial Print Battery Voltage
  //Serial.print("Batt_v0: ");
  Serial.print(batt_vo);
  Serial.print(" - ");

  // Keep this here to make sure of line return
  Serial.println(" ");
  

  // LED Flash to signal data read and sent
  digitalWrite(tLED, HIGH);
  delay(50);
  digitalWrite(tLED, LOW);

  // Delay set for x second
  delay(1 * 1000);
}
