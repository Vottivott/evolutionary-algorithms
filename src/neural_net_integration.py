from enemy import Enemy
from neural_network import NeuralNetwork
import numpy as np

from recurrent_neural_network import RecurrentNeuralNetwork


class NeuralNetIntegration:
    def __init__(self, layer_sizes, input_function, output_function, recurrent=False):
        """
        :param layer_sizes: the sizes of the layers in a feed-forward neural network
        :param input_function: function that takes a copter_simulation and an enemy_index (or None for main copter) and returns the input to the network
        :param output_function: function that takes the output of the network and the copter_simulation and an enemy_index (or None for main copter) and modifies the copter_simulation accordingly
        """
        self.recurrent = recurrent
        if recurrent:
            self.neural_network = RecurrentNeuralNetwork(layer_sizes)
        else:
            self.neural_network = NeuralNetwork(layer_sizes)
        self.input_function = input_function
        self.output_function = output_function

    def run_network(self, copter_simulation, enemy_index=None, custom_h_layer=None):
        if enemy_index is None and custom_h_layer is not None: # enemy matrix
            network_output = self.neural_network.run_multiple([self.input_function(copter_simulation, i) for i in range(len(custom_h_layer))],
                                                     custom_h_layer)
            self.output_function(network_output, copter_simulation, enemy_index)
        else:
            network_output = self.neural_network.run(self.input_function(copter_simulation, enemy_index), custom_h_layer)
            self.output_function(network_output, copter_simulation, enemy_index)

    # def clear_h(self):
    #     self.neural_network.h = self.get_empty_h()

    def initialize_h(self):
        self.neural_network.h = self.get_initial_h()

    # def set_custom_h_layer(self, h):
    #     self.neural_network.set_custom_h_layer(h)

    def set_weights_and_possibly_initial_h(self, variables):
        num_weights = self.neural_network.number_of_weights
        if len(variables) > num_weights:
            self.set_weights_and_initial_h(variables[:num_weights], variables[num_weights:])
        else:
            print "No initial h encoded in the chromosome, initializing to all zeros."
            self.neural_network.initial_h = self.get_all_zeros_h_vector()
            self.set_weights(variables)


    def set_weights(self, weights):
        self.neural_network.set_weights_from_single_vector(weights)
        if self.recurrent:
            self.neural_network.h = [None] + [np.zeros((size, 1)) for size in self.neural_network.layer_sizes[1:-1]] # Reset state vectors
        else:
            print "NOT RECURRENT!"

    def set_weights_and_initial_h(self, weights, initial_h):
        self.neural_network.set_weights_from_single_vector(weights)
        self.neural_network.initial_h = initial_h
        # TODO: Add support for multiple layers
        if self.recurrent:
            if len(self.neural_network.layer_sizes) > 3:
                print "MORE THAN ONE HIDDEN LAYER NOT SUPPORTED YET, BUT EASY TO FIX!"
            self.neural_network.h = [None, np.copy(self.neural_network.initial_h)] # Reset state vectors
        else:
            print "NOT RECURRENT!"

    def get_all_zeros_h_vector(self):
        return np.zeros((self.neural_network.layer_sizes[1], 1))

    def get_initial_h(self):
        return [None, np.copy(self.neural_network.initial_h)]#[None] + [np.zeros(h.shape) for h in self.neural_network.h[1:-1]]


    def get_number_of_variables(self):
        return self.neural_network.get_total_number_of_weights() + self.neural_network.get_h_size()

def evocopter_neural_net_integration(copter_simulation):

    enemy_radar_size = copter_simulation.radar_system.enemy_radar.number_of_neurons

    input_layer_size = 0
    input_layer_size += copter_simulation.radar_system.num_front_radars
    input_layer_size += copter_simulation.radar_system.num_back_radars
    input_layer_size += 2 # velocity in up-direction + velocity in down-direction
    input_layer_size += 2 # velocity in left-direction + velocity in right-direction
    input_layer_size += enemy_radar_size

    middle_layer_size = 50

    output_layer_size = 2

    layer_sizes = (input_layer_size, middle_layer_size, output_layer_size)


    def evocopter_input_function(sim, enemy_index):
        yvel = np.asscalar(sim.copter.velocity[1])
        if yvel <= 0:
            velocity_up = -yvel / sim.copter.max_y_velocity
            velocity_down = 0
        else:
            velocity_up = 0
            velocity_down = yvel / sim.copter.max_y_velocity
        velocity_inputs = np.array([[velocity_up], [velocity_down]])

        xvel = np.asscalar(sim.copter.velocity[0])
        if xvel <= 0:
            velocity_left = -xvel / sim.copter.max_x_velocity
            velocity_right = 0
        else:
            velocity_left = 0
            velocity_right = xvel / sim.copter.max_x_velocity
        x_velocity_inputs = np.array([[velocity_left], [velocity_right]])

        enemy_radar = sim.radar_system.enemy_radar
        position = sim.copter.position
        enemies = sim.get_living_enemy_instances()
        enemy_dist_vec = enemy_radar.read_dist_vector(position, enemies, sim.level)

        dist_inputs = np.array([[radar.read(sim.copter.position, sim.level)[1]] for radar in sim.radar_system.radars])

        input = np.vstack((velocity_inputs, dist_inputs, enemy_dist_vec, x_velocity_inputs))
        # print input
        assert len(input) == input_layer_size
        return input

    def evocopter_output_function(network_output, sim, enemy_index):
        should_fire = network_output[0] > 0.5
        sim.copter.firing = should_fire
        if network_output[1] > 0.5:
            sim.copter_shoot()
        # print should_fire

    return NeuralNetIntegration(layer_sizes, evocopter_input_function, evocopter_output_function, recurrent=True)

def black_neural_net_integration(copter_simulation):
    input_layer_size = 0
    input_layer_size += copter_simulation.enemys_radar_system.num_front_radars
    input_layer_size += copter_simulation.enemys_radar_system.num_back_radars
    input_layer_size += copter_simulation.enemys_radar_system.copter_radar.number_of_neurons
    input_layer_size += copter_simulation.enemys_radar_system.shot_radar.number_of_neurons
    input_layer_size += copter_simulation.enemys_radar_system.enemy_radar.number_of_neurons
    input_layer_size += 2 # velocity in up-direction + velocity in down-direction
    input_layer_size += 1 # velocity in left-direction

    middle_layer_size = 50

    output_layer_size = 3

    layer_sizes = (input_layer_size, middle_layer_size, output_layer_size)

    def enemy_input_function(sim, enemy_index):
        return np.hstack(enemy_input_function_single(sim, i) for i in range(len(sim.get_neural_enemy_indices())))

    def enemy_input_function_single(sim, enemy_index):
        enemy = sim.enemy_instances[enemy_index].enemy
        yvel = np.asscalar(enemy.velocity[1])
        if yvel <= 0:
            velocity_up = -yvel / Enemy.max_y_velocity
            velocity_down = 0
        else:
            velocity_up = 0
            velocity_down = yvel / Enemy.max_y_velocity
        xvel = np.asscalar(enemy.velocity[0])
        velocity_left = -xvel / Enemy.max_x_velocity
        velocity_inputs = np.array([[velocity_up], [velocity_down], [velocity_left]])

        shot_radar = sim.enemys_radar_system.shot_radar
        copter_radar = sim.enemys_radar_system.copter_radar
        position = enemy.position
        shots = sim.shots
        copters = sim.get_living_copter_list()

        enemy_radar = sim.enemys_radar_system.enemy_radar
        other_enemies = sim.get_living_enemy_instances(enemy_index)

        shot_dist_vec = shot_radar.read_dist_vector(position, shots, sim.level)
        copter_dist_vec = copter_radar.read_dist_vector(position, copters, sim.level)
        enemy_dist_vec = enemy_radar.read_dist_vector(position, other_enemies, sim.level)



        dist_inputs = np.array([[radar.read(position, sim.level)[1]] for radar in sim.enemys_radar_system.radars])

        input = np.vstack((velocity_inputs, dist_inputs, shot_dist_vec, enemy_dist_vec, copter_dist_vec))
        # print input
        assert len(input) == input_layer_size
        return input

    # def enemy_output_function_old(network_output, sim, enemy_index):
    #     enemy = sim.enemy_instances[enemy_index].enemy
    #     # print network_output[:3]
    #     should_fire = network_output[0] > 0.5
    #     moving_left = network_output[1] > 0.5
    #     diving = network_output[2] > 0.5
    #     enemy.firing = should_fire
    #     enemy.moving_left = moving_left
    #     enemy.diving = diving
    #     if diving:
    #         enemy.dive()

            # print should_fire

    def enemy_output_function(network_output, sim, enemy_index):
        enemies = [ei.enemy for ei in sim.get_living_enemies(sim.user_control)]
        # print network_output[:3]
        should_fire = network_output[0,:] > 0.5
        moving_left = network_output[1,:] > 0.5
        diving = network_output[2,:] > 0.5
        for i,enemy in enumerate(enemies):
            enemy.firing = should_fire[i]
            enemy.moving_left = moving_left[i]
            enemy.diving = diving[i]
            if diving[i]:
                enemy.dive()

        # print should_fire

    return NeuralNetIntegration(layer_sizes, enemy_input_function, enemy_output_function, recurrent=True)


