import math
import sys
import time

import numpy as np
from PIL import Image
from pathlib import Path
from Planet import *

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

N = 17


# Skalowany promień Słońca

radius = 5.0
center = [0.0, 0.0, 0.0]
latitude = 0.0
longitude = 0.0
t = 0.0
s = 0.0
current_x = 0.0
current_y = 0.0
current_z = 0.0
next_x = 0.0
next_y = 0.0
next_z = 0.0
movement_speed = 2.0
rotation_speed = 2.0

planets = []

SCALE_SIZE = 1.0  # Bazowy rozmiar Ziemi
SCALE_DISTANCE = 1.0  # Bazowa odległość Ziemi
sun_radius = 8.0
BASE_RADIUS = 4.0  # Odległość Merkurego
TIME_SCALE = 525600  # Jeden rok w symulacji trwa 1 minutę
# Słońce


angular_velocity = 10.0

left_mouse_button_pressed = 0
right_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
mouse_z_pos_old = 0
delta_x = 0
delta_y = 0
cam_radius = 20.0
camera_position = np.array([0.0, 0.0, 50.0])
camera_angle = np.array([0.0, 0.0])
upv = [0.0, 1.0, 0.0]

last_time = time.time()

def calculate_delta_time():
    global last_time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time  # Update the last frame's time
    return delta_time

def shutdown():
    pass



def startup():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    update_viewport(None, 1000, 1000)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_CULL_FACE)
    glFrontFace(GL_CCW)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)



def axes():
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0) #red x-axis
    glVertex3f(-50.0, 0.0, 0.0)
    glVertex3f(50.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0) #green y-axis
    glVertex3f(0.0, -50.0, 0.0)
    glVertex3f(0.0, 50.0, 0.0)

    glColor3f(0.0, 0.0, 1.0) #blue z-axis
    glVertex3f(0.0, 0.0, -50.0)
    glVertex3f(0.0, 0.0, 50.0)

    glEnd()

def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global mouse_x_pos_old
    global delta_y
    global mouse_y_pos_old
    if left_mouse_button_pressed == 1:
        delta_x += (x_pos - mouse_x_pos_old) * 0.005
        mouse_x_pos_old = x_pos

        delta_y += (y_pos - mouse_y_pos_old) * 0.005
        mouse_y_pos_old = y_pos

def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed
    global right_mouse_button_pressed
    global mouse_x_pos_old, mouse_y_pos_old

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
        mouse_x_pos_old, mouse_y_pos_old = glfwGetCursorPos(window)
    else:
        left_mouse_button_pressed = 0

    if button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        right_mouse_button_pressed = 1
    else:
        right_mouse_button_pressed = 0

def keyboard_key_callback(window, key, scancode, action, mods):
    global camera_position, camera_angle, movement_speed, TIME_SCALE
    if action == GLFW_PRESS or action == GLFW_REPEAT:
        pass
    if key == GLFW_KEY_W:
        camera_position[2] -= movement_speed
    elif key == GLFW_KEY_S:
        camera_position[2] += movement_speed
    elif key == GLFW_KEY_A:
        camera_position[0] -= movement_speed
    elif key == GLFW_KEY_D:
        camera_position[0] += movement_speed
    elif key == GLFW_KEY_R:
        camera_position[1] += movement_speed
    elif key == GLFW_KEY_F:
        camera_position[1] -= movement_speed
    elif key == GLFW_KEY_UP:
        camera_angle[1] += rotation_speed
    elif key == GLFW_KEY_DOWN:
        camera_angle[1] -= rotation_speed
    elif key == GLFW_KEY_LEFT:
        camera_angle[0] -= rotation_speed
    elif key == GLFW_KEY_RIGHT:
        camera_angle[0] += rotation_speed
    elif key == GLFW_KEY_0: #real time
        TIME_SCALE = 1
    elif key == GLFW_KEY_1: #base time
        TIME_SCALE = 525600
    elif key == GLFW_KEY_2: #accelerate
        TIME_SCALE += (525600/2)
    elif key == GLFW_KEY_3: #decelerate
        TIME_SCALE -= (525600/2)
    elif key == GLFW_KEY_4: #accelerate*2
        TIME_SCALE *= 2
    elif key == GLFW_KEY_5: #accelerate/2
        TIME_SCALE /= 2


def scroll_callback(window, xoffset, yoffset):
    global cam_radius
    if -195 <= cam_radius <= 195:
        cam_radius -= yoffset
    if cam_radius < -195:
        cam_radius = -195
    if cam_radius > 195:
        cam_radius = 195

def render(time):
    global delta_x, delta_y, cam_radius, camera_position, upv, center, radius, camera_position
    delta_time = calculate_delta_time()  # Compute time elapsed since the last frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    target = np.array([camera_position[0] + np.sin(np.radians(camera_angle[0])),camera_position[1] + np.sin(np.radians(camera_angle[1])),camera_position[2] - np.cos(np.radians(camera_angle[0]))])

    glLoadIdentity()
    gluLookAt(camera_position[0], camera_position[1], camera_position[2],target[0], target[1], target[2],0.0, 1.0, 0.0)
    axes()


    for planet in planets:
        planet.update_orbit(delta_time)
        planet.rotate(delta_time)
        planet.draw_orbit()
        planet.changeTimeScaling(TIME_SCALE)
        planet.render()

    glfwSwapBuffers(glfwGetCurrentContext())
    glFlush()

def update_viewport(window, width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.01, 3000.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    global planets, TIME_SCALE

    print("Zmiana pozycji przy pomocy WSAD, zaś w górę i w dół przy pomocy RF")
    print("Zmiana kąta patrzenia przy pomocy strzałek")
    print("")
    print("Czas rzeczywisty obrotu - 0")
    print("Czas roku ziemskiego w minutę - 1")
    print("Przyspieszenie liniowe - 2")
    print("Opóźnienie liniowe - 3")
    print("Większe przyśpieszenie - 4")
    print("Większe opóźnienie - 5")

    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(800, 800, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow(b"GLUT Solar System")

    glfwMakeContextCurrent(window)
    # glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSetScrollCallback(window, scroll_callback)
    glEnable(GL_COLOR_MATERIAL)

    minimal_ambient = [0.0, 0.0, 0.0, 1.0]  # Brak światła otoczenia
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, minimal_ambient)

    glfwSwapInterval(1)


    planets = [
        Planet(sun_radius, 8.0, 0, 0, 0, 0, "textures/2k_sun.jpg", SCALE_DISTANCE, SCALE_SIZE,0.0,0,1, TIME_SCALE, True),
        Planet(sun_radius + 0.4, 0.4, 0.0, sun_radius + 4.0, 5.0, 0, "textures/2k_mercury.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.205,58.6,88.0,TIME_SCALE),  # Merkury
        Planet(sun_radius + 0.9, 0.9, 177.4, sun_radius + 7.5, 3.0, 0, "textures/2k_venus_surface.jpg", SCALE_DISTANCE, SCALE_SIZE,0.007,243,224.7,TIME_SCALE),  # Wenus
        Planet(sun_radius + 1.0, 1.0, 23.5, sun_radius + 10.3, 2.5, 0, "textures/2k_earth_daymap.jpg", SCALE_DISTANCE, SCALE_SIZE,0.017,1,365.25,TIME_SCALE),  # Ziemia
        Planet(sun_radius + 0.5, 0.5, 25.2, sun_radius + 15.0, 2.0, 0, "textures/2k_mars.jpg", SCALE_DISTANCE, SCALE_SIZE,0.093, 1.03,687.0,TIME_SCALE),  # Mars
        Planet(sun_radius + 2.0, 2.0, 3.1, sun_radius + 30.0, 1.0, 0, "textures/2k_jupiter.jpg", SCALE_DISTANCE, SCALE_SIZE,0.049, 0.41, 4331.6, TIME_SCALE),  # Jowisz
        Planet(sun_radius + 1.5, 1.5, 26.7, sun_radius + 50.0, 0.7, 0, "textures/2k_saturn.jpg", SCALE_DISTANCE, SCALE_SIZE,0.056, 0.45,10.75,TIME_SCALE),  # Saturn
        Planet(sun_radius + 1.0, 1.0, 97.8, sun_radius + 70.0, 0.5, 0, "textures/2k_uranus.jpg", SCALE_DISTANCE, SCALE_SIZE,0.046,0.72,30,TIME_SCALE),  # Uran
        Planet(sun_radius + 1.0, 1.0, 28.3, sun_radius + 90.0, 0.3, 0, "textures/2k_neptune.jpg", SCALE_DISTANCE, SCALE_SIZE,0.010, 0.67, 60, TIME_SCALE),  # Neptun
    ]

    startup()

    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()

if __name__ == '__main__':

    main()
