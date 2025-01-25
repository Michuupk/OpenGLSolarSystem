import math
import sys
import numpy as np
from PIL import Image
from pathlib import Path

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Planet:
    N = 26
    tab = np.array([])
    texture = np.zeros((N, N, 2))

    def __init__(self, radius, size, tilt_angle, orbit_radius, orbit_speed, orbit_angle, texture_name, scale_distance, scale_size, eccentricity ,day_length ,year_length):
        self.angle = 0
        self.size = size * scale_size
        self.radius = radius * scale_size
        self.tilt_angle = tilt_angle
        self.orbit_radius = orbit_radius * scale_distance  # Wielka półoś (a)
        self.orbit_speed = orbit_speed
        self.orbit_angle = orbit_angle  # Początkowy kąt orbity
        self.eccentricity = eccentricity  # Ekscentryczność (e)
        self.texture_name = texture_name
        self.texture_id = self.load_texture(texture_name)
        self.day_length = day_length  # Czas obrotu planety wokół osi (dni)
        self.year_length = year_length  # Czas obiegu planety wokół Słońca (dni)

    def draw_orbit(self):
        a = self.orbit_radius  # Wielka półoś
        b = a * math.sqrt(1 - self.eccentricity ** 2)  # Mała półoś
        c = a * self.eccentricity  # Odległość środka elipsy od ogniska
        segments = 100  # Liczba segmentów, które przybliżą elipsę

        glColor3f(0.5, 0.5, 0.5)  # Kolor orbity (szary)
        glBegin(GL_LINE_LOOP)  # Rozpocznij rysowanie linii

        for i in range(segments):
            theta = 2.0 * math.pi * i / segments  # Podziel elipsę na segmenty
            x = a * math.cos(theta) - c  # Przesunięcie względem ogniska
            z = b * math.sin(theta)
            glVertex3f(x, 0.0, z)  # Rysuj punkt orbity w płaszczyźnie XZ

        glEnd()  # Zakończ rysowanie linii

    def load_texture(self, texture_name):
        try:
            # Load the texture image using PIL
            img = Image.open(texture_name).transpose(Image.FLIP_TOP_BOTTOM)  # Flip vertically for OpenGL
            img_data = np.array(img, dtype=np.uint8)

            # Generate a texture ID and bind it
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)

            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            # Upload the texture to OpenGL
            if img.mode == "RGB":
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            elif img.mode == "RGBA":
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            else:
                raise ValueError(f"Unsupported image mode: {img.mode}")

            return texture_id
        except Exception as e:
            print(f"Error loading texture {texture_name}: {e}")
            return None

    def rotate(self, delta_time):
        rotations_per_year = self.year_length / self.day_length

        # Prędkość obrotowa planety
        angular_velocity = rotations_per_year * 360.0  # Stopnie na rok


        self.angle += angular_velocity * delta_time / self.year_length
        self.angle %= 360  # Ogranicz kąt do zakresu [0, 360]

    def update_orbit(self, delta_time):
        if self.orbit_radius == 0:  # Jeśli planeta nie ma orbity (np. Słońce)
            return

        velocity = self.calculate_velocity()  # Prędkość orbitalna w km/s
        r = self.get_current_distance()  # AU -> metry

        if r == 0 or velocity == 0:  # Unikaj dzielenia przez 0
            print(f"Skipping update_orbit for {self.texture_name} due to zero r or velocity")
            return

        # Uwzględnij skalowanie prędkości orbitalnej


        angular_velocity = velocity * 1000 / r  # radian/s
        self.orbit_angle += math.degrees(angular_velocity * delta_time)  # Dodaj zmianę kąta
        self.orbit_angle %= 360  # Zawijanie kąta w przedziale [0, 360]



    def calculate_velocity(self):
        G = 6.67430e-11  # Stała grawitacyjna w jednostkach SI
        M_sun = 1.989e30  # Masa Słońca [kg]
        scale_mass = 0.000002  # Współczynnik skalowania masy Słońca


        # Zastosowanie współczynnika skalowania
        M_scaled = M_sun * scale_mass

        # Aktualna odległość od Słońca (r) w metrach
        r = self.get_current_distance() * 1.496e11  # AU -> metry

        if r == 0:  # Jeśli odległość jest zerowa, np. dla Słońca
            return 0

        # Prędkość w m/s
        v = (G * M_scaled / r) ** 0.5

        # Prędkość w km/s
        return v / 1000

    def get_current_distance(self):
        a = self.orbit_radius
        e = self.eccentricity
        theta = math.radians(self.orbit_angle)

        r = a * (1 - e ** 2) / (1 + e * math.cos(theta))

        print(f"get_current_distance: a={a:.2f}, e={e:.2f}, theta={math.degrees(theta):.2f}, r={r:.2f}")
        return r

    def render(self):
        glPushMatrix()

        try:
            # Oblicz pozycję na elipsie
            theta = math.radians(self.orbit_angle)
            a = self.orbit_radius
            b = a * math.sqrt(1 - self.eccentricity ** 2)
            c = a * self.eccentricity
            x = a * math.cos(theta) - c
            z = b * math.sin(theta)

            glTranslatef(x, 0.0, z)

            # Rotacja planety
            glRotatef(self.tilt_angle, 1.0, 0.0, 0.0)
            glRotatef(self.angle, 0.0, 1.0, 0.0)
            glColor3f(1.0, 1.0, 1.0)

            glScalef(self.size, self.size, self.size)

            # Teksturowanie i rysowanie
            if self.texture_id and glIsTexture(self.texture_id):
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)

            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluQuadricTexture(quadric, GL_TRUE)
            gluSphere(quadric, 1.0, self.N, self.N)
            gluDeleteQuadric(quadric)

            # Debugowanie prędkości
            velocity = self.calculate_velocity()
            print(f"Prędkość planety ({self.texture_name}): {velocity:.2f} km/s")

        except Exception as e:
            print(f"Error during rendering: {e}")

        finally:
            if self.texture_id and glIsTexture(self.texture_id):
                glDisable(GL_TEXTURE_2D)

            glPopMatrix()
            glutSwapBuffers()