from genopt.optimizer import SGA
from genopt.scalers import sigma_trunc_scaling
from genopt.selectors import tournament_selection
from genopt.crossovers import two_point_crossover
from genopt.mutators import uniform_mutation
import os
from CGRtools.files import SDFRead
from pickle import dump

import logging

os.environ['DB'] = './data/db.shelve'
os.environ['DATA'] = './data/rules'

from RNNSynthesis.environment import SimpleSynthesis
from RNNSynthesis.helper import get_feature, get_feature_bits
logger = logging.getLogger("exampleApp")
logger.setLevel(logging.INFO)

# create the logging file handler
fh = logging.FileHandler("GA.log")

formatter = logging.Formatter()
fh.setFormatter(formatter)

# add handler to logger object
logger.addHandler(fh)

logger.info("Program started")

target = next(SDFRead(open('./data/tylenol.sdf', encoding='UTF-8')))
env = SimpleSynthesis(target, steps=10)
target_bits = get_feature_bits(target)
step_per_score = dict()


def fit_func(hromosoma):
    for action in hromosoma:
        state, reward, done, info = env.step(action)
        if done:
            if state == target_bits:
                logger.info(f'синтетический путь для молекулы {target} = {[step for step in env.render()]}')
                print(f'синтетический путь для молекулы {target} = {[step for step in env.render()]}')
            # elif env.steps > env.max_steps:
            #     logger.info(f'Превышено число шагов: {env.steps} > {env.max_steps}')
            #     print(f'Превышено число шагов: {env.steps} > {env.max_steps}')
            # elif env.depth >= 5:
            #     logger.info(f'Превышена глубина синтеза {env.depth} > 5')
            #     print(f'Превышена глубина синтеза {env.depth} > 5')
            # elif action == 'STOP':
            #     logger.info('Выпало действие STOP')
            #     print('Выпало действие STOP')
            return reward


ga = SGA(task='maximize', pop_size=25, cross_prob=0.8, mut_prob=0.2, elitism=True)
ga.set_selector_type(tournament_selection)
ga.set_scaler_type(sigma_trunc_scaling)
ga.set_crossover_type(two_point_crossover)
ga.set_mutator_type(uniform_mutation)
ga.set_fitness(fit_func)

ga.initialize(space=env.action_space, steps=10)
# ga.run(n_iter=500, verbose=True)

for i in range(100):
    ga.step()
    print(f'ga.score = {ga.best_individual().score}')
    logger.info(f'{i}: {ga.best_individual().score}')
    step_per_score[i] = ga.best_individual().score
logger.info('Done')

with open('ga_result.pickle', 'wb') as f:
    dump(step_per_score, f)
