#include <Arduino.h>

// ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
// Author: Anita de Prado
//    Based on: JJROBOTS AIR HOCKEY ROBOT EVO PROJECT
//    http://jjrobotos.com/air-hockey-robot-evo/
//    Author: Jose Julio (JJROBOTS)
// Hardware: Arduino Mega2560 + JJROBOTS brain shield v3 (devia)
// Date: 03/01/2017
// Version: 0.00

// License: Open Software GPL License


#define VERSION "0.0"

// ROBOT and USER configuration parameters
#include "Configuration.h"
#include "Definitions.h"   // Variable definitions

void setup()
{
  // STEPPER PINS ON JJROBOTS BRAIN SHIELD
  pinMode(4, OUTPUT);   // ENABLE MOTORS
  pinMode(7, OUTPUT);   // STEP MOTOR 1 (PORTE, 6) --> (PORTH, 4) in Mega2560
  pinMode(8, OUTPUT);   // DIR MOTOR 1  (PORTB, 4) --> (PORTH, 5) in Mega2560
  pinMode(12, OUTPUT);  // STEP MOTOR 2 (PORTD, 6) --> (PORTB, 6) in Mega2560
  pinMode(5, OUTPUT);   // DIR MOTOR 2  (PORTC, 6) --> (PORTE, 3) in Mega2560
  digitalWrite(4, HIGH);  // Disbale stepper motors


  pinMode(A4, OUTPUT);    // Microstepping selector
  digitalWrite(A4, LOW);  // 1/8 Microstepping

  pinMode(A3,INPUT);      // User puch button (pushed=>gnd)
  digitalWrite(A3,HIGH);  // Enable pullup

  Serial.begin(115200);   // ESP & serial connection
  delay(3000); //5000

  //LED blink 3 times
  for (uint8_t k = 0; k < 3; k++)
  {
    digitalWrite(13, HIGH);
    delay(300);
    digitalWrite(13, LOW);
    delay(300);
  }

  //Serial.println("Initializing Wifi module...");
  // ESP Wifi module initialization routine.
  // The Robot will generate it´s own wifi network JJROBOTS_xx
  // and listen external UDP messages...
  ESPInit();

  //Serial.println("Initializing Stepper motors...");
  // STEPPER MOTORS INITIALIZATION
  // We use TIMER 1 for stepper motor 1 and Timer 3 for motor 2
  // TIMER1 CTC MODE
  TCCR1B &= ~(1 << WGM13);
  TCCR1B |=  (1 << WGM12);
  TCCR1A &= ~(1 << WGM11);
  TCCR1A &= ~(1 << WGM10);

  // output mode = 00 (disconnected)
  TCCR1A &= ~(3 << COM1A0);
  TCCR1A &= ~(3 << COM1B0);

  // Set the timer pre-scaler
  // Generally we use a divider of 8, resulting in a 2MHz timer on 16MHz CPU
  TCCR1B = (TCCR1B & ~(0x07 << CS10)) | (2 << CS10);

  OCR1A = ZERO_SPEED;   // Motor stopped
  dir_M1 = 0;
  TCNT1 = 0;

  // We use TIMER 3 for stepper motor 2
  // STEPPER MOTORS INITIALIZATION
  // TIMER3 CTC MODE
  TCCR3B &= ~(1 << WGM13);
  TCCR3B |=  (1 << WGM12);
  TCCR3A &= ~(1 << WGM11);
  TCCR3A &= ~(1 << WGM10);

  // output mode = 00 (disconnected)
  TCCR3A &= ~(3 << COM1A0);
  TCCR3A &= ~(3 << COM1B0);

  // Set the timer pre-scaler
  // Generally we use a divider of 8, resulting in a 2MHz timer on 16MHz CPU
  TCCR3B = (TCCR3B & ~(0x07 << CS10)) | (2 << CS10);

  OCR3A = ZERO_SPEED;   // Motor stopped
  dir_M2 = 0;
  TCNT3 = 0;

  delay(1000);
  TIMSK1 |= (1 << OCIE1A); // Enable Timer1 interrupt
  TIMSK3 |= (1 << OCIE1A); // Enable Timer1 interrupt

  // Enable steppers
  digitalWrite(4, LOW);

  delay(1000);

  //Initializing Robot initial position and parameters...
  position_M1 = (ROBOT_INITIAL_POSITION_X + ROBOT_INITIAL_POSITION_Y) * X_AXIS_STEPS_PER_UNIT;
  position_M2 = (ROBOT_INITIAL_POSITION_X - ROBOT_INITIAL_POSITION_Y) * Y_AXIS_STEPS_PER_UNIT;
  target_position_M1 = position_M1;
  target_position_M2 = position_M2;

  user_max_speed = MAX_SPEED*0.7;
  user_max_accel = MAX_ACCEL*0.7;
  max_acceleration = user_max_accel;
  max_speed = user_max_speed / 2;

  //Serial.println("Moving to initial position...");
  //setPosition_straight(ROBOT_INITIAL_POSITION_X, ROBOT_INITIAL_POSITION_Y);

  digitalWrite(13, HIGH);
  Serial.print("ICE-QUEEN ROBOT: Q-Learning AirHockey Robot version ");
  Serial.println(VERSION);
  Serial.println("ready...");

  testmode=false;
  robot_status = 0;

  //Time control:
   timer_old = micros();
   timer_packet_old = timer_old;
   micros_old = timer_old;
}

// Main loop
void loop()
{
  int dt;
  uint8_t logOutput = 0;

  debug_counter++;

  if (analogRead(A3)<100) // pushbutton pushed => TEST PATTERN
  {
    testmode=true;
    loop_counter=0;
  }

  timer_value = micros();
  if ((timer_value - timer_old) >= 1000) // MAIN 1Khz loop
  {
    timer_old = timer_value;
    loop_counter++;

    packetRead();  // Check for new packets...

    //If the packet is correct...
    if (newPacket > 0)
    {
      dt = (timer_value - timer_packet_old) / 1000.0;
      //Serial.println(dt);
      //dt = 16;  //60 Hz = 16.66ms
      timer_packet_old = timer_value;
      logOutput = 0;

      //Serial.print("P");
      //Serial.print(newPacket);


      if (newPacket == 2) {// EVO manual mode
        robot_status = 5;

      }else if (newPacket == 9) {// IceQueen manual mode
        robot_status = 9;

      }else{
        //LED blink 1 time long
          digitalWrite(13, LOW);
          delay(300);
          digitalWrite(13, HIGH);
          delay(1000);
          digitalWrite(13, LOW);
          delay(300);
          digitalWrite(13, HIGH);
          Serial.println("\"La estupidez humana siempre vencera\' a la inteligencia artificial\"-TerryPratchett");

      }

      robotStrategy();

      //Serial.println();
      newPacket = 0;
    }  // End packet received

    if (testmode)
      testMovements();

#ifdef DEBUG
    // DEBUG: We inform of the position error of the robot as seen in the camera (util for calibrations)
    if ((loop_counter % 1293) == 0) {
      //Serialprint("ROBOT MSD: ");
      //Serialprint(robotMissingStepsErrorX);
      //Serialprint(",");
      //Serialprintln(robotMissingStepsErrorY);
    }
#endif

    if ((loop_counter % 10) == 0)
      updatePosition_straight();  // update straight line motion algorithm

    // Position, speed and acceleration control:
    positionControl();
  } // 1Khz loop
}
