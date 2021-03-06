import numpy as np

from radar import Radar, ObjectRadar


class RadarSystem:
    def __init__(self):
        max_steps = 250
        step_size = 4
        self.num_front_radars = 15
        directions = np.linspace(-3.0*np.pi/7, 3.0*np.pi/7, self.num_front_radars)
        self.radars = [Radar(dir, max_steps, step_size) for dir in directions]
        max_steps = 250
        step_size = -4
        self.num_back_radars = 7
        directions = np.linspace(np.pi - 3.0 * np.pi / 7, np.pi + 3.0 * np.pi / 7, self.num_back_radars)
        self.radars.extend([Radar(dir, max_steps, step_size) for dir in directions])

        number_of_neurons = 20
        x_step_size = 4
        max_num_steps = 100
        max_dist = 1000
        only_left_half = False
        self.enemy_radar = ObjectRadar(number_of_neurons, x_step_size, max_num_steps, max_dist, only_left_half)



class EnemysRadarSystem:
    def __init__(self):
        max_steps = 250
        step_size = -4
        self.num_front_radars = 15
        directions = np.linspace(-3.0*np.pi/7, 3.0*np.pi/7, self.num_front_radars)
        self.radars = [Radar(dir, max_steps, step_size) for dir in directions]
        max_steps = 250
        step_size = 4
        self.num_back_radars = 7
        directions = np.linspace(np.pi - 3.0 * np.pi / 7, np.pi + 3.0 * np.pi / 7, self.num_back_radars)
        self.radars.extend([Radar(dir, max_steps, step_size) for dir in directions])

        number_of_neurons = 10
        x_step_size = 4
        max_num_steps = 100
        max_dist = 1000
        only_left_half = True
        self.copter_radar = ObjectRadar(number_of_neurons, x_step_size, max_num_steps, max_dist, only_left_half)

        number_of_neurons = 10
        x_step_size = 4
        max_num_steps = 100
        max_dist = 800
        only_left_half = True
        self.shot_radar = ObjectRadar(number_of_neurons, x_step_size, max_num_steps, max_dist, only_left_half)

        number_of_neurons = 20
        x_step_size = 4
        max_num_steps = 100
        max_dist = 1000
        only_left_half = False
        self.enemy_radar = ObjectRadar(number_of_neurons, x_step_size, max_num_steps, max_dist, only_left_half) # for detecting other enemies
