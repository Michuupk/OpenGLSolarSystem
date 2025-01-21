import math
import sys
import numpy as np
from PIL import Image
from pathlib import Path
from Planet import *

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

N = 17

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

p = Planet(radius)

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

def shutdown():
    pass

def startup():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    update_viewport(None, 800, 800)

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

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
    p.render()


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
