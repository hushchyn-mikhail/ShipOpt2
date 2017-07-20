import numpy as np
import pandas as pd
import GPy
import GPyOpt
import os
import sys
import getopt

from objective import objective
from feasible_region import space, constraints

if __name__=='__main__':
    
    argv = sys.argv[1:]

    msg = '''Runs sampling of new points.\n\
    Usage:\n\
      python run_newPointsCalculation.py [options] \n\
    Example: \n\
      python RunPR.py -m "Baseline" -n 10
    Options:
      -n  --number                  : Number of new sampled points:
                                    : Default is 1
      -m  --method                  : Name of a track pattern recognition method: 'Baseline', 'FH', 'AR', 'R'
                                    : Default is 'Baseline'
      -h  --help                    : Shows this help
      '''
    
    try:
        opts, args = getopt.getopt(argv, "hm:n:",
                                   ["help", "method=", "number="])
    except getopt.GetoptError:
        print "Wrong options were used. Please, read the following help:\n"
        print msg
        sys.exit(2)
        
    method = 'Baseline'
    number = 1
    
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print msg
            sys.exit()
        elif opt in ("-m", "--method"):
            method = arg
        elif opt in ("-n", "--number"):
            number = arg
    
    if 'observations.csv' in os.listdir('.'):
        observations = pd.read_csv('observations.csv')
    else:
        observations = pd.DataFrame(columns=['num', 'pitch', 'yoffset_layer', 'yoffset_plane', 'zshift_layer',\
                                             'zshift_plane', 'zshift_view', 'angle', 'objective'])
    
    feasible_region = GPyOpt.Design_space(space=space, constraints=constraints)
    
    for num_i in range(number):
        
        obj = GPyOpt.core.task.SingleObjective(objective)
        model = GPyOpt.models.GPModel(exact_feval=True, optimize_restarts=10, verbose=False)
        aquisition_optimizer = GPyOpt.optimization.AcquisitionOptimizer(feasible_region)
        acquisition = GPyOpt.acquisitions.AcquisitionEI(model, feasible_region, optimizer=aquisition_optimizer)
        evaluator = GPyOpt.core.evaluators.Sequential(acquisition)
        
        design = observations[observations.columns[1:-1]].values
        answers = observations[observations.columns[-1:]].values
        design = design[~np.isnan(answers.ravel())]
        answers = answers[~np.isnan(answers.ravel())]
        bo = GPyOpt.methods.ModularBayesianOptimization(model, space, obj, acquisition, evaluator, design, answers)
        new_point = bo.suggested_sample[0]
        value = objective(*tuple(new_point))
        observations.loc[len(observations)] = [len(observations)] + list(new_point) + [value]
        observations.to_csv('observations.csv', index=False)