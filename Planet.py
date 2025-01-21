import math
import sys
import numpy as np
from PIL import Image
from pathlib import Path

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *


class Planet:
    radius = 20
    def __init__(self, radius):
        self.angle = None
        self.radius = radius

    def compute_normals(self):
        self.normals = np.zeros((self.N, self.N, 3))  # Tablica na normalne
        for i in range(self.N):
            for j in range(self.N):
                # Punkt na powierzchni jajka
                x, y, z = self.tab[i, j]

                # Normalizacja wektora normalnego (prosty wektor skierowany na zewnątrz)
                length = np.sqrt(x ** 2 + y ** 2 + z ** 2)
                self.normals[i, j] = [x / length, y / length, z / length]

    def generate_sphere(self):
        N = 20
        center = [0.0, 0.0, 0.0]

        tab = np.zeros((N, N, 3))
        texture = np.zeros((N, N, 2))

        ul = np.linspace(0.0, 0.5, N)
        vl = np.linspace(0.0, 2.0, N)

        ut = np.linspace(0.0, 1.0, N)
        vt = np.linspace(0.0, 1.0, N)

        for j, u in enumerate(ul):
            for i, v in enumerate(vl):
                theta = 2 * math.pi * u  # azimuthal angle
                phi = math.pi * v  # polar angle
                x = math.sin(phi) * math.cos(theta)
                y = math.sin(phi) * math.sin(theta)
                z = math.cos(phi)
                tab[i, j] = [x, y, z]
                texture[j, i] = [ut[i], vt[j]]

        glFrontFace(GL_CW)
        glBegin(GL_TRIANGLES)
        for j in range(1, N):
            for i in range(1, N):
                v1 = tab[i - 1, j - 1]
                v2 = tab[i, j - 1]
                v3 = tab[i, j]
                v4 = tab[i - 1, j]

                glColor3f(1.0, 1.0, 1.0)  # white
                # glNormal3f(*normal1)
                glTexCoord2f(*texture[i - 1, j - 1])  # Współrzędne tekstury dla v1
                glVertex3f(*v1)
                glTexCoord2f(*texture[i, j - 1])  # Współrzędne tekstury dla v2
                glVertex3f(*v2)
                glTexCoord2f(*texture[i, j])  # Współrzędne tekstury dla v3
                glVertex3f(*v3)

                # Drugi trójkąt
                glColor3f(1.0, 1.0, 1.0)  # white
                # glNormal3f(*normal2)
                glTexCoord2f(*texture[i - 1, j - 1])  # Współrzędne tekstury dla v1
                glVertex3f(*v1)
                glTexCoord2f(*texture[i, j])  # Współrzędne tekstury dla v3
                glVertex3f(*v3)
                glTexCoord2f(*texture[i - 1, j])  # Współrzędne tekstury dla v4
                glVertex3f(*v4)
        glEnd()

    def rotate(self, angular_velocity, delta_time):
        self.angle += angular_velocity * delta_time  # Update rotation angle
        self.angle %= 360  # Keep the angle within the range [0, 360]

    def render(self):
        glPushMatrix()
        glRotatef(self.angle, 0.0, 1.0, 0.0)  # Rotate around the Y-axis
        self.generate_sphere()
        glPopMatrix()