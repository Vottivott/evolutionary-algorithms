import pickle
import os

def save_population_data(subfoldername, population_data, keep_last_n=None, keep_mod = 100):
    directory_path = "../saved_populations/" + subfoldername + "/"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    if keep_last_n:
        files = os.listdir(directory_path)
        for filename in files:
            num = int(filename[:-4])
            diff = population_data.generation - num
            if diff >= keep_last_n and not (keep_mod is not None and num % keep_mod == 0):
                os.remove(directory_path + filename)
    with open(directory_path + str(population_data.generation) + ".pkl", 'w') as out:
        pickle.dump(population_data, out)


def load_population_data(subfoldername, generation):
    directory_path = "../saved_populations/" + subfoldername + "/"
    if generation == -1:
        file_loaded = False
        if not os.path.exists(directory_path):
            return None
        files = os.listdir(directory_path)
        if not len(files):
            return None
        nums = (int(file[:-4]) for file in files)
        nums = sorted(nums)
        generation = nums[-1]
        print "Loading latest generation of " + str(subfoldername) + ": " + str(generation)
        while 1:
            try:
                with open(directory_path + str(generation) + ".pkl") as file:
                    return pickle.load(file)
            except ValueError:
                old = nums[-1]
                del nums[-1]
                if len(nums) == 0:
                    print "No file left to try! Returning None"
                    return None
                else:
                    generation = nums[-1]
                    print "ValueError on " + str(old) + ", trying with " + str(generation) + " instead!"
    else:
        with open(directory_path + str(generation) + ".pkl") as file:
            return pickle.load(file)


if __name__ == "__main__":
    import numpy as np
    #subfoldername = "7 counters (length 4), 15 radars (max_steps = 250, step_size = 4), velocity up+down"
    subfoldername = "enemy"
    p = load_population_data(subfoldername, -1)
    print sum(p.population[40][-1500:])
    print sum(sum(ind[-1500:] for ind in p.population))
    subfoldername = "copter"
    p = load_population_data(subfoldername, -1)
    print sum(p.population[40][-1500:])
    print sum(sum(ind[-1500:] for ind in p.population))
    # p = load_population_data(subfoldername, 105)
    # print p
    # p = load_population_data(subfoldername, 106)
    # print p
    # p.generation += 1
    # save_population_data(subfoldername, p)
    # print p
    # num_extra_genes = 30 * 50
    # for i,chromosome in enumerate(p.population):
    #     initial_h = np.zeros((num_extra_genes,1))
    #     p.population[i] = np.vstack((chromosome, initial_h))
    # print p
    # save_population_data(subfoldername, p)
    # print "Finished!"