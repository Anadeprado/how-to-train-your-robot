// ICE-QUEEN ROBOT: Q-Learning AirHockey ROBOT
//  Based on: JJROBOTS AIR HOCKEY ROBOT EVO PROJECT

// USER CONFIGURATIONS HERE
// ROBOT DIMENSIONS, MAX SPEED, MAX ACCELERATION, CALIBRATION...

//#define DEBUG

// ABSOLUTE MAX ROBOT SPEED AND ACCELERATION
// THIS VALUES DEPENDS ON YOUR ROBOT CONSTRUCTION (MOTORS, MECHANICS...)
// RECOMMENDED VALUES FOR 12V POWER SUPPLY
#define MAX_ACCEL 275           // Maximun motor acceleration in (steps/seg2)/1000. Max recommended value:280
#define MAX_SPEED 32000         // Maximun speed in steps/seg. Max absolute value: 32767!!

#define MIN_ACCEL 100//100
#define MIN_SPEED 5000//5000
#define SCURVE_LOW_SPEED 2500
#define SCURVE_HIGH_SPEED 28000

// Geometric calibration.
// This depends on the pulley teeth. DEFAULT: 200(steps/rev)*8(microstepping) = 1600 steps/rev. 1600/32teeth*2mm(GT2) = 25 steps/mm
#define X_AXIS_STEPS_PER_UNIT 25
#define Y_AXIS_STEPS_PER_UNIT 25

// This is the center of the table. All units in milimeters
// This are the dimensions of the official air hockey table Exploter from Buffalo
#define TABLE_LENGTH 710
#define TABLE_WIDTH 400

// # Numero de sectores en la matriz. Normalmente [7x4]
// # NIVEL-> 0     1     2     3     4     5     6
// #     .-----.-----.-----.-----.-----.-----.-----.--> X
// #   0 |     |     |     |     |     |     |     |
// #     |     |  R  |     |     |     |     |     |
// #     .-----.-----.-----.-----.-----.-----.-----.
// #   1 |  R  |     |     |     |     |     |     |
// #     |     |     |     |     |     |  D  |     |
// #     .-----.-----.-----.-----.-----.-----.-----.
// #   2 |     |     |     |  D  |  D  |     |  D  |
// #     |     |     |     |     |     |     |     |
// #     .-----.-----.-----.-----.-----.-----.-----.
// #   3 |     |     |     |     |     |     |     |
// #     |     |     |     |     |     |     |     |
// #     .-----.-----.-----.-----.-----.-----.-----.
// #     |
// #    Y
// #
// NUM_SEC_X = 7
// NUM_SEC_Y = 4
// SEC_SIZ = 100 #Tamaño sectores

// # Posiciones límites robot: (0,0)-->(3,3)
// #   Ejemplo: nunca pise nivel 4, ni 5, ni 6...

// Absolute Min and Max robot positions in mm (measured from center of robot pusher)
#define ROBOT_MIN_X 50
#define ROBOT_MIN_Y 50
#define ROBOT_MAX_X 350
#define ROBOT_MAX_Y 350

// Initial robot position in mm
// The robot must be at this position at start time
// Default: Centered in X and minimun position in Y
#define ROBOT_INITIAL_POSITION_X 150
#define ROBOT_INITIAL_POSITION_Y 150

// PACKET SIZE (UDP MESSAGE)
#define PACKET_SIZE 12  // UDP PACKET SIZE (without sync mark), total size = PACKET_SIZE+3(sync mark)

// Utils (don´t modify)
#define CLR(x,y) (x&=(~(1<<y)))
#define SET(x,y) (x|=(1<<y))

#define RAD2GRAD 57.2957795
#define GRAD2RAD 0.01745329251994329576923690768489

#define ZERO_SPEED 65535
