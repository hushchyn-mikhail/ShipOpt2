min_dist = 1.6

space = [{'name': 'pitch', 'type': 'continuous', 'domain': (min_dist, min_dist*2)},\
         {'name': 'yoffset_layer', 'type': 'continuous', 'domain': (0, min_dist*2)},\
         {'name': 'yoffset_plane', 'type': 'continuous', 'domain': (0, min_dist*2)},\
         {'name': 'zshift_layer', 'type': 'continuous', 'domain': (min_dist, 10)},\
         {'name': 'zshift_plane', 'type': 'continuous', 'domain': (min_dist*2, 20)},\
         #{'name': 'zshift_view', 'type': 'continuous', 'domain': (min_dist*4, 50)},\
         {'name': 'zshift_view', 'type': 'continuous', 'domain': (min_dist*6, min_dist*6)},\
         {'name': 'alpha', 'type': 'discrete', 'domain': (5, 5)}]

constraints = [{'name': 'constr_1', 'constrain': 'x[:,1]-x[:,0]'},\
               {'name': 'constr_2', 'constrain': 'x[:,2]-x[:,0]'},\
               {'name': 'constr_4', 'constrain': 'x[:,3]-x[:,4]+'+str(min_dist)},\
               {'name': 'constr_5', 'constrain': 'x[:,4]-x[:,5]+'+str(min_dist)+'+x[:,3]'}]