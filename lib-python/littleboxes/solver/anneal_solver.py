import logging
import math
import random

from littleboxes.solver.solver import Solver


class XWordMonteCarloSimulator(object):
    '''Perform Metropolis-Hastings simulation on a Crossword.

    Args:
        scorefxn (callable): Takes a Crossword and returns an energy
            score (lower = more favorable).
        moves (list(callable)): List of candidate MC moves. Each must
            take a Crossword and modify it in some way. Moves will be
            selected randomly during the simulation.
            TODO: Select moves according to a set of weights.
        temperature (float): The simulation temperature.
    '''
    logger = logging.getLogger('littleboxes.solver.anneal_solver.XWordMonteCarloSimulator')

    def __init__(self, scorefxn, moves, temperature=1.0):
        self.scorefxn = scorefxn
        self.moves = moves
        self.set_temperature(temperature)

    def set_temperature(self, temperature):
        self.logger.debug('Setting simulation temperature = %.3f', temperature)
        self.beta = 1.0 / temperature

    def attempt_move(self, xword):
        E = self.scorefxn(xword)
        tmp = xword.copy()
        move = random.choice(self.moves)
        move(tmp)
        E_prime = self.scorefxn(tmp)
        p = math.exp(-self.beta * (E_prime - E))
        self.logger.debug("Attempting move %s, E = %.3f, E' = %.3f, p = %.3f",
                          move, E, E_prime, p)
        if p >= random.random():
            self.logger.debug('Move accepted')
            return tmp

        self.logger.debug('Move rejected')
        return xword


class SimulatedAnnealingSolver(Solver):
    logger = logging.getLogger('littleboxes.solver.anneal_solver.SimulatedAnnealingSolver')

    def __init__(self, scorefxn, moves, T_schedule):
        self._sim = XWordMonteCarloSimulator(scorefxn, moves)
        self.T_schedule = T_schedule

    def solve(self, xword):
        xword = xword.copy()
        for T in self.T_schedule:
            self._sim.set_temperature(T)
            xword = self._sim.attempt_move(xword)
            yield xword.n_set, xword
        yield xword.n_set, xword
