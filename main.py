import math
import sys
import time
import numpy as np
from PIL import Image
from pathlib import Path
from Planet import *  # Assuming the Planet class is already defined

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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
movement_speed = 4.0
rotation_speed = 3.0

planets = []

SCALE_SIZE = 1.0  # Bazowy rozmiar Ziemi
SCALE_DISTANCE = 1.0  # Bazowa odległość Ziemi
sun_radius = 8.0
BASE_RADIUS = 4.0  # Odległość Merkurego
TIME_SCALE = 525600  # Jeden rok w symulacji trwa 1 minutę

# Słońce
angular_velocity = 10.0

# Global variables for camera control
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
    update_viewport(800, 800)

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
    glColor3f(1.0, 0.0, 0.0)  # red x-axis
    glVertex3f(-50.0, 0.0, 0.0)
    glVertex3f(50.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)  # green y-axis
    glVertex3f(0.0, -50.0, 0.0)
    glVertex3f(0.0, 50.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)  # blue z-axis
    glVertex3f(0.0, 0.0, -50.0)
    glVertex3f(0.0, 0.0, 50.0)

    glEnd()


def keyboard_key_callback(key, x, y):
    global camera_position, camera_angle, movement_speed, TIME_SCALE
    if key == b'w':
        camera_position[2] -= movement_speed
    elif key == b's':
        camera_position[2] += movement_speed
    elif key == b'a':
        camera_position[0] -= movement_speed
    elif key == b'd':
        camera_position[0] += movement_speed
    elif key == b'r':
        camera_position[1] += movement_speed
    elif key == b'f':
        camera_position[1] -= movement_speed
    elif key == b'k':
        camera_angle[1] -= rotation_speed
    elif key == b'i':
        camera_angle[1] += rotation_speed
    elif key == b'l':
        camera_angle[0] += rotation_speed
    elif key == b'j':
        camera_angle[0] -= rotation_speed
    elif key == b'\033':  # ESC key
        sys.exit(0)
    elif key == b'0':  # real time
        TIME_SCALE = 1
    elif key == b'1':  # base time
        TIME_SCALE = 525600
    elif key == b'2':  # accelerate
        TIME_SCALE += (525600 / 2)
    elif key == b'3':  # decelerate
        TIME_SCALE -= (525600 / 2)
    elif key == b'4':  # accelerate*2
        TIME_SCALE *= 2
    elif key == b'5':  # accelerate/2
        TIME_SCALE /= 2


def render():
    global delta_x, delta_y, cam_radius, camera_position, upv, center, radius, camera_position
    delta_time = calculate_delta_time()  # Compute time elapsed since the last frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    target = np.array([camera_position[0] + np.sin(np.radians(camera_angle[0])),
                       camera_position[1] + np.sin(np.radians(camera_angle[1])),
                       camera_position[2] - np.cos(np.radians(camera_angle[0]))])

    glLoadIdentity()
    gluLookAt(camera_position[0], camera_position[1], camera_position[2], target[0], target[1], target[2], 0.0, 1.0,
              0.0)
    axes()
    for planet in planets:
        planet.update_orbit(delta_time)
        planet.rotate(delta_time)
        planet.draw_orbit()
        planet.changeTimeScaling(TIME_SCALE)
        planet.render()

    glutSwapBuffers()
    glFlush()


def update_viewport(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.01, 3000.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glutSwapBuffers()


def main():
    global planets, TIME_SCALE

    print("Zmiana pozycji przy pomocy WSAD, zaś w górę i w dół przy pomocy RF")
    print("Zmiana kąta patrzenia przy pomocy ikjl")
    print("")

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"GLUT Solar System")

    glutKeyboardFunc(keyboard_key_callback)
    glutDisplayFunc(render)
    glutIdleFunc(render)  # Continuously render when idle
    glutReshapeFunc(update_viewport)

    startup()
    planets = [
        Planet(sun_radius, 8.0, 0, 0, 0, 0, "textures/2k_sun.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.0, 0, 1, TIME_SCALE,
               True),
        Planet(sun_radius + 0.4, 0.4, 0.0, sun_radius + 4.0, 5.0, 0, "textures/2k_mercury.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.205, 58.6, 88.0, TIME_SCALE),  # Merkury
        Planet(sun_radius + 0.9, 0.9, 177.4, sun_radius + 7.5, 3.0, 0, "textures/2k_venus_surface.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.007, 243, 224.7, TIME_SCALE),  # Wenus
        Planet(sun_radius + 1.0, 1.0, 23.5, sun_radius + 10.3, 2.5, 0, "textures/2k_earth_daymap.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.017, 1, 365.25, TIME_SCALE),  # Ziemia
        Planet(sun_radius + 0.5, 0.5, 25.2, sun_radius + 15.0, 2.0, 0, "textures/2k_mars.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.093, 1.03, 687.0, TIME_SCALE),  # Mars
        Planet(sun_radius + 2.0, 2.0, 3.1, sun_radius + 30.0, 1.0, 0, "textures/2k_jupiter.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.049, 0.41, 4331.6, TIME_SCALE),  # Jowisz
        Planet(sun_radius + 1.5, 1.5, 26.7, sun_radius + 50.0, 0.7, 0, "textures/2k_saturn.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.056, 0.45, 10.75, TIME_SCALE),  # Saturn
        Planet(sun_radius + 1.0, 1.0, 97.8, sun_radius + 70.0, 0.5, 0, "textures/2k_uranus.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.046, 0.72, 30, TIME_SCALE),  # Uran
        Planet(sun_radius + 1.0, 1.0, 28.3, sun_radius + 90.0, 0.3, 0, "textures/2k_neptune.jpg", SCALE_DISTANCE,
               SCALE_SIZE, 0.010, 0.67, 60, TIME_SCALE),  # Neptun
    ]

    glutSwapBuffers()

    glutMainLoop()


if __name__ == '__main__':
    main()
