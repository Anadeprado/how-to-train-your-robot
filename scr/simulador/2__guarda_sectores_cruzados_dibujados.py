import cv2
import numpy as np


#-------------------------------
# Variable que guarda los sectores cruzados
crossedSectors = []

# Numero de sectores en la matriz. Normalmente 7x5
#   ______Y
#   |
#   |
#  X
num_secX = 7
num_secY = 5

# Tamannos maximos de la matriz
sizeX = num_secX*100
sizeY = num_secY*100

drawing = False # true if mouse is pressed
new_tray = False # new trajectory

# Mouse position in pintaBALL window
ix,iy = -1,-1

# Actual sector
actual_sector = (-1,-1)

# Creamos unas imagenes vacias (de ceros)
pintaBALL = np.zeros((sizeX,sizeY,3), np.uint8)
pintaTRAY = np.zeros((sizeX,sizeY,3), np.uint8)

# Creamos ventanas
cv2.namedWindow('pintaBALL')
cv2.namedWindow('pintaTRAY')
cv2.moveWindow('pintaBALL',0,0)
cv2.moveWindow('pintaTRAY',700,0)

#-------------------------------



# Mouse callback function
#-------------------------------
def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing, new_tray, crossedSectors

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        new_tray = True

    elif event == cv2.EVENT_MOUSEMOVE:
        ix,iy = x,y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        print ('Sectores cruzados en la trayectoria = %d' % len(crossedSectors))
        print crossedSectors

#---------------------------------------------
# Annadimos la funcion del raton a esa ventana:
cv2.setMouseCallback('pintaBALL',draw_circle)
#---------------------------------------------


# Sector Lines function
#-------------------------------
def draw_sector_lines(imgg):

    # Draw lines with thickness of 'tt' px and color 'cc'
    tt = 1
    cc = (200,200,200)

    # Vertical lines...
    for i in range(1,num_secY):
        cv2.line(imgg,(i*100,0),(i*100,sizeX),cc,tt)

    # Horizontal lines...
    for i in range(1,num_secX):
        cv2.line(imgg,(0,i*100),(sizeY,i*100),cc,tt)



# Colored crossed sectors function
#-------------------------------
def colored_crossed_sectors(imggg):
    global actual_sector

    cro_secX = actual_sector[0]
    cro_secY = actual_sector[1]

    # Draw rectangles and color 'cc'
    ini = (cro_secX*100, cro_secY*100)
    fin = (cro_secX*100 + 100, cro_secY*100 + 100)

    cc = (200,255,200)

    cv2.rectangle(imggg,ini,fin,cc,-1)

# Update actual sector position function :
#-----------------------------------------------
def update_actual_sector_position():
    global actual_sector, ix, iy

    #Si no te has salido de la matriz:
    if (0<ix<sizeX) & (0<iy<sizeY):
        actualX = ix // 100
        actualY = iy // 100

        #Si el sector ha cambiado, actualiza la variable y sennala nuevo sector
        if (actual_sector[0] is not actualX) or (actual_sector[1] is not actualY):
            actual_sector = (actualX,actualY)
            return True

        else:
            return False

    else:
        return False



# Programa Principal:
#---------------------------------------------
while(1):


    # Imagen pintaBALL: Borramos imagen cada vez y pintamos la pelotita
    # ---------------
    pintaBALL = np.zeros((sizeX,sizeY,3), np.uint8)
    cv2.circle(pintaBALL,(ix,iy),10,(0,0,255),-1)

    draw_sector_lines(pintaBALL)
    cv2.imshow('pintaBALL', pintaBALL)



    # Imagen pintaTRAY: no borramos a menos q vuelvas a pulsar, pintamos encima
    # ---------------
    if new_tray is True:
        # Borramos la trayectoria anterior y los sectores
        pintaTRAY = np.zeros((sizeX,sizeY,3), np.uint8)
        crossedSectors = []
        new_tray = False

    if drawing == True:
        new_sector = update_actual_sector_position()
        if new_sector:
            #Pintamos y annadimos el nuevo sector
            colored_crossed_sectors(pintaTRAY)
            crossedSectors.append(actual_sector)

        cv2.circle(pintaTRAY,(ix,iy),2,(0,255,0),2)

    draw_sector_lines(pintaTRAY)
    cv2.imshow('pintaTRAY',pintaTRAY)



    # Pulsar 'Q' para SALIR o 'M' para cambiar modo
    k = cv2.waitKey(1) & 0xFF
    if k == ord('m'):
        mode = not mode
    elif k == 27 or k == ord('q'):  # Pulsar 'Q' o ESC para SALIR
        break


cv2.destroyAllWindows()
