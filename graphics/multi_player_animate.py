import tkinter as tk
import matplotlib

matplotlib.use('TkAgg')

"""
generalise all colours and options, perhaps into a dictionary? Maybe get some themes

Create benefit graphs above and below for the players
"""

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800

SIDE_BUFFER = 20
# A constant to change the side of the rectangles (smaller number means bigger rectangle)
RECTANGLE_DIFFERENCE_CONSTANT = 10

CIRCLE_RADIUS = 4

# Time pause between updates (milliseconds)
STEP_TIME = 10

# COLOURS
BACKGROUND_COLOUR = "white"

player_colours = {1: "blue", 2: "red", 3: "green", 4: "yellow", 5: "brown", 6: "maroon", 7: "pink"}

# TIME_INCREMENT
TIME_INCREMENT = 0.01


class Animate:

    def __init__(self):

        # Setting up the canvas
        self.root = tk.Tk()
        self.root.title("Animation")
        # ulc position of root window
        self.root.geometry("+{}+{}".format(150, 80))
        # create a canvas to draw on
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=BACKGROUND_COLOUR)
        self.canvas.pack()

        # Create specific graphics
        self.graphics = {}
        self.time_label = tk.Label(text="Time: 0.0")
        self.time_label.pack()

        self.game = None
        self.system = None
        self.number_of_servers = 0
        self.move_number = {}  # This is a dictionary of a dictionary: {Server: {Player: move_number}}
        self.players = {}  # A dictionary of players and their playing position >= 1
        self.server_ownership = {}
        self.player_properties = {}

        # Time set up
        self.time = 0.0
        self.time_limit = 0.0
        self.time_conversion = 0.0
        self.time_increment = TIME_INCREMENT

        # Positional set up
        self.rectangle_difference = 0.0
        self.segment_size = 0.0
        self.first_player_rectangle = 0.0
        self.segment_position = 0.0

    def __setup_game(self, game):
        self.game = game
        self.system = game.get_system()
        self.number_of_servers = self.system.get_number_of_servers() + 1

        # Assign each player an integer to be used as a position later
        for counter, player in enumerate(self.system.get_all_servers()[0].get_players()):
            self.players[player] = counter + 1

        # Calculate the time-pixel representation in order to fit the game on the screen
        self.time_limit = self.game.get_time_limit()
        self.time_conversion = (CANVAS_WIDTH - 2 * SIDE_BUFFER) / self.time_limit
        self.rectangle_difference = CANVAS_HEIGHT / (RECTANGLE_DIFFERENCE_CONSTANT * self.number_of_servers)
        # Calculate canvas space (or segment height) for each server graphic
        self.segment_size = CANVAS_HEIGHT / self.number_of_servers
        self.first_player_rectangle = (self.segment_size - (len(self.players) * self.rectangle_difference)) / 2

    def start(self, game):
        """
        Starts the animation. Needs to be able to calculate all required information from system.
        The system is a list of servers. 
        The servers contain player history and benefits
        :param game: 
        :return: 
        """
        self.__setup_game(game)

        # We want to put each graphic in the centre of this
        # Want to create a graphic for each server
        for server_counter, server in enumerate(self.system.get_all_servers()):
            self.graphics[server] = {}
            self.move_number[server] = {}
            # Which segment are we currently in?
            self.segment_position = server_counter * self.segment_size

            # Draw lines to segment off the servers
            if server_counter > 0:
                self.graphics[server]['line'] = self.canvas.create_line(0, self.segment_position,
                                                                        CANVAS_WIDTH, self.segment_position, width=5)

            # Create all the lines for the rectangles to extend between
            for player in self.players:

                if self.players[player] < len(self.players):
                    line_height = self.segment_position + self.first_player_rectangle + \
                                  self.rectangle_difference*self.players[player]
                    self.graphics[server]['line'] = self.canvas.create_line(SIDE_BUFFER, line_height,
                                                                            CANVAS_WIDTH - SIDE_BUFFER, line_height)

            # Find the player that first controlled the server
            for player, times in server.get_all_player_benefit_times().items():
                self.move_number[server][player] = 0
                if len(times) > 0:
                    if times[0][0] == 0.0:
                        self.server_ownership[server] = player
                        # print("First Owner is:", player.get_name())

            tag = self.server_ownership[server].get_name() + str(server_counter - 1) + "_" + str(0)
            colour = player_colours[self.players[self.server_ownership[server]]]
            y1 = self.segment_position + self.first_player_rectangle\
                 + (self.players[self.server_ownership[server]] - 1) * self.rectangle_difference
            y2 = y1 + self.rectangle_difference

            self.graphics[server]['rectangles'] = [self.canvas.create_rectangle(SIDE_BUFFER,
                                                                                y1,
                                                                                SIDE_BUFFER, y2,
                                                                                tag=tag, fill=colour)]

        ###################################
        # Add the system graphic
        ###################################

        self.graphics["system"] = {}
        self.move_number["system"] = {}
        # Which segment are we currently in?
        self.segment_position = (self.number_of_servers - 1) * self.segment_size

        # Draw lines to segment off the servers
        if server_counter > 0:
            self.graphics[server]['line'] = self.canvas.create_line(0, self.segment_position,
                                                                    CANVAS_WIDTH, self.segment_position,
                                                                    width=5)

        # Create all the lines for the rectangles to extend between
        for player in self.players:

            if self.players[player] < len(self.players):
                line_height = self.segment_position + self.first_player_rectangle + \
                              self.rectangle_difference * self.players[player]
                self.graphics["system"]['line'] = self.canvas.create_line(SIDE_BUFFER, line_height,
                                                                        CANVAS_WIDTH - SIDE_BUFFER, line_height)

        # Find the player that first controlled the server
        for player, times in self.system.get_all_player_benefit_times().items():
            self.move_number["system"][player] = 0
            if len(times) > 0:
                if times[0][0] == 0.0:
                    self.server_ownership["system"] = player
                    # print("First Owner is:", player.get_name())

        tag = self.server_ownership["system"].get_name() + str(server_counter - 1) + "_" + str(0)
        colour = player_colours[self.players[self.server_ownership["system"]]]
        y1 = self.segment_position + self.first_player_rectangle \
             + (self.players[self.server_ownership["system"]] - 1) * self.rectangle_difference
        y2 = y1 + self.rectangle_difference

        self.graphics['system']['rectangles'] = [self.canvas.create_rectangle(SIDE_BUFFER,
                                                                            y1,
                                                                            SIDE_BUFFER, y2,
                                                                            tag=tag, fill=colour)]

        self.time += self.time_increment
        self.__update()
        self.root.mainloop()

    def __update(self):

        for server_counter, server in enumerate(self.system.get_all_servers()):
            # Which segment are we currently in?
            self.segment_position = server_counter * self.segment_size

            server_owner = None
            player_benefit_times = server.get_all_player_benefit_times()
            move_check = {}
            for player in player_benefit_times:
                move_check[player] = 0
                times = player_benefit_times[player]
                if len(times) > 0:
                    # print(self.time)
                    # print(player.get_name(), times)
                    for counter, t in enumerate(times):
                        if t[0] < self.time < t[1]:
                            # Currently this player is gaining benefit
                            server_owner = player
                            move_check[player] = counter
                            break

                    if server_owner is not None:
                        break

            if server_owner == self.server_ownership[server]:
                # No change in control, need to check if this is a new move though..
                current_rectangle = self.graphics[server]['rectangles'][-1]
                x1, y1, x2, y2 = self.canvas.coords(current_rectangle)
                self.canvas.coords(current_rectangle, x1, y1, self.time * self.time_conversion + SIDE_BUFFER, y2)

                if move_check[server_owner] > self.move_number[server][server_owner]:

                    self.move_number[server][server_owner] += 1
                    tag = self.server_ownership[server].get_name() + str(server_counter) + "_" + str(0)
                    colour = player_colours[self.players[self.server_ownership[server]]]
                    y1 = self.segment_position + self.first_player_rectangle + (self.players[self.server_ownership[
                        server]] - 1) * self.rectangle_difference
                    y2 = y1 + self.rectangle_difference
                    circle_height = y1 + self.rectangle_difference/2

                    x = self.time * self.time_conversion + SIDE_BUFFER
                    self.__create_circle(x, circle_height, CIRCLE_RADIUS, tag + "circle_", colour)

            else:
                self.server_ownership[server] = server_owner
                self.move_number[server][server_owner] += 1
                tag = self.server_ownership[server].get_name() + str(server_counter) + "_" + str(0)
                colour = player_colours[self.players[self.server_ownership[server]]]
                y1 = self.segment_position + self.first_player_rectangle + (self.players[self.server_ownership[
                    server]] - 1) * self.rectangle_difference
                y2 = y1 + self.rectangle_difference
                circle_height = y1 + self.rectangle_difference/2

                x = self.time * self.time_conversion + SIDE_BUFFER
                self.graphics[server]['rectangles'].append(self.canvas.create_rectangle(x, y1, x, y2, tag=tag, fill=colour))
                self.__create_circle(x, circle_height, CIRCLE_RADIUS, tag + "circle_", colour)


        # Update the system line

        # Which segment are we currently in?
        self.segment_position = (self.number_of_servers - 1) * self.segment_size

        server_owner = None
        player_benefit_times = self.system.get_all_player_benefit_times()
        move_check = {}
        for player in player_benefit_times:
            move_check[player] = 0
            times = player_benefit_times[player]
            if len(times) > 0:
                # print(self.time)
                # print(player.get_name(), times)
                for counter, t in enumerate(times):
                    if t[0] < self.time < t[1]:
                        # Currently this player is gaining benefit
                        server_owner = player
                        move_check[player] = counter
                        break

                if server_owner is not None:
                    break

        if server_owner == self.server_ownership["system"]:
            # No change in control, need to check if this is a new move though..
            current_rectangle = self.graphics["system"]['rectangles'][-1]
            x1, y1, x2, y2 = self.canvas.coords(current_rectangle)
            self.canvas.coords(current_rectangle, x1, y1, self.time * self.time_conversion + SIDE_BUFFER, y2)

            if move_check[server_owner] > self.move_number["system"][server_owner]:

                self.move_number["system"][server_owner] += 1
                tag = self.server_ownership["system"].get_name() + str(server_counter) + "_" + str(0)
                colour = player_colours[self.players[self.server_ownership["system"]]]
                y1 = self.segment_position + self.first_player_rectangle + (self.players[self.server_ownership[
                    "system"]] - 1) * self.rectangle_difference
                y2 = y1 + self.rectangle_difference
                circle_height = y1 + self.rectangle_difference/2

                x = self.time * self.time_conversion + SIDE_BUFFER
                self.__create_circle(x, circle_height, CIRCLE_RADIUS, tag + "circle_", colour)

        else:
            self.server_ownership["system"] = server_owner
            self.move_number["system"][server_owner] += 1
            tag = self.server_ownership["system"].get_name() + str(server_counter) + "_" + str(0)
            colour = player_colours[self.players[self.server_ownership["system"]]]
            y1 = self.segment_position + self.first_player_rectangle + (self.players[self.server_ownership[
                "system"]] - 1) * self.rectangle_difference
            y2 = y1 + self.rectangle_difference
            circle_height = y1 + self.rectangle_difference/2

            x = self.time * self.time_conversion + SIDE_BUFFER
            self.graphics["system"]['rectangles'].append(self.canvas.create_rectangle(x, y1, x, y2, tag=tag, fill=colour))
            # self.__create_circle(x, circle_height, CIRCLE_RADIUS, tag + "circle_", colour)


        self.time_label.config(text="Time: " + str(round(self.time, 3)))
        self.time += self.time_increment
        if self.time * self.time_conversion > CANVAS_WIDTH - SIDE_BUFFER or self.time > self.time_limit:
            return
        self.canvas.after(STEP_TIME, self.__update)


    def __create_circle(self, x, y, r, tag, colour):
        """
        :param x: centre x coordinate
        :param y: centre y coordinate
        :param r: radius length
        :param tag: name of the circle
        :param colour: circle colour
        """
        ulc = x - r, y - r
        lrc = x + r, y + r
        # give the circle a tag name for reference
        self.canvas.create_oval(ulc, lrc, tag=tag, fill=colour)



