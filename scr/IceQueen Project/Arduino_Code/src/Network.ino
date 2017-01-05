#include <Arduino.h>

// ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
//  Based on: JJROBOTS AIR HOCKEY ROBOT EVO PROJECT

// ESP Wifi module functions
// and UDP packets decoding...

uint16_t extractParamInt(uint8_t pos) {
  union {
    unsigned char Buff[2];
    uint16_t d;
  }
  u;

  u.Buff[0] = (unsigned char)SBuffer[pos];
  u.Buff[1] = (unsigned char)SBuffer[pos + 1];
  return (u.d);
}

// Read UDP packets from remote device. Only Manual Modes.
// Packet structure:
// Packet 2: Set manual robot position packet: (include robot position read from camera)
//      sync bytes[3]+[12]:   "mm2"[3bytes]
//                            + user_target_posX_mm[UINT16] + user_target_posY_mm[UINT16]
//                            + speed[UINT16] + accel[UINT16]
//                            + robotCoordX_mm[UINT16] + robotCoordY_mm[UINT16]
// Packet 9: Set manual IceQueen Robot simple position packet: (same but without speed/accel)
//      sync bytes[3]+[12]:   "mma"[3bytes]
//                            + user_target_posX_mm[UINT16] + user_target_posY_mm[UINT16]
//                            + payload[UINT16] + payload[UINT16]
//                            + robotCoordX_mm[UINT16] + robotCoordY_mm[UINT16]
//
void packetRead()
{
  unsigned char i;
  uint16_t value;

  if (Serial.available() > 0) {

    // we use direct character manipulation because itÃ‚Â´s fast and we had some problems with arduino String functions...
    // We rotate the Buffer (we could implement a ring buffer in future...)
    for (i = (PACKET_SIZE - 1); i > 0; i--){
      SBuffer[i] = SBuffer[i - 1];
    }
    SBuffer[0] = Serial.read();

    // We look for a  message sync start (mm1, mm2, mmc or mma)
    if ((SBuffer[2] == 'm') && (SBuffer[1] == 'm'))
    {
      if (readStatus != 0){
        Serial.println("P ERR");
      }
      switch (SBuffer[0]) {
        case 'a':
          readStatus = 9;     // PACKET TYPE 9 (Anita's test)
          Serial.println("P type: mma\n");
          break;
        default:
          newPacket = 0; // No valid packet! Or old packets
          Serial.println("P ERR");
      }
      readCounter = PACKET_SIZE;
      return;
    }


    if (readStatus == 9)
    {
        readCounter--;   // Until we complete the packet
        if (readCounter <= 0) // packet complete!!
        {
          // for (int pos = 0; pos < PACKET_SIZE; pos++){
          //   Serial.print("extrayendo pos[");
          //   Serial.print(pos);
          //   Serial.print("] = ");
          //   Serial.println(extractParamInt(pos));
          // }

          if (extractParamInt(6) != 0xFFFF) // Check payload (as a quality control)
          {
            Serial.println("mma PACKET ERROR! No correct final payload");
            readStatus = 0;
            newPacket = 0;
            return;
          }

          // CHECK MAXIMUNS
          user_target_x = constrain(extractParamInt(10), 0, ROBOT_MAX_X);
          user_target_y = constrain(extractParamInt(8), 0, ROBOT_MAX_Y);
          //payload = extractParamInt(6);
          //payload = extractParamInt(4);
          robotCoordX = extractParamInt(2);
          robotCoordY = extractParamInt(0);
          // Recibido
          newPacket = 9;
          readStatus = 0;
        }

    }
    else if (readStatus == 2)
    {
        readCounter--;   // Until we complete the packet
        if (readCounter <= 0) // packet complete!!
        {
          // CHECK MAXIMUNS
          user_target_x = constrain(extractParamInt(10), 0, ROBOT_MAX_X);
          user_target_y = constrain(extractParamInt(8), 0, ROBOT_MAX_Y);
          user_target_speed = constrain(extractParamInt(6), MIN_SPEED, MAX_SPEED);
          user_target_accel = constrain(extractParamInt(4), MIN_ACCEL, MAX_ACCEL);
          robotCoordX = extractParamInt(2);
          robotCoordY = extractParamInt(0);
          newPacket = 2;
          readStatus = 0;
        }
    }
  }
}

// ESP initialization process...
// We configure the ESP8266 to generate a JJROBOTS_xx Wifi and
// Listen UDP messages on port 2222
// --> "_xx" depends on your robot = 78 (in my case)
void ESPInit()
{
  // With the ESP8266 WIFI MODULE WE NEED TO MAKE AN INITIALIZATION PROCESS
  Serial.println("Initalizing ESP Wifi Module...");
  Serial.flush();
  Serial.print("+++");  // To ensure we exit the transparent transmision mode
  delay(100);
  ESPsendCommand("AT", "OK", 1);
  ESPsendCommand("AT+RST", "OK", 2); // ESP Wifi module RESET
  ESPwait("ready", 6);
  ESPsendCommand("AT+GMR", "OK", 5);
  Serial.println("AT+CIPSTAMAC?");
  ESPgetMac();
  //Serialprint("MAC:");
  //Serialprintln(MAC);
  delay(250);
  ESPsendCommand("AT+CWQAP", "OK", 3);
  ESPsendCommand("AT+CWMODE=2", "OK", 3); // Soft AP mode
  // Generate Soft AP. SSID=JJROBOTS, PASS=87654321
  char *cmd =  "AT+CWSAP=\"JJROBOTS_78\",\"87654321\",5,3";
  // Update XX characters with MAC address (last 2 characters)
  // / --> "_xx" depends on your robot = 78 (in my case)
  cmd[19] = MAC[10];
  cmd[20] = MAC[11];
  ESPsendCommand(cmd, "OK", 6);

  // Start UDP SERVER on port 2222
  //Serial.println("Start UDP server at port 2222");
  ESPsendCommand("AT+CIPMUX=0", "OK", 3);  // Single connection mode
  ESPsendCommand("AT+CIPMODE=1", "OK", 3); // Transparent mode
  //ESPsendCommand("AT+CIPSTART=\"UDP\",\"0\",2223,2222,0", "OK", 3);
  ESPsendCommand("AT+CIPSTART=\"UDP\",\"192.168.4.2\",2223,2222,0", "OK", 3);
  delay(250);
  ESPsendCommand("AT+CIPSEND", ">", 2); // Start transmission (transparent mode)
  delay(250);   // Time to settle things... the bias_from_no_motion algorithm needs some time to take effect and reset gyro bias.
}


int ESPwait(String stopstr, int timeout_secs)
{
  String response;
  bool found = false;
  char c;
  long timer_init;
  long timer;

  timer_init = millis();
  while (!found) {
    timer = millis();
    if (((timer - timer_init) / 1000) > timeout_secs) { // Timeout?
      //Serialprintln("!Timeout!");
      return 0;  // timeout
    }
    if (Serial.available()) {
      c = Serial.read();
      //Serialprint(c);
      response += c;
      if (response.endsWith(stopstr)) {
        found = true;
        delay(10);
        Serial.flush();
        //Serialprintln();
      }
    } // end Serial1_available()
  } // end while (!found)
  return 1;
}

// getMacAddress from ESP wifi module
int ESPgetMac()
{
  char c1, c2;
  bool timeout = false;
  long timer_init;
  long timer;
  uint8_t state = 0;
  uint8_t index = 0;

  MAC = "";
  timer_init = millis();
  while (!timeout) {
    timer = millis();
    if (((timer - timer_init) / 1000) > 5) // Timeout?
      timeout = true;
    if (Serial.available()) {
      c2 = c1;
      c1 = Serial.read();
      //Serialprint(c1);
      switch (state) {
        case 0:
          if (c1 == ':')
            state = 1;
          break;
        case 1:
          if (c1 == '\r') {
            MAC.toUpperCase();
            state = 2;
          }
          else {
            if ((c1 != '"') && (c1 != ':'))
              MAC += c1;  // Uppercase
          }
          break;
        case 2:
          if ((c2 == 'O') && (c1 == 'K')) {
            //Serialprintln();
            Serial.flush();
            return 1;  // Ok
          }
          break;
      } // end switch
    } // Serial_available
  } // while (!timeout)
  //Serialprintln("!Timeout!");
  Serial.flush();
  return -1;  // timeout
}

int ESPsendCommand(char *command, String stopstr, int timeout_secs)
{
  Serial.println(command);
  ESPwait(stopstr, timeout_secs);
  delay(250);
}
