A file to keep my musings and to dos


Game analysis explained:
------------------------

A tournament is run between all the different strategies. We place each one in defence and test it against all other
strategies when attacking.
I want to be able to set up a tournament between all the different strategies, and see which one comes out on top.
We should play each game a number of times, and take the average score (also standard deviation, all stats etc.)

For example: periodic does well until he plays an adaptive strategy. This could lower his score considerably.



What questions do i want to answer?
-----------------------------------
- Can our GA converge upon the best rate for a given strategy (periodic, exponential etc.)?
- Can our GA pick the best strategy from a list of various strategies?
- Can iterating through all rates converge (find) the Nash Equilibrium




TODO: List

Core Game play
------------------------
DONE - Add the cost of moving in (in a smart way)
DONE - Tidy up game logic
DONE - Make sure the system/server set up all makes sense
DONE - Set up the system benefit. i.e. based on the threshold, the benefit can be calculated rather than individual servers
DONE - Make the move costs specific to the player on each server, not player type
DONE - Remove defender/attacker player type
DONE - Figure out a better way to input move costs into the servers
- Convert lists to numpy arrays where appropriate
- Sort out a way to assign who is defender and who is attacker. (Only allow one defender). Defender starts off with control
- Point above still isn't fixed. Need to check there is only one defender in each game.
- Need to figure out how best to choose rates when comparing strategies, we have a continuum to deal with
- Check that new strategies are able to apply old strategies on individual servers (not sure they can at the moment, how would it work?)
- Calculate some form of mean reward when playing the tournament between strategies
- Decide on what should be in player base_properties, try to make it as minimal as possible



FlipIt paper
----------------------------------------
DONE - Do own version of heatplots on page 19
DONE - Do heatplots for the phase periodic strategies
- Do heatplots for LastMovePeriodic Strategies
- Do heatplots for Exponential Strategies

Pandas Work
-----------------------
- Figure out best way of converting all the data into some form of dataframe
- Write these to files, in a logical structure
- Be able to import these files, simulate and analyse. I want all information tracked.



Plots
------------------------
- Create a class that plots the server benefits
- Progress this to system benefit

Animations
------------------------

DONE 1 Get rid of the double circles
- Tidy up the code for animate
DONE - Change the animation to accommodate 2+ players
DONE - Fix the side_buffer issues in the animation
DONE - File "/Users/chrissherfield/Documents/Python/FlipIt/graphics/multi_player_animate.py", line 194, in __update
    self.move_number[server][server_owner] += 1
- Create an animation of the benefit plots


Strategies
------------------------

DONE - Change the exponential strategy to accommodate multiple servers etc.



Logic explained:
------------------------

Game class holds a system and multiple players.

The system holds a list of servers. - This is where the game type can be decided, all on the reward structure (threshold etc.)

The servers keep track of of all benefit, moves, costs etc. (for the individual server obviously)
