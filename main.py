import math
import sys
import numpy as np
from PIL import Image
from pathlib import Path

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *


radius = 3.0
center = [0.0, 0.0, 0.0]
latitude = 0.0
longitude = 0.0
current_x = 0.0
current_y = 0.0
current_z = 0.0
next_x = 0.0
next_y = 0.0
next_z = 0.0

def shutdown():
    pass

def startup():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    update_viewport(None, 800, 800)


def sphere():
    global latitude, longitude, current_x, current_y, current_z, next_x, next_y, next_z

    current_x = center[0] + radius
    current_y = center[1]
    current_z = center[2]


    glBegin(GL_POINTS)
    for latitude in np.linspace(0, 2 * np.pi, 100):
        for longitude in np.linspace(0, np.pi, 100):
            next_x = radius * math.cos(latitude) * math.sin(longitude) + center[0]
            next_y = radius * math.sin(latitude) * math.sin(longitude) + center[1]
            next_z = radius * math.cos(longitude) + center[2]
            glVertex3f(current_x, current_y, current_z)
            glVertex3f(next_x, next_y, next_z)
        current_x = next_x
        current_y = next_y

    glEnd()

def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
    sphere()

    glFlush()

def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 360.0 / width
    
    if height == 0:
        height = 1
    if width == 0:
        width = 1
    aspectRatio = width / height
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    gluPerspective(90, 1.0, 0.1, 100.0)
    glViewport(0, 0, width, height)

    if width <= height:
        glOrtho(-10, 10, -10 / aspectRatio, 10 / aspectRatio, 10, -10)
    else:
        glOrtho(-10 * aspectRatio, 10 * aspectRatio, -10, 10, 10, -10)
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
    # glfwSetCursorPosCallback(window, mouse_motion_callback)
    # glfwSetMouseButtonCallback(window, mouse_button_callback)
    # glfwSetScrollCallback(window, scroll_callback)

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
