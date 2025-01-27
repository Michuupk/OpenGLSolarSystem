import math
import sys
import numpy as np
from PIL import Image
from pathlib import Path


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Planet:
    N = 26
    tab = np.array([])
    texture = np.zeros((N, N, 2))

    def __init__(self, radius, size, tilt_angle, orbit_radius, orbit_speed, orbit_angle, texture_name, scale_distance, scale_size, eccentricity ,day_length ,year_length, scale_global,light_transparent = False ):
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
        self.scale_global = scale_global  # Globalny współczynnik skalowania
        self.light_transparent = light_transparent

    def changeTimeScaling(self, TIME_SCALE):
        self.scale_global = TIME_SCALE


    def draw_orbit(self):

        a = self.orbit_radius  # Wielka półoś
        b = a * math.sqrt(1 - self.eccentricity ** 2)  # Mała półoś
        c = a * self.eccentricity  # Odległość środka elipsy od ogniska
        segments = 100  # Liczba segmentów, które przybliżą elipsę

        glColor3f(0.5, 0.5, 0.5)  # Kolor orbity (szary)
        # Ustawienie materiału, aby obiekt nie reagował na światło
        no_light_material = [0.0, 0.0, 0.0, 1.0]  # Brak odbicia światła

        # Wyłącz komponenty materiału dla tego obiektu
        glMaterialfv(GL_FRONT, GL_DIFFUSE, no_light_material)  # Brak odbicia rozproszonego
        glMaterialfv(GL_FRONT, GL_SPECULAR, no_light_material)  # Brak odbicia specularnego
        glMaterialfv(GL_FRONT, GL_AMBIENT, no_light_material)  # Brak odbicia specularnego
        glMaterialfv(GL_FRONT, GL_EMISSION, no_light_material)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 0)

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
        if self.day_length == 0:  # Unikaj dzielenia przez 0 (np. dla Słońca)
            return

        # Prędkość obrotu planety (liczba obrotów na dzień symulacyjny)
        rotations_per_day = 1 / self.day_length
        angular_velocity = rotations_per_day * 360.0  # Stopnie na dzień

        # Uwzględnij globalne skalowanie czasu
        angular_velocity *= self.scale_global

        # Przeliczenie delta_time na dni
        delta_time_days = delta_time / 86400  # Sekundy na dni
        self.angle += angular_velocity * delta_time_days
        self.angle %= 360

        #print(
         #   f"rotate: angle={self.angle:.2f}, angular_velocity={angular_velocity:.6f}, delta_time_days={delta_time_days:.6f}")

    def update_orbit(self, delta_time):
        if self.orbit_radius == 0:  # Jeśli to Słońce, nie wykonuj obliczeń
            return

        # Średnia prędkość orbitalna w jednostkach symulacyjnych (np. AU/dzień)
        velocity = self.calculate_velocity()

        if velocity == 0:
            return

        # Przeliczenie delta_time na dni, uwzględniając scale_global
        delta_time_days = (delta_time / 86400) * self.scale_global

        orbit_circumference = 2 * math.pi * self.orbit_radius
        angular_change = (velocity / orbit_circumference) * 360  # W stopniach

        self.orbit_angle += angular_change * delta_time_days
        self.orbit_angle %= 360  # Zawijanie kąta w zakresie [0, 360]

        #print(
#            f"update_orbit: orbit_angle={self.orbit_angle:.2f}, angular_change={angular_change:.6f}, delta_time_days={delta_time_days:.6f}")

    def calculate_velocity(self):
        # Wielka i mała półoś
        a = self.orbit_radius  # Wielka półoś (skalowana)
        b = a * math.sqrt(1 - self.eccentricity ** 2)  # Mała półoś

        # Przybliżona długość orbity
        orbit_length = 2 * math.pi * math.sqrt((a ** 2 + b ** 2) / 2)
        #print("orbit: ",orbit_length)

        # Średnia prędkość orbitalna (długość orbity / czas obiegu w dniach)
        # Prędkość zwrócona jest w jednostkach symulacyjnych na dzień
        average_velocity = orbit_length / self.year_length

        return average_velocity

    def get_current_distance(self):
        a = self.orbit_radius
        e = self.eccentricity
        theta = math.radians(self.orbit_angle)

        r = a * (1 - e ** 2) / (1 + e * math.cos(theta))

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

            if self.light_transparent:
                # Ustaw planetę jako źródło światła (GL_LIGHT0)
                light_position = [0.0, 0.0, 0.0, 1.0]  # W centrum światło punktowe (w każdą stronę)
                light_diffuse = [1.5, 1.5, 1.2, 1.0]  # Bardzo jasne światło
                light_specular = [1.2, 1.2, 1.2, 1.0]  # Jasne odbicie specularne
                light_ambient = [0.1, 0.1, 0.1, 1.0]  # Subtelne światło otoczenia

                glEnable(GL_LIGHTING)
                glEnable(GL_LIGHT0)  # Słońce jako GL_LIGHT0
                glLightfv(GL_LIGHT0, GL_POSITION, light_position)
                glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
                glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
                glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)

            else:


                diffuse_reflection = [1.0, 1.0, 1.0, 1.0]  # Maksymalne odbicie dyfuzyjne (biały kolor)
                specular_reflection = [1.0, 1.0, 1.0, 1.0]  # Maksymalne odbicie specularne (biały kolor)
                ambient_reflection = [0, 0, 0, 0]  # Maksymalne światło otoczenia (biały kolor)
                shininess = 128.0  # Wysoki połysk (wartość maksymalna)

                # Zastosowanie do materiału
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, diffuse_reflection)
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular_reflection)
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient_reflection)
                glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)


            # Teksturowanie i rysowanie
            if self.texture_id and glIsTexture(self.texture_id):
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)

            if self.day_length == 0:
                glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 0.0, 1.0]) # Jasnożółta emisja słońca
            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluQuadricTexture(quadric, GL_TRUE)
            gluSphere(quadric, 1.0, self.N, self.N)
            gluDeleteQuadric(quadric)
            if self.day_length == 0:
                glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

            # Debugowanie prędkości
            velocity = self.calculate_velocity()
            #print(f"Prędkość planety ({self.texture_name}): {velocity:.2f} km/s")

        except Exception as e:
            print(f"Error during rendering: {e}")

        finally:
            if self.texture_id and glIsTexture(self.texture_id):
                glDisable(GL_TEXTURE_2D)

            if self.light_transparent:
                glDisable(GL_BLEND)  # Wyłącz blending po renderowaniu przezroczystej planety

            glPopMatrix()