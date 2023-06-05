.. running_your_first_ga:

*********************
Running your first GA
*********************

The first thing we'll try is setting up a simple Genetic Algorithm (GA), running it and then plotting the results::

    from genetic_algorithms.genetic_algorithm import GeneticAlgorithm
    from strategies.server_strategies.exponential import Exponential
    from strategies.player import Player
    from core.tournament import TOURNAMENT_TYPE

Here, we have imported the modules required to run some form of GA.
We are going to fill the two (defender and attacker) populations with Exponential strategies only.
For this, we have imported the ``Exponential`` class.
We have also imported the ``Player`` class in order to create players to fill the population
and also the ``TOURNAMENT_TYPE`` enum, to decide whether we want to run it deterministically
using payoff formulae or stochastically as a simulation. In this case we will run it stochastically.
\n
Next we define some dictionary defining the properties of the ``ga``, ``game``, ``tournament``, and ``player``.::

    game_properties = {'time_limit': 200}

We set the time limit of each game to be 200.::

    tournament_properties = {
        'number_of_rounds': 5,
        'attacker_threshold': 1,
        'defender_threshold': 1,
        'selection_ratio': 1.0,
        'tournament_type': TOURNAMENT_TYPE.STOCHASTIC,
        'game_properties': game_properties,
        }

The GA runs a tournament each generation between the two populations.
The number of rounds is the number of games played between each gene (player) in the population.
The defender and attacker threshold are the number of resources each player is required to be
in control of for the player to receive payoff.
The selection ratio is between 0 and 1 and is the proportion of matches to be played between
the two populations.
The tournament type is either deterministic (using analytic payoffs) or stochastic (simulated).::


    ga_properties = {
        'mutation_rate': 0.002,
        'file_location': 'data/stochastic/location/',
        'upper_bound': 5.0,
        'print_out': True
        }

The ``ga_properties`` represent the set up of the genetic algorithm.
The ``mutation_rate`` is how often a gene is likely to be mutated.
The ``file_location`` is where all data is to be written.
The ``upper_bound`` is the highest rate that can be introduced to the population.
Note that in the stochastic case, having a higher upper bound slows down the simulations.
``print_out`` is a boolean, if true it will print out more information to the console.::

    defender_ga_properties = {
        'name': "Defender ",
        'number_of_players': 50,
        'strategy_classes': (Exponential,),
        'move_costs': (0.2,),
        }

    attacker_ga_properties = {
        'name': "Attacker ",
        'number_of_players': 50,
        'strategy_classes': (Exponential,),
        'move_costs': (0.3,),
        }

Above, we define the properties for the defender population and the attacker population.
``name`` is purely the name of population we're referring to, plus a number for each gene in the
population.
``number_of_players`` is the size of the population.
``stategy_classes`` is a tuple of strategies, taken from the ``strategies.server_strategies`` directory.
In this case we only include ``Exponential``, however if desired we can put in any of the current strategies available.
``move_costs`` is a tuple of costs, one for each server. In this case it is a tuple of length as we are only playing over
one resource.::


    ga = GeneticAlgorithm(defenders=defender_ga_properties,
                          attackers=attacker_ga_properties,
                          ga_properties=ga_properties,
                          tournament_properties=tournament_properties)

    ga.run(1000, 100)
    ga.plot()

Finally, we can call the ``GeneticAlgorithm`` class with all the dictionaries defined above.
After this we call the ``ga.run`` method for 5000 iterations, writing to file every 100 iterations.
Once this is complete, we can plot the results, resulting in....






