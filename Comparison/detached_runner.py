import GPyOpt
import GPy
import numpy as np
import pandas as pd
import re
import json
import sys
import getopt
import os.path

sys.path.append("../../devel/")

from binomial_optimization import expected_improvement, expected_improvement_approx, fidelity_decision

min_dist = 3.6
radius = 2

space = [{'name': 'pitch', 'type': 'continuous', 'domain': (min_dist, min_dist)},\
         {'name': 'yoffset_layer', 'type': 'continuous', 'domain': (min_dist/2, min_dist)},\
         {'name': 'yoffset_plane', 'type': 'continuous', 'domain': (min_dist*0.25, min_dist*1.25)},\
         {'name': 'zshift_layer', 'type': 'continuous', 'domain': (1, 12)},\
         {'name': 'zshift_plane', 'type': 'continuous', 'domain': (1, 12)},\
         {'name': 'zshift_view', 'type': 'continuous', 'domain': (10, 12)},\
         {'name': 'alpha', 'type': 'continuous', 'domain': (5, 15)}]

constraints = [{'name': 'constr_1', 'constrain': '-(x[:,0]-x[:,1])**2-x[:,3]**2+'+str(radius)+'**2'},\
               {'name': 'constr_2', 'constrain': '-(x[:,1]-x[:,2])**2-(x[:,3]-x[:,4])**2+'+str(radius)+'**2'},\
               {'name': 'constr_3', 'constrain': 'x[:,3]+x[:,4]+'+str(radius)+'-x[:,5]'},
               {'name': 'constr_4', 'constrain': 'x[:,3]+'+str(radius)+'-x[:,4]'}]

feasible_region = GPyOpt.Design_space(space=space, constraints=constraints)

np.random.seed(7)

import time
import json

from disneylandClient import (
    new_client,
    Job,
    RequestWithId,
)

STATUS_IN_PROCESS = set([
    Job.PENDING,
    Job.PULLED,
    Job.RUNNING,
])
STATUS_FINAL = set([
    Job.COMPLETED,
    Job.FAILED,
])

def return_descriptor(point, n_events=100):
    
    pitch, yoffset_layer, yoffset_plane, zshift_layer, zshift_plane, zshift_view, alpha = point
    
    cmd = "/opt/disney-run.sh python /opt/objective.py --pitch "+str(pitch)+" --yoffset_layer "+str(yoffset_layer)+\
        " --yoffset_plane "+str(yoffset_plane)+" --zshift_layer "+str(zshift_layer)+" --zshift_plane "+\
        str(zshift_plane)+" --zshift_view "+str(zshift_view)+" --alpha "+str(int(alpha))+\
        " --nEvents "+str(n_events)+" --method FH"

    descriptor = {
        "input": [],

        "container": {
            "workdir": "",
            "name": "oleg94/ship_metric:latest",
            "cpu_needed": 1,
            "max_memoryMB": 4096,
            "min_memoryMB": 1024,
            "cmd": cmd,
        },

        "required_outputs": {
            "output_uri": "none:",
            "file_contents": [
                {"file": "output.txt", "to_variable": "out"}
            ]
        }
    }
    
    return descriptor

def convertor(disney_output):
    
    return float(json.loads(re.sub(r"\\", '', disney_output[15:-2]))['reconstructible']), float(json.loads(re.sub(r"\\", '', disney_output[15:-2]))['reco_passed_no_clones'])

def simulate(point, n_events=100):
    
    descriptor = return_descriptor(point, n_events)
    job = stub.CreateJob(Job(input=json.dumps(descriptor), kind="docker")) 
    while True:
        job = stub.GetJob(RequestWithId(id=job.id))
        
        if job.status in STATUS_FINAL:
            break
        time.sleep(10)
    
    return convertor(job.output)

def get_new_point(model, bounds, opt_value, initial_points=None, seed=None, 
                  method='gaussian', n_sample=500, constraints=None, max_iter=5):

    if seed is not None:
        np.random.seed(seed)

    def acquisition(x):
        
        if x.ndim == 1:
            x = x.reshape(1, -1)
            
        if method=='gaussian':
            mean_values, variance = model.predict(x)
            std_values = np.sqrt(variance)
            
            return -expected_improvement(mean_values, std_values, opt_value)
        
        elif method=='laplace':
            mean_values, variance = model._raw_predict(x)
            std_values = np.sqrt(variance)
            
            return -expected_improvement_approx(mean_values, std_values, opt_value, GPy.likelihoods.Binomial(), n_sample)


    problem = GPyOpt.methods.BayesianOptimization(acquisition, bounds, constraints, exact_feval=True, 
                                                  initial_design_numdata=100, batch_size=100)
    problem.run_optimization(max_iter)
    
    return problem.x_opt, problem.fx_opt

def optimization_step(training_points, training_values, objective, space, trials=None, n_trials_low=20, 
                      n_trials_high=np.nan, kernel=GPy.kern.RBF(1), 
                      method='gaussian', treshold_proba=0.5, constraints=None):
    
    if trials.ndim != 2:
        trials = trials.reshape(-1, 1)
    
    new_point = None
    
    if method=='gaussian':
        model = GPy.models.GPRegression(training_points, training_values / trials, kernel)
        model.optimize_restarts(num_restarts=10, verbose=False)
        new_point, criterion_value = get_new_point(model, opt_value=np.min(model.predict(training_points)[0]), method=method,
                                               constraints=constraints, bounds=space)
        
    elif method=='laplace':
        binomial = GPy.likelihoods.Binomial()
        model = GPy.core.GP(training_points, training_values, kernel=kernel, 
                            Y_metadata={'trials': trials},
                            inference_method=GPy.inference.latent_function_inference.laplace.Laplace(),
                            likelihood=binomial)
        model.optimize_restarts(num_restarts=10, verbose=False)
        new_point, criterion_value = get_new_point(model,
                                               opt_value=binomial.gp_link.transf(np.min(model._raw_predict(training_points)[0])), 
                                               method='laplace', constraints=constraints, bounds=space)
    else:
        raise ValueError("method must be gaussian or laplace.")
    
    new_point = new_point.reshape(1, -1)
    new_value = np.asarray(objective(new_point, n_trials_low)).reshape(1, -1)
    new_trials = n_trials_low
    training_points = np.vstack([training_points, new_point])
    
    if (n_trials_high >= n_trials_low+1) and (method == 'laplace'):

        if fidelity_decision(n_trials_low, new_value, 
                             model.likelihood.gp_link.transf(np.min(model._raw_predict(training_points)[0])), 
                             treshold_proba):

            new_value = new_value + objective(new_point, n_trials_high-n_trials_low)
            new_trials = n_trials_high
            
    
    trials = np.vstack([trials, np.array([[new_trials]])])
    training_values = np.vstack([training_values, new_value])
        
    return training_points, training_values, trials, model

if __name__=='__main__':
    
    argv = sys.argv[1:]

    msg = '''Runs sampling of new points.\n\
    Usage:\n\
      python detached_runner.py [options] \n\
      
    Options:
      --n_points                    : Number of new sampled points:
                                    : Default is 100
      --n_events                    : Number of events in one simulation:
                                    : Default is 100
      --n_events_high               : Number of events in simulation with higher fidelity:
                                    : Default is 100
      --treshold_proba              : Treshold probability to calculate point with higher fidelity:
                                    : Default is 0.5
      --method                      : Name of regression method: 'gp', 'ggpm'
                                    : Default is 'gp'
      --help                        : Shows this help
      '''
    
    try:
        opts, args = getopt.getopt(argv, "hm:n:",
                                   ["help", "n_points=", "n_events_high=", "n_events=", "method=", "treshold_proba=", "index="])
    except getopt.GetoptError:
        print("Wrong options were used. Please, read the following help:\n")
        print(msg)
        sys.exit(2)
        
    method = 'gp'
    n_points = 100
    n_events = 100
    n_events_high = 100
    treshold_proba = 0.5
    index = 0
    
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print(msg)
            sys.exit()
        elif opt == "--method":
            if method in ['gp', 'ggpm']:
                method = arg
            else:
                print("Wrong method value.")
                print(msg)
                sys.exit()
        elif opt == "--n_points":
            n_points = int(arg)
        elif opt == "--n_events":
            n_events = int(arg)
        elif opt == "--n_events_high":
            n_events_high = int(arg)
        elif opt == "--treshold_proba":
            treshold_proba = float(arg)
        elif opt == "--index":
            index = int(arg)
            
    if os.path.exists('data/observations_'+str(n_events)+'_'+method+'_'+str(index)+'.csv'):
        observed_points = pd.read_csv('data/observations_'+str(n_events)+'_'+method+'_'+str(index)+'.csv').dropna()
    else:
        observed_points = pd.read_csv('data/initial_observations_'+str(n_events)+'.csv').dropna()
        
    stub = new_client()
    kernel = GPy.kern.RBF(len(space))

    for i in range(n_points):
        
        X = observed_points.dropna().drop(['reconstructible', 'reco_passed_no_clones', 'total'], axis=1).values
        Y = observed_points.dropna()[['reco_passed_no_clones']].values
        trials = observed_points.dropna()[['total']].values
        #because we want to maximize Y:
        Y = trials - Y

        new_x = None

        if method=='gp':
            model = GPy.models.GPRegression(X, Y/trials, kernel)

            model.optimize_restarts(num_restarts=10, verbose=False)
            new_x, criterion_value = get_new_point(model, opt_value=np.min(model.predict(X)[0]), method='gaussian',
                                                   constraints=constraints, bounds=space)

        elif method=='ggpm':
            binomial = GPy.likelihoods.Binomial()
            model = GPy.core.GP(X, Y, kernel=kernel, 
                                Y_metadata={'trials': trials},
                                inference_method=GPy.inference.latent_function_inference.laplace.Laplace(),
                                likelihood=binomial)

            model.optimize_restarts(num_restarts=10, verbose=False)
            new_x, criterion_value = get_new_point(model, 
                                                   opt_value=binomial.gp_link.transf(np.min(model._raw_predict(X)[0])), 
                                                   method='laplace', constraints=constraints, bounds=space)

        reconstructible, passed_no_clones = simulate(new_x, n_events)
        total = n_events

        if (n_events_high >= n_events+1) and (method == 'ggpm'):

            if fidelity_decision(reconstructible, passed_no_clones, 
                                 model.likelihood.gp_link.transf(np.min(model._raw_predict(X)[0])), 
                                 treshold_proba):

                reconstructible_additional, passed_no_clones_additional = simulate(new_x, n_events_high-n_events)

                reconstructible += reconstructible_additional
                passed_no_clones += passed_no_clones_additional
                total = n_events_high

        observed_points.loc[len(observed_points)] = list(new_x) + [reconstructible, passed_no_clones, total]
        observed_points.to_csv('data/observations_'+str(n_events)+'_'+method+'_'+str(index)+'.csv', index=False)