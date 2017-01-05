#include <Arduino.h>

// ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
//  Based on: JJROBOTS AIR HOCKEY ROBOT EVO PROJECT

// Robot Moves depends directly on robot status
// robot status:
//   0: Go to defense position 
//   5: Manual mode => User send direct commands to robot
//   9: Manual mode IceQueen => User send direct commands to robot
void robotStrategy()
{
  max_speed = user_max_speed;  // default to max robot speed and accel
  max_acceleration = user_max_accel;

  switch (robot_status) {

    case 5: // EVO manual mode
      setPosition_straight(user_target_x, user_target_y);
      break;

    case 9: // IceQueen manual mode
      position_M1 = (robotCoordX + robotCoordY) * X_AXIS_STEPS_PER_UNIT;
      position_M2 = (robotCoordX - robotCoordY) * Y_AXIS_STEPS_PER_UNIT;
      setPosition_straight(user_target_x, user_target_y);
      break;

    default:
      Serial.println("\"La estupidez humana siempre vencera\' a la inteligencia artificial\"-TerryPratchett");
      break;
  }
}

// Test sequence to check mechanics, motor drivers...
void testMovements()
{
  if (loop_counter >= 9000) {
    testmode = false;
    return;
  }
  max_speed = user_max_speed;
  if (loop_counter > 8000)
    setPosition_straight(200, 60);
  else if (loop_counter > 6260)
    setPosition_straight(100, 200);
  else if (loop_counter > 6000)
    setPosition_straight(320, 200);
  else if (loop_counter > 5000)
    setPosition_straight(200, 60);
  else if (loop_counter > 3250)
    setPosition_straight(300, 280);
  else if (loop_counter > 3000)
    setPosition_straight(200, 280);
  else if (loop_counter > 2500)
    setPosition_straight(200, 60);
  else if (loop_counter > 1500)
    setPosition_straight(200, 300);
  else
    setPosition_straight(200, 60);
}
