import math
import sys
import numpy as np
from PIL import Image
from pathlib import Path

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *


class Planet:
    N = 26
    tab = np.array([])
    texture = np.zeros((N, N, 2))
    normals = np.zeros((N, N, 3))  # Tablica na przechowywanie normalnych

    def __init__(self, radius, size, tilt_angle, orbit_radius, orbit_speed, orbit_angle, texture_name, scale_distance, scale_size):
        self.angle = 0
        self.size = size * scale_size  # Skalowany rozmiar planety
        self.radius = radius * scale_size  # Skalowany promień planety
        self.tilt_angle = tilt_angle
        self.orbit_radius = orbit_radius * scale_distance  # Skalowana odległość orbitalna
        self.orbit_angle = orbit_angle
        self.orbit_speed = orbit_speed
        self.texture_name = texture_name
        self.generate_sphere()
        self.generate_normals()  # Generowanie normalnych raz na początku

    def calculate_normal(self, v1, v2, v3):
        u = np.subtract(v2, v1)
        v = np.subtract(v3, v1)
        normal = np.cross(u, v)
        norm = np.linalg.norm(normal)
        if norm == 0:
            return normal
        return normal / norm

    def generate_sphere(self):
        self.tab = np.zeros((self.N, self.N, 3))

        ul = np.linspace(0.0, 0.5, self.N)
        vl = np.linspace(0.0, 2.0, self.N)

        ut = np.linspace(0.0, 1.0, self.N)
        vt = np.linspace(0.0, 1.0, self.N)

        for j, v in enumerate(vl):
            for i, u in enumerate(ul):
                theta = 2 * math.pi * u  # Azimuthal angle
                phi = math.pi * v  # Polar angle
                x = self.size * math.sin(phi) * math.cos(theta)
                y = self.size * math.sin(phi) * math.sin(theta)
                z = self.size * math.cos(phi)
                self.tab[i, j] = [x, y, z]
                self.texture[j, i] = [ut[j], vt[i]]

    def generate_normals(self):
        """Generowanie normalnych dla wszystkich punktów na sferze."""
        for j in range(1, self.N):
            for i in range(1, self.N):
                v1 = self.tab[i - 1, j - 1]
                v2 = self.tab[i, j - 1]
                v3 = self.tab[i, j]
                v4 = self.tab[i - 1, j]

                normal1 = self.calculate_normal(v1, v2, v3)
                normal2 = self.calculate_normal(v1, v3, v4)

                # Zapisujemy normalne dla odpowiednich punktów
                self.normals[i - 1, j - 1] = normal1
                self.normals[i - 1, j] = normal2

    def draw(self):
        glFrontFace(GL_CW)

        texture_image = Image.open(self.texture_name)
        glTexImage2D(
            GL_TEXTURE_2D, 0, 3, texture_image.size[0], texture_image.size[1], 0,
            GL_RGB, GL_UNSIGNED_BYTE, texture_image.tobytes("raw", "RGB", 0, -1)
        )

        glBegin(GL_TRIANGLES)
        for j in range(1, self.N):
            for i in range(1, self.N):
                v1 = self.tab[i - 1, j - 1]
                v2 = self.tab[i, j - 1]
                v3 = self.tab[i, j]
                v4 = self.tab[i - 1, j]

                normal1 = self.normals[i - 1, j - 1]  # Odczyt z predefiniowanej tablicy
                normal2 = self.normals[i - 1, j]  # Odczyt z predefiniowanej tablicy

                glColor3f(1.0, 1.0, 1.0)  # White
                glNormal3f(*normal1)
                glTexCoord2f(*self.texture[i - 1, j - 1])  # Texture coordinates for v1
                glVertex3f(*v1)
                glTexCoord2f(*self.texture[i, j - 1])  # Texture coordinates for v2
                glVertex3f(*v2)
                glTexCoord2f(*self.texture[i, j])  # Texture coordinates for v3
                glVertex3f(*v3)

                # Second triangle
                glColor3f(1.0, 1.0, 1.0)  # White
                glNormal3f(*normal2)
                glTexCoord2f(*self.texture[i - 1, j - 1])  # Texture coordinates for v1
                glVertex3f(*v1)
                glTexCoord2f(*self.texture[i, j])  # Texture coordinates for v3
                glVertex3f(*v3)
                glTexCoord2f(*self.texture[i - 1, j])  # Texture coordinates for v4
                glVertex3f(*v4)
        glEnd()

    def rotate(self, angular_velocity, delta_time):
        self.angle += angular_velocity * delta_time
        self.angle %= 360

    def update_orbit(self, delta_time):
        self.orbit_angle += self.orbit_speed * delta_time
        self.orbit_angle %= 360

    def render(self):
        glPushMatrix()

        x = self.orbit_radius * math.cos(math.radians(self.orbit_angle))
        z = self.orbit_radius * math.sin(math.radians(self.orbit_angle))

        glTranslatef(x, 0.0, z)
        glRotatef(self.tilt_angle, 1.0, 0.0, 0.0)
        glRotatef(self.angle, 0.0, 1.0, 0.0)

        self.draw()
        glPopMatrix()