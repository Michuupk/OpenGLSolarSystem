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


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *



# Constants and global variables
movement_speed = 4.0
TIME_SCALE = 525600  # One year in simulation equals one minute in real-time
camera_position = np.array([0.0, 0.0, 50.0])
camera_angle = np.array([0.0, 0.0])

last_time = time.time()
planets = []
SCALE_SIZE = 1.0
SCALE_DISTANCE = 1.0
sun_radius = 8.0


def calculate_delta_time():
    """Calculate time elapsed since the last frame."""
    global last_time
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    return delta_time


def startup():
    """Initialize OpenGL settings."""
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_CULL_FACE)
    glFrontFace(GL_CCW)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_TEXTURE_2D)


def axes():
    """Render axes for reference."""
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)  # X-axis (red)
    glVertex3f(-50.0, 0.0, 0.0)
    glVertex3f(50.0, 0.0, 0.0)
    glColor3f(0.0, 1.0, 0.0)  # Y-axis (green)
    glVertex3f(0.0, -50.0, 0.0)
    glVertex3f(0.0, 50.0, 0.0)
    glColor3f(0.0, 0.0, 1.0)  # Z-axis (blue)
    glVertex3f(0.0, 0.0, -50.0)
    glVertex3f(0.0, 0.0, 50.0)
    glEnd()


def update_viewport(width, height):
    """Update the OpenGL viewport."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, width / height, 0.01, 3000.0)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def keyboard_key_callback(key, x, y):
    """Handle keyboard input for camera movement and time scaling."""
    global camera_position, TIME_SCALE

    if key == b'w':  # Move forward
        camera_position[2] -= movement_speed
    elif key == b's':  # Move backward
        camera_position[2] += movement_speed
    elif key == b'a':  # Move left
        camera_position[0] -= movement_speed
    elif key == b'd':  # Move right
        camera_position[0] += movement_speed
    elif key == b'r':  # Move up
        camera_position[1] += movement_speed
    elif key == b'f':  # Move down
        camera_position[1] -= movement_speed
    elif key == b'\033':  # ESC key to exit
        sys.exit(0)
    elif key == b'0':  # Real-time scale
        TIME_SCALE = 1
    elif key == b'1':  # Base time scale
        TIME_SCALE = 525600
    elif key == b'2':  # Accelerate
        TIME_SCALE += 262800
    elif key == b'3':  # Decelerate
        TIME_SCALE -= 262800
    elif key == b'4':  # Double speed
        TIME_SCALE *= 2
    elif key == b'5':  # Halve speed
        TIME_SCALE /= 2


def render():
    """Main render loop."""
    global planets, camera_position, camera_angle, TIME_SCALE

    delta_time = calculate_delta_time()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Camera target
    target = np.array([
        camera_position[0] + math.sin(math.radians(camera_angle[0])),
        camera_position[1],
        camera_position[2] - math.cos(math.radians(camera_angle[0]))
    ])

    # Set camera view
    glLoadIdentity()
    gluLookAt(camera_position[0], camera_position[1], camera_position[2], target[0], target[1], target[2], 0.0, 1.0, 0.0)

    # Render axes and planets
    axes()
    for planet in planets:
        planet.update_orbit(delta_time)
        planet.rotate(delta_time)
        planet.draw_orbit()
        planet.changeTimeScaling(TIME_SCALE)
        planet.render()

    glutSwapBuffers()


def main():
    """Initialize GLUT and start the main loop."""
    global planets

    # Initialize GLUT
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"GLUT Solar System")

    # Register callbacks
    glutKeyboardFunc(keyboard_key_callback)
    glutDisplayFunc(render)
    glutReshapeFunc(update_viewport)
    glutIdleFunc(render)

    # OpenGL setup
    startup()

    # Define planets
    planets = [
        Planet(sun_radius, 8.0, 0, 0, 0, 0, "textures/2k_sun.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.0, 0, 1, TIME_SCALE, True),
        Planet(sun_radius + 0.4, 0.4, 0.0, sun_radius + 4.0, 5.0, 0, "textures/2k_mercury.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.205, 58.6, 88.0, TIME_SCALE),
        Planet(sun_radius + 0.9, 0.9, 177.4, sun_radius + 7.5, 3.0, 0, "textures/2k_venus_surface.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.007, 243, 224.7, TIME_SCALE),
        Planet(sun_radius + 1.0, 1.0, 23.5, sun_radius + 10.3, 2.5, 0, "textures/2k_earth_daymap.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.017, 1, 365.25, TIME_SCALE),
        Planet(sun_radius + 0.5, 0.5, 25.2, sun_radius + 15.0, 2.0, 0, "textures/2k_mars.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.093, 1.03, 687.0, TIME_SCALE),
        Planet(sun_radius + 2.0, 2.0, 3.1, sun_radius + 30.0, 1.0, 0, "textures/2k_jupiter.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.049, 0.41, 4331.6, TIME_SCALE),
        Planet(sun_radius + 1.5, 1.5, 26.7, sun_radius + 50.0, 0.7, 0, "textures/2k_saturn.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.056, 0.45, 10759, TIME_SCALE),
        Planet(sun_radius + 1.0, 1.0, 97.8, sun_radius + 70.0, 0.5, 0, "textures/2k_uranus.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.046, 0.72, 30685, TIME_SCALE),
        Planet(sun_radius + 1.0, 1.0, 28.3, sun_radius + 90.0, 0.3, 0, "textures/2k_neptune.jpg", SCALE_DISTANCE, SCALE_SIZE, 0.010, 0.67, 60190, TIME_SCALE),
    ]

    # Start main loop
    glutMainLoop()


if __name__ == "__main__":
    main()