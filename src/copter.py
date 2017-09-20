from rectangular import Rectangular
import numpy as np

class Copter(Rectangular):
    def __init__(self, position, size):
        Rectangular.__init__(self, position, size, size)
        self.velocity = np.array([[10.0],[0.0]])
        self.exploded = False
        self.firing = False

    def step(self, level, gravity, fire_force, delta_time):
        acceleration = gravity + fire_force
        self.velocity += acceleration * delta_time
        self.position += self.velocity * delta_time
        if self.exploded:
            self.velocity *= 0.97
        if level.collides_with(self):
            return False
        return True



