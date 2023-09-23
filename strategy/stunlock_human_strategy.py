# This is a complex human stratagy:
# 5 Marksman, 5 Medics, 5 Traceurs, and one builder.
# Pile on one tile. Move toward the zombies.
# Specifically stay 7 tiles away from the closest zombie.
# When the zombie gets within 6 tiles of us, move toward it and attack.
# Make sure attacks arent wasted, staggering them to achieve a stunlock.
# The hope is that all zombies get trapped in a state of stunlock.
# When the base model is complete, work on making this resiliant to staggered zombie stratagies.
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


class StunlockHumanStrategy(Strategy):
    def decide_character_classes(
            self,
            possible_classes: list[CharacterClassType],
            num_to_pick: int,
            max_per_same_class: int,
            ) -> dict[CharacterClassType, int]:
        # The maximum number of special classes we can choose is 16
        # Selecting 6 Marksmen, 6 Medics, and 4 Traceurs
        # The other 4 humans will be regular class
        choices = {
            CharacterClassType.MARKSMAN: 5,
            CharacterClassType.MEDIC: 5,
            CharacterClassType.TRACEUR: 5,
            CharacterClassType.BUILDER: 1,
        }
        return choices

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        choices = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue


            pos = game_state.characters[character_id].position  # position of the human
            closest_zombie_pos = pos  # default position is zombie's pos
            closest_zombie_distance =  1234  # large number, map isn't big enough to reach this distance
            farthest_zombie_pos = pos
            farthest_zombie_distance = 0

            # Iterate through every zombie to find the closest one
            for c in game_state.characters.values():
                if not c.is_zombie:
                    continue  # Fellow humans are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y)  # calculate manhattan distance between human and zombie
                if distance < closest_zombie_distance:  # If distance is closer than current closest, replace it!
                    closest_zombie_pos = c.position
                    closest_zombie_distance = distance

            for c in game_state.characters.values():
                if not c.is_zombie:
                    continue  # Fellow humans are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y)  # calculate manhattan distance between human and zombie
                if distance > farthest_zombie_distance:  # If distance is bigger than current farthest, replace it!
                    farthest_zombie_pos = c.position
                    farthest_zombie_distance = distance

# // End block collecting data.
# // Start block moving to defense loctation.

            move_choice = moves[0]

            if game_state.turn < 27:
                if game_state.turn == 2:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 50:
                            move_choice = m
                elif game_state.turn == 4:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 53:
                            move_choice = m
                elif game_state.turn == 6:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 56:
                            move_choice = m
                elif game_state.turn == 8:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 59:
                            move_choice = m
                elif game_state.turn == 10:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 62:
                            move_choice = m
                elif game_state.turn == 12:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 65:
                            move_choice = m
                elif game_state.turn == 14:
                    for m in moves:
                        if m.destination.x == 50 and m.destination.y == 68:
                            move_choice = m
                elif game_state.turn == 16:
                    for m in moves:
                        if m.destination.x == 47 and m.destination.y == 68:
                            move_choice = m
                elif game_state.turn == 18:
                    for m in moves:
                        if m.destination.x == 44 and m.destination.y == 68:
                            move_choice = m
                elif game_state.turn == 20:
                    for m in moves:
                        if m.destination.x == 41 and m.destination.y == 68:
                            move_choice = m
                elif game_state.turn == 22:
                    for m in moves:
                        if m.destination.x == 41 and m.destination.y == 71:
                            move_choice = m
                elif game_state.turn == 24:
                    for m in moves:
                        if m.destination.x == 41 and m.destination.y == 74:
                            move_choice = m
                elif game_state.turn == 26:
                    for m in moves:
                        if m.destination.x == 41 and m.destination.y == 76:
                            move_choice = m
                
                choices.append(move_choice)



# // End block moving to defense location.
# // Start block looking for zombies in distance.

            move_distance = 7  # Distance between the move action's destination and the closest zombie
            move_choice = moves[0]  # The move action the human will be taking


        # // If you want to make it more robust, look at farthest zombie distance
            if closest_zombie_distance <= 6:
                for m in moves:
                    distance = abs(m.destination.x - closest_zombie_pos.x) + abs(m.destination.y - closest_zombie_pos.y)

                    if distance < move_distance and distance > 0: # // If the manhattan distance is less than the closest move found, choose that one.
                        move_distance = distance
                        move_choice = m
            
                choices.append(move_choice)
            
        return choices

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:
        choices = []

        attacked_zombie = []

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the human
            farthest_zombie = None  # Closest zombie in range
            farthest_zombie_distance = 0  # Distance between closest zombie and human
            
            # Iterate through zombies in range and find the farthest unstunned one
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    attackee_pos = game_state.characters[a.attacking_id].position  # Get position of zombie in question

                    distance = abs(attackee_pos.x - pos.x) + abs(attackee_pos.y - pos.y)  # Get distance between the two

                    plsHit = True
                    for i in attacked_zombie:
                        if i.id == a.attacking_id:
                            plsHit = False
                        print(i.id)

                    if distance > farthest_zombie_distance and plsHit:  # Farther than current and is not stunned? New target!
                        farthest_zombie = a
                        farthest_zombie_distance = distance
            
            attacked_zombie.append(game_state.characters[farthest_zombie.attacking_id])

            if farthest_zombie is not None:  # Attack the farthest unstunned zombie, if there is one
                choices.append(farthest_zombie)

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

            # Since we only have medics, the choices must only be healing a nearby human
            # human_target = abilities[0]  # the human that'll be healed
            # least_health = 999  # The health of the human being targeted

            # for a in abilities:
            #     health = game_state.characters[a.character_id_target].health  # Health of human in question

            #     if health < least_health:  # If they have less health, they are the new patient!
            #         human_target = a
            #         least_health = health

            # if human_target:  # Give the human a cookie
            #     choices.append(human_target)
        
        return choices
