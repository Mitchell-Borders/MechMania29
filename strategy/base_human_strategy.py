# 5 Marksman, 5 Medics, and 5 Traceurs, 1 Builder
# Move as far away from the closest zombie as possible
# If there are any zombies in attack range, attack the closest
# If a Medic's ability is available, heal a human in range with the least health

import random
from game.character.action.ability_action import AbilityAction
from game.character.action.ability_action_type import AbilityActionType
from game.character.action.attack_action import AttackAction
from game.character.action.attack_action_type import AttackActionType
from game.character.action.move_action import MoveAction
from game.character.character_class_type import CharacterClassType
from game.game_state import GameState
from game.util.position import Position
from strategy.strategy import Strategy


class BaseHumanStrategy(Strategy):
    def decide_character_classes(
            self,
            possible_classes: list[CharacterClassType],
            num_to_pick: int,
            max_per_same_class: int,
            ) -> dict[CharacterClassType, int]:
        # The maximum number of special classes we can choose is 16
        # Selecting 5 Marksmen, 5 Medics, 5 Traceurs, 1 Builder
        # The other 4 humans will be regular class
        choices = {
            CharacterClassType.MARKSMAN: 5,
            CharacterClassType.MEDIC: 5,
            CharacterClassType.TRACEUR: 5,
            CharacterClassType.BUILDER: 1
        }
        return choices

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        choices = []

        counter: int = 0 # counter for spliting humans  in initial phase

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            # get current position of human
            current_pos = game_state.characters[character_id].position

            # Set positions to run to
            middle_left_pos: Position = Position(30, 50)
            middle_right_pos: Position = Position(70, 50)
            bottom_middle_pos: Position = Position(50, 65)
            bottom_left_pos: Position = Position(35, 70)
            bottom_right_pos: Position = Position(65, 70)
            far_left_pos: Position = Position(0, 70)
            far_right_pos: Position = Position(99, 70)

            # holder for selected distracting tracuer
            distract = None


            # if not character_id == leftToken and not character_id == rightToken:
                # SPLIT STRAT (LOTS OF HARD CODE, KINDA WANNA CHANGE IT)
                    

            if game_state.turn <= 8:
                if counter <= 5:
                    move_choice = self.move_to_destination(middle_left_pos, current_pos, moves)
                    choices.append(move_choice)
                elif counter >= 6 and counter <= 10:
                    move_choice = self.move_to_destination(middle_right_pos, current_pos, moves)
                    choices.append(move_choice)
                else:
                    move_choice = self.move_to_destination(bottom_middle_pos, current_pos, moves)
                    choices.append(move_choice)
                
            elif game_state.turn >= 9 and game_state.turn <= 16:
                if counter <= 5 or (counter >= 11 and counter <= 15):
                    move_choice = self.move_to_destination(bottom_left_pos, current_pos, moves)
                    choices.append(move_choice)
                else:
                    move_choice = self.move_to_destination(bottom_right_pos, current_pos, moves)
                    choices.append(move_choice)

            elif game_state.turn >= 17 and game_state.turn <= 24:
                if counter <= 5 or (counter >= 11 and counter <= 15):
                    move_choice = self.move_to_destination(far_left_pos, current_pos, moves)
                    choices.append(move_choice)
                else:
                    move_choice = self.move_to_destination(far_right_pos, current_pos, moves)
                    choices.append(move_choice)

            # SCATTER STRAT
            else:
                closest_zombie_pos = current_pos
                closest_human_pos = current_pos  
                closest_zombie_distance =  1234
                closest_human_distance = 1234
                closest_zombie_to_closest_human_pos = current_pos
                closest_zombie_to_closest_human_distance = 1234
                

                # Iterate through every zombie to find the closest one
                for c in game_state.characters.values():

                    # get distance from character
                    distance = self.manhattan_distance(c.position, current_pos) 
                    
                    # get closest zombie position
                    if c.is_zombie and distance < closest_zombie_distance: 
                        closest_zombie_pos = c.position
                        closest_zombie_distance = distance

                    # get closest human position
                    if not c.is_zombie and distance < closest_human_distance:
                        closest_human_pos = c.position
                        closest_human_distance = distance
                        for c in game_state.characters.values():
                            if c.is_zombie and distance < closest_zombie_to_closest_human_distance:
                                closest_zombie_to_closest_human_pos = c.position
                                closest_zombie_to_closest_human_distance = distance

                # Move as far away from either the zombie or human as possible
                move_distance = -1  # Distance between the move action's destination and the closest zombie
                move_choice = moves[0]  # The move action the human will be taking

                for m in moves:
                    if closest_zombie_distance < 25 or game_state.characters[character_id].class_type == CharacterClassType.TRACEUR:
                        distance = self.manhattan_distance(m.destination, closest_zombie_pos)
                    elif closest_zombie_to_closest_human_distance < closest_zombie_distance:
                        distance = self.manhattan_distance(m.destination, closest_zombie_to_closest_human_pos)
                    else:
                        distance = self.manhattan_distance(m.destination, closest_human_pos)

                    if distance > move_distance:  # If distance is further, that's our new choice!
                        move_distance = distance
                        move_choice = m

                choices.append(move_choice)  # add the choice to the list

            counter += 1

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

            current_pos = game_state.characters[character_id].position  # position of the human
            closest_zombie = None  # Closest zombie in range
            closest_zombie_distance = 404  # Distance between closest zombie and human

            # Iterate through zombies in range and find the closest one
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    # if the zombie is stunned, ignore
                    if game_state.characters[a.attacking_id].is_stunned:
                        continue

                    attackee_pos = game_state.characters[a.attacking_id].position  # Get position of zombie in question

                    distance = self.manhattan_distance(attackee_pos, current_pos)

                    if distance < closest_zombie_distance:  # Closer than current? New target!
                        closest_zombie = a
                        closest_zombie_distance = distance

            if closest_zombie:  # Attack the closest zombie, if there is one
                choices.append(closest_zombie)

        return choices

    def decide_abilities(
            self, 
            possible_abilities: dict[str, list[AbilityAction]], 
            game_state: GameState
            ) -> list[AbilityAction]:
        choices = []

        for [character_id, abilities] in possible_abilities.items():
            if len(abilities) == 0:  # No choices? Next!
                continue

            target = abilities[0]  # the human that'll be healed
            least_health = 999  # The health of the human being targeted

            for a in abilities:
                # heal someone with least health in range
                if a.type == AbilityActionType.HEAL:
                    health = game_state.characters[a.character_id_target].health

                    if health < least_health:  # If they have less health, they are the new patient!
                        target = a
                        least_health = health

                # place barricade randomly
                elif a.type == AbilityActionType.BUILD_BARRICADE:
                    target = random.choice(abilities)

            if target:
                choices.append(target)
        
        return choices
    
    # Calculate manhattan_distance for movement
    def manhattan_distance(self, target_pos: Position, current_pos: Position) -> int:
        distance = abs(target_pos.x - current_pos.x) + \
            abs(target_pos.y - current_pos.y)

        return distance

    # Method to choose destination to move to
    def move_to_destination(self, target_pos: Position, current_pos: Position, moves: list[MoveAction]) -> MoveAction:
        move_distance = 1337
        move_choice = moves[0]  # The move action the zombie will be taking
        for m in moves:
            distance = self.manhattan_distance(m.destination, target_pos)
            # If distance is closer, that's our new choice!
            if distance < move_distance:
                move_distance = distance
                move_choice = m
        return move_choice
