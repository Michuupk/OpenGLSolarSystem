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

SCALE_SIZE = 1.0  # Bazowy rozmiar Ziemi
SCALE_DISTANCE = 1.0  # Bazowa odległość Ziemi
sun_radius = 8.0

# Słońce
sun = Planet(
    radius=sun_radius,  # Słońce około 8 razy większe od Ziemi
    size=8.0,  # Rozmiar Słońca
    tilt_angle=0,  # Brak nachylenia
    orbit_radius=0,  # Słońce w centrum
    orbit_speed=0,  # Słońce nieruchome
    orbit_angle=0,
    texture_name="textures/2k_sun.jpg",
    scale_distance=SCALE_DISTANCE,
    scale_size=SCALE_SIZE
)

planets = [
    # Planet(sun_radius + 0.4, 0.4, 0.0, sun_radius + 4.0, 5.0, 0, "textures/2k_mercury.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Merkury
    # Planet(sun_radius + 0.9, 0.9, 177.4, sun_radius + 7.0, 3.0, 0, "textures/2k_venus_surface", SCALE_DISTANCE, SCALE_SIZE),  # Wenus
    Planet(sun_radius + 1.0, 1.0, 23.5, sun_radius + 10.0, 2.5, 0, "textures/2k_earth_daymap.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Ziemia
    # Planet(sun_radius + 0.5, 0.5, 25.2, sun_radius + 15.0, 2.0, 0, "textures/2k_mars.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Mars
    # Planet(sun_radius + 2.0, 2.0, 3.1, sun_radius + 30.0, 1.0, 0, "textures/2k_jupiter.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Jowisz
    # Planet(sun_radius + 1.5, 1.5, 26.7, sun_radius + 50.0, 0.7, 0, "textures/2k_saturn.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Saturn
    # Planet(sun_radius + 1.0, 1.0, 97.8, sun_radius + 70.0, 0.5, 0, "textures/2k_uranus.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Uran
    # Planet(sun_radius + 1.0, 1.0, 28.3, sun_radius + 90.0, 0.3, 0, "textures/2k_neptune.jpg", SCALE_DISTANCE, SCALE_SIZE),  # Neptun
]

angular_velocity = 10.0

left_mouse_button_pressed = 0
right_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
mouse_z_pos_old = 0
delta_x = 0
delta_y = 0
cam_radius = 0.0
camera_position = [1.0, 0.0, 0.0]
upv = [0.0, 1.0, 0.0]

last_time = time.time()

def calculate_delta_time():
    global last_time
    current_time = time.time()
    delta_time = current_time - last_time  # Time difference between frames
    last_time = current_time  # Update the last frame's time
    return delta_time

def shutdown():
    pass

def startup():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    update_viewport(None, 1000, 1000)

    glEnable(GL_DEPTH_TEST)
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

def scroll_callback(window, xoffset, yoffset):
    global cam_radius
    if -45 <= cam_radius <= 45:
        cam_radius -= yoffset
    if cam_radius < -45:
        cam_radius = -45
    if cam_radius > 45:
        cam_radius = 45

def render(time):
    global delta_x, delta_y, cam_radius, camera_position, upv, center, radius
    delta_time = calculate_delta_time()  # Compute time elapsed since the last frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    if left_mouse_button_pressed:
        camera_position[0] = math.cos(delta_y) * math.cos(delta_x)
        camera_position[1] = math.sin(delta_y)
        camera_position[2] = math.cos(delta_y) * math.sin(delta_x)

        upv[0] = -math.cos(delta_x) * math.sin(delta_y)
        upv[1] = math.cos(delta_y)
        upv[2] = -math.sin(delta_x) * math.sin(delta_y)

        up_length = math.sqrt(upv[0]**2 + upv[1]**2 + upv[2]**2)
        upv[0] /= up_length/2
        upv[1] /= up_length/2
        upv[2] /= up_length/2
        
    else:
        cam_radius = cam_radius
        upv[0] = upv[0]
        upv[1] = upv[1]
        upv[2] = upv[2]
        camera_position[0] = camera_position[0]
        camera_position[1] = camera_position[1]
        camera_position[2] = camera_position[2]

    glLoadIdentity()
    gluLookAt(camera_position[0] * cam_radius,camera_position[1] * cam_radius,camera_position[2] * cam_radius, 0.0, 0.0, 0.0, upv[0], upv[1], upv[2])
    
    axes()

    sun.render()

    for planet in planets:
        planet.update_orbit(delta_time)
        planet.rotate(angular_velocity, delta_time)
        planet.render()


    glFlush()

def update_viewport(window, width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(800, 800, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    # glfwSetFramebufferSizeCallback(window, update_viewport)
    # glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSetScrollCallback(window, scroll_callback)

    glfwSwapInterval(1)
    

    startup()

    while not glfwWindowShouldClose(window):

        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()

if __name__ == '__main__':
    main()
