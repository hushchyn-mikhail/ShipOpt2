import os
import GPyOpt
import numpy as np

from feasible_region import space, constraints

feasible_region = GPyOpt.Design_space(space=space, constraints=constraints)

np.random.seed(7)
initial_design = GPyOpt.util.stats.initial_design('random', feasible_region, 5)

ShipOpt = str(os.getenv('SHIPOPT'))
np.save(ShipOpt+'/observations/initial_design.npy', initial_design)