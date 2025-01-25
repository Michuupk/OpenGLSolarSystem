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

    def __init__(self, radius, size, tilt_angle, orbit_radius, orbit_speed, orbit_angle, texture_name, scale_distance, scale_size):
        self.angle = 0
        self.size = size * scale_size  # Skalowany rozmiar planety
        self.radius = radius * scale_size  # Skalowany promień planety
        self.tilt_angle = tilt_angle
        self.orbit_radius = orbit_radius * scale_distance  # Skalowana odległość orbitalna
        self.orbit_angle = orbit_angle
        self.orbit_speed = orbit_speed
        self.texture_name = texture_name
        self.texture_id = self.load_texture(texture_name)

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

    def rotate(self, angular_velocity, delta_time):
        self.angle += angular_velocity * delta_time
        self.angle %= 360

    def update_orbit(self, delta_time):
        self.orbit_angle += self.orbit_speed * delta_time
        self.orbit_angle %= 360

    def render(self):
        glPushMatrix()

        try:
            # Calculate orbital position
            x = self.orbit_radius * math.cos(math.radians(self.orbit_angle))
            z = self.orbit_radius * math.sin(math.radians(self.orbit_angle))
            glTranslatef(x, 0.0, z)

            # Planet rotation and tilt
            glRotatef(self.tilt_angle, 1.0, 0.0, 0.0)
            glRotatef(self.angle, 0.0, 1.0, 0.0)
            glColor3f(1.0, 1.0, 1.0)

            # Scale the planet
            glScalef(self.size, self.size, self.size)

            # Enable and bind texture if valid
            if self.texture_id and glIsTexture(self.texture_id):
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)

            # Draw the planet
            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluQuadricTexture(quadric, GL_TRUE)
            gluSphere(quadric, 1.0, self.N, self.N)
            gluDeleteQuadric(quadric)

        except Exception as e:
            print(f"Error during rendering: {e}")

        finally:
            if self.texture_id and glIsTexture(self.texture_id):
                glDisable(GL_TEXTURE_2D)

            glPopMatrix()
            glutSwapBuffers()