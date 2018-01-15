.. _whetting_the_appetite:

*********************
Whetting The Appetite
*********************


The first thing we'd like to do is play a quick game of FlipIt. etc. etc.
To begin simulating games within the library we need to understand how to create players::

    from strategies.player import Player
    from strategies.server_strategies.exponential import Exponential


    attacker_properties = {'move_costs': (0.8, ),
                           'threshold': 1
                           }

    defender_properties = {'move_costs': (1.2, ),
                           'threshold': 1
                           }

First import the ``Player`` class from the ``strategies`` directory.
We then define two dictionaries, one for each player. This includes ``move_costs``, the costs of moving on each resource
and ``threshold``, the number of resources required to be compromised by the player to receive reward.

Create the players::

    defender = Player("Defender ", player_properties=copy(defender_properties), strategies=Exponential(1.1))
    attacker = Player("Attacker ", player_properties=copy(attacker_properties), strategies=Exponential(0.9))

The first argument is the player's name. The player properties are defined as above. For now, we have chosen the simplest class of
strategy for both players as the ``Exponential`` class.

We are now ready to create and play the game::

    from system import System

    game_properties = {'time_limit': 10}
    s = System(1)

    g = Game(players=(defender, attacker), system=s, game_properties=game_properties)
    g.play()

First, we import the system the game is to be played over (explain system later)
Next, we create the game properties to choose the amount of time the game is played for.
Then, we create the game and play.

Full code::

    from strategies.player import Player
    from system import System

    from strategies.server_strategies.exponential import Exponential


    attacker_properties = {'move_costs': (0.8, ),
                           'threshold': 1
                           }

    defender_properties = {'move_costs': (1.2, ),
                           'threshold': 1
                           }

    defender = Player("Defender ", player_properties=copy(defender_properties), strategies=Exponential(1.1))
    attacker = Player("Attacker ", player_properties=copy(attacker_properties), strategies=Exponential(0.9))

    game_properties = {'time_limit': 10}
    s = System(1)

    g = Game(players=(defender, attacker), system=s, game_properties=game_properties)
    g.play()
    g.print_full_game_summary()


.. _animating_game:

==================
Animating the Game
==================

This game can easily be animated::

    from graphics.multi_player_animate import Animate

    a = Animate()
    a.start(g)


