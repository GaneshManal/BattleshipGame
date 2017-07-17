"""
 Class definitions for Player and Battle Management
"""

import constants
from weapons import BattleShip, Missile


class Player(object):
    """ class definition for player management in battle"""

    def __init__(self, name):
        """ Initialize the player name, ships and missiles """
        self._name = name
        self._ships = []
        self._missiles = []

    def get_name(self):
        """ Read the player name"""
        return self._name

    def get_missiles(self):
        """ Read player missiles"""
        return self._missiles

    def get_ships(self):
        """ Read the player ships"""
        return self._ships

    def add_ship(self, ship):
        """ Add ship to the player ships"""
        self._ships.append(ship)

    def add_missile(self, missile):
        """ Add missile to the player missiles"""
        self._missiles.append(missile)

    def hit_missile(self):
        """ Read the missile from the available set of missiles
        Ultimately we get the target to hit in opponents battlefield
        :return: missile in queue if available else None
        """
        if len(self._missiles):
            return self._missiles.pop(0)
        else:
            return None

    def defend_missile(self, target):
        """
        Check if missile hits any of the player's ship
        :param target: position the attacker is hitting in battlefield
        :return: if missile was successfully defended or not
        """
        hit_flag = False
        for x_ship in self._ships:
            hit_flag = x_ship.hit_me(target)
            if hit_flag:
                ret = x_ship.destroy_me()
                if ret:
                    self._ships.remove(x_ship)
                break
        return not hit_flag


class BattleArea(object):
    """ class definition for battle management in provided field"""

    def __init__(self):
        self.player_count = 0
        self._players = []
        self._dimensions = []
        self.war_details = None
        self.ship_row_count = 0

    def _configure_battle_field(self, dimensions):
        bf_dimension = dimensions.split(' ')
        if len(bf_dimension) != 2:
            return False, 'In-valid Dimension Parameters'

        width, height = bf_dimension[0], bf_dimension[1]
        width, height = int(width), int(ord(height)) - 64

        for x_width in range(height):
            for y_height in range(1, width+1):
                self._dimensions.append((chr(x_width+65), y_height))

        return True, None

    def _is_ship_in_battle_area(self, ship_cells):
        """
        Check if each cell of the ship is in battle area
        :return: True if ship in battle area
        """
        in_battle_area = True
        for x_cell in ship_cells:
            if x_cell not in self._dimensions:
                in_battle_area = False
                break
        return in_battle_area

    def _configure_battle_ships(self, ship_type, ship_details):
        """
         Update Ship Positions for player
        :param ship_type: P or Q, Q needs 2 missile hits
        :param ship_details: position and size of ship
        """
        ship_size = (ship_details[1], ship_details[2])
        all_ship_pos = ship_details[3:]

        # Pending - Add ship only if its in battlefield dimensions

        start, ship_per_player = 0, len(all_ship_pos) / self.player_count
        for x_player in self._players:
            player_ships = all_ship_pos[start: start + ship_per_player]
            start += ship_per_player

            for ship_pos in player_ships:
                ship_obj = BattleShip(ship_type, ship_size, ship_pos)

                ship_cells = ship_obj.get_ship_cells()
                if self._is_ship_in_battle_area(ship_cells):
                    x_player.add_ship(ship_obj)
                else:
                    print("Skipping (%s)- ship not in battle area." % str(ship_cells))

        return True, None

    def configure_players(self):
        """ Configure players from the input details"""
        names = ['Player-1', 'Player-2', 'Player-3']
        for i in range(self.player_count):
            self._players.append(Player(names[i]))
        return True, None

    def configure_ships(self):
        """ Configure Ships from the input details"""
        for data in self.war_details[constants.PLAYERS_COUNT + 1:]:
            ship_details = data.split(' ')
            ship_type = ship_details[0]

            if ship_type in ['P', 'Q']:
                self.ship_row_count += 1

                ret, msg = self._configure_battle_ships(ship_type, ship_details)
                if not ret:
                    return ret, msg
            else:
                break

        return True, None

    def configure_missiles(self):
        # Configure Missiles
        player_index = 0
        for data in self.war_details[constants.PLAYERS_COUNT + self.ship_row_count + 1:]:
            x_player = self._players[player_index]
            player_index += 1

            missiles = data.split(' ')
            for missile_pos in missiles:
                if len(missile_pos) == 2:
                    missile_obj = Missile(missile_pos)
                    x_player.add_missile(missile_obj)
                else:
                    print('Skipping(%s) - Invalid missile position' % missile_pos)
                    return False, 'Invalid Missile Target'

        return True, None

    def configure_battle(self, war_details):
        """
        Configure the battle using the user input details
        :param war_details: input details for battle management
        :return: Successfully configured or not, error message
        """
        self.war_details = war_details

        # Configure battlefield dimensions
        ret, msg = self._configure_battle_field(self.war_details[constants.BF_DIMENSIONS])
        if not ret:
            return ret, msg

        # Configure Player Count
        self.player_count = int(war_details[constants.PLAYERS_COUNT])

        # Configure Players
        ret, msg = self.configure_players()
        if not ret:
            return ret, msg

        # Configure Ships
        ret, msg = self.configure_ships()
        if not ret:
            return ret, msg

        # Configure Missiles
        ret, msg = self.configure_missiles()
        if not ret:
            return ret, msg

        return True, 'Battle Configuration Successful.'

    def get_players(self):
        """ Read the battle field players"""
        return self._players

    def run_battle(self):
        """ Run the battle in configured battle"""
        attacker, defender = self._players[0], self._players[1]

        while True:
            if len(attacker.get_missiles()) == 0 and len(defender.get_missiles()) == 0:
                print("Peace Declared")
                break

            missile = attacker.hit_missile()
            if missile:
                target = missile.get_target()
            else:
                print('%s has no more missiles left to launch' % attacker)
                attacker, defender = defender, attacker
                continue

            defended = defender.defend_missile(target)
            result = defended and 'miss' or 'hit'

            target_str = ''.join([str(item) for item in target])
            print('%s fires a missile with target %s which got %s' %
                  (attacker.get_name(), str(target_str), result))

            if defended:
                if len(defender.get_missiles()):
                    attacker, defender = defender, attacker
                else:
                    print('%s has no more missiles left to launch' % defender.get_name())
                    continue
            else:
                if not len(defender.get_ships()):
                    print('%s won the battle' % attacker.get_name())
                    break

        return True
