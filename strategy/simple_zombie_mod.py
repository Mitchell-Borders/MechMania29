# This is a simple zombie strategy:
# Move directly towards the closest human. If there are any humans in attacking range, attack a random one.
# If there are no humans in attacking range but there are obstacles, attack a random obstacle.

import random
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.game_state import GameState
from game.character.action.attack_action_type import AttackActionType
from game.util.position import Position
from strategy.strategy import Strategy


class SimpleZombieModification(Strategy):

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        choices = []
        already_attacked_humans = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue


            pos = game_state.characters[character_id].position  # position of the zombie
            closest_human_pos = pos  # default position is zombie's pos
            closest_human_distance = 1984  # large number, map isn't big enough to reach this distance
            count = 0
            # Iterate through every human to find the closest one
            for c in game_state.characters.values():
                characters = game_state.characters.values()
                # get characters that are humans
                humans = [c for c in characters if not c.is_zombie]
                if len(humans) < 10:
                    already_attacked_humans = []
                if c.is_zombie:
                    continue  # Fellow zombies are frens :D, ignore them
                
                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y) # calculate manhattan distance between human and zombie
                if distance < closest_human_distance and c.id not in already_attacked_humans:  # If distance is closer than current closest, replace it!
                    closest_human_pos = c.position
                    closest_human_distance = distance
                    already_attacked_humans.append(c.id)

            # for each positoin to move to in a*, get the max amount of manhatten distance from 
            #curr position to the positions in the list. Stopping when we reach a distance of 5
                position_list = self.get_a_star_path(c.position, closest_human_pos, game_state)
            

            # Move as close to the human as possible
            move_distance = 1337  # Distance between the move action's destination and the closest human
            move_choice = moves[0]  # The move action the zombie will be taking
            current_distance = 0  
            for m in moves:
                for position in position_list:
                    man_distance = self.manhattan_distance(m.destination, position)
                    if man_distance <= 5 and man_distance > current_distance:
                        current_distance = man_distance
                        move_choice = m
            choices.append(move_choice)  # add the choice to the list
        return choices

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:

        choices = []

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue

            humans = []  # holds humans that are in range

            # Gather list of humans in range
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    humans.append(a)
                    
            humans = sorted(humans, key=lambda h: game_state.characters[h.attacking_id].health)
            
            if humans:  # Attack a random human in range
                choices.append(humans[0])
            else:  # No humans? Shame. The targets in range must be terrain. May as well attack one.
                terrain = [a for a in attacks if a.type is AttackActionType.TERRAIN and game_state.terrains[a.attacking_id]]
                terrain = sorted(terrain, key=lambda t: game_state.terrains[t.attacking_id].health)
                choices.append(random.choice(attacks))

        return choices
    
    class StarNode:
        def __init__(self, f = None, g = None, h = None, position = None, parent = None):
            self.f = f
            self.g = g
            self.h = h
            self.position = position
            self.parent = parent

    def get_a_star_path(self, start: Position, goal: Position, game_state: GameState):
        starting_node = self.StarNode(0, 0, 0, start)
        open_list = [starting_node]
        end_node = self.StarNode(0, 0, 0, goal)

        closed_list = []
        # while end has not been reached
        while len(open_list) > 0:
            curr_node = self.lowest_f_node(open_list)
            if curr_node.position == goal:
                return open_list
            else:
                #remove from open list where the curr-node object is
                closed_list.append(curr_node)
                adjacent_positions = self.get_adjacent_positions(curr_node, game_state, goal)
                
                for adj_position in adjacent_positions:
                    if adj_position.g < curr_node.g and adj_position in closed_list:
                        adj_position.g = curr_node.g
                        curr_node.parent = adj_position
                    elif curr_node.g < adj_position.g and adj_position in open_list:
                        adj_position.g = curr_node.g
                        adj_position.parent = curr_node
                    elif adj_position not in open_list and adj_position not in closed_list:
                        open_list.append(adj_position)

            # for position in open_list:
            #     h_of_position = self.get_h(position, goal)
    
    def get_adjacent_positions(self, curr_pos_star_node: StarNode, game_state: GameState, goal):
        #for each positoin around the current position, create a StarNode
        adjacent_positions = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                #Don't add the current position
                if x == 0 and y == 0:
                    continue
                #Don't add positions that are out of bounds OR terrain/walls
                adjacent_star_node = self.StarNode()
                adjacent_star_node.position = Position(curr_pos_star_node.position.x + x, curr_pos_star_node.position.y + y)
                adjacent_star_node.g = self.get_g(curr_pos_star_node, adjacent_star_node)
                adjacent_star_node.h = self.get_h(adjacent_star_node.position, goal)
                adjacent_star_node.f = adjacent_star_node.g + adjacent_star_node.h
                adjacent_positions.append(adjacent_star_node)
        return adjacent_positions
                
    def lowest_f_node(self, open_list):
        lowest_node = open_list[0]
        for node in open_list:
            if node.f < lowest_node.f:
                lowest_node = node
        return lowest_node

    def get_h(self, position, goal) -> int:
        # h is the manhatten distance between the current node and the goal
        return self.manhattan_distance(position, goal)

    def get_g(self, cur_postion : StarNode, adjacent_position : StarNode) -> float:
        if cur_postion.position.x - 1 == adjacent_position.position.x \
            and cur_postion.position.y - 1 == adjacent_position.position.y:
                return cur_postion.g + 1.5
            
        if cur_postion.position.x == adjacent_position.position.x \
            and cur_postion.position.y - 1 == adjacent_position.position.y:
                return cur_postion.g + 1
        
        if cur_postion.position.x + 1 == adjacent_position.position.x \
            and cur_postion.position.y - 1 == adjacent_position.position.y:
                return cur_postion.g + 1.5
        
        if cur_postion.position.x - 1 == adjacent_position.position.x \
            and cur_postion.position.y == adjacent_position.position.y:
                return cur_postion.g + 1
        
        if cur_postion.position.x + 1 == adjacent_position.position.x \
            and cur_postion.position.y == adjacent_position.position.y:
                return cur_postion.g + 1

        if cur_postion.position.x - 1 == adjacent_position.position.x \
            and cur_postion.position.y + 1 == adjacent_position.position.y:
                return cur_postion.g + 1.5

        if cur_postion.position.x == adjacent_position.position.x \
            and cur_postion.position.y + 1 == adjacent_position.position.y:
                return cur_postion.g + 1
                
        if cur_postion.position.x + 1 == adjacent_position.position.x \
            and cur_postion.position.y + 1 == adjacent_position.position.y:
                return cur_postion.g + 1.5
        
        print("ERROR: get_g() failed to find a valid g value")
        print(f"cur_postion: {cur_postion.position.x}, {cur_postion.position.y}")
        print(f"adjacent_position: {adjacent_position.position.x}, {adjacent_position.position.y}")

     # Calculate manhattan_distance for movement
    def manhattan_distance(self, target_pos: Position, current_pos: Position) -> int:
        distance = abs(target_pos.x - current_pos.x) + \
            abs(target_pos.y - current_pos.y)

        return distance
