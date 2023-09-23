import random
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.game_state import GameState
from game.character.action.attack_action_type import AttackActionType
from game.character.character_class_type import CharacterClassType
from game.character.character import Character
from strategy.strategy import Strategy



class BaseZombieStrategy(Strategy):
    

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        # SIMPLE ZOMBIE STRATEGY FOR MOVEMENT, CHANGE!!

        choices = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the zombie
            closest_human_pos = pos  # default position is zombie's pos
            closest_human_distance = 1984  # large number, map isn't big enough to reach this distance

            # Iterate through every human to find the closest one
            for c in game_state.characters.values():
                if c.is_zombie:
                    continue  # Fellow zombies are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y) # calculate manhattan distance between human and zombie
                if distance < closest_human_distance:  # If distance is closer than current closest, replace it!
                    closest_human_pos = c.position
                    closest_human_distance = distance

            # Move as close to the human as possible
            move_distance = 1337  # Distance between the move action's destination and the closest human
            move_choice = moves[0]  # The move action the zombie will be taking
            for m in moves:
                distance = abs(m.destination.x - closest_human_pos.x) + abs(m.destination.y - closest_human_pos.y)  # calculate manhattan distance

                # If distance is closer, that's our new choice!
                if distance < move_distance:  
                    move_distance = distance
                    move_choice = m

            choices.append(move_choice)  # add the choice to the list

        return choices

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:

        choices = [] # our attack

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:
                continue

            humans = []  # holds humans that are in range

            # Gather list of humans in range
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    humans.append(a)

            # Initialize a list of what we can attack
            attackList = []

            # Generate hitlist
            hitlist = self.hitlist()

            
            # Iterate and get all characters in game_state
            for i in game_state.characters.values():
                
                # For all in chev distance, append it to the attackList
                for x in range(-1, 2):
                     for y in range(-1, 2):
                        attackList.append(self.find_attack(i, x, y, game_state, character_id, attackList))

            # Choice who to attack based on health and class type, prioritizing people with low hitpoints, then
            # Tracuers, Medics, Marksmen, etc.
            if not len(humans) == 0: # // attack a target with regards to class and hitpoint
                 for x in humans:
                      for hitlist_index, h in enumerate(hitlist):
                           if x.class_type == hitlist[hitlist_index]:
                                if x.health == 1:
                                     choices.append(AttackAction(character_id, x.id))
                                     break
                 if len(choices) == 0: # // attack a target indiscrimate of hit points
                    for x in attackList:
                        for hitlist_index, h in enumerate(hitlist):
                            if x.class_type == hitlist[hitlist_index]:
                                 choices.append(AttackAction(character_id, x.id))
            elif(len(choices) == 0):  # The targets in range must be terrain. May as well attack one.
                choices.append(random.choice(attacks))
        print("____________________________________________________________________________")
        print("Choices: " + choices)
        print("Humans: " + humans)
        print("AttackList: " + attackList)
        print('End of decide attacks')
        return choices
    
    # Calculate manhattan_distance for movement
    def manhattan_distance(self, target, pos) -> int:
        distance = abs(target.position.x - pos.x) + abs(target.position.y - pos.y)

        return distance
    
    # Append any character that is not a zombie and is in range for attack to the list
    def find_attack(self, target, x, y, game_state, character_id, attackList) -> list:
        target.position.x = target.position.x + x
        target.position.y = target.position.y + y
        if (target.position) == game_state.characters[character_id].position and not target.is_zombie: 
            attackList.append(target)
        return attackList
    
    # Create priority list for who to attack first
    def hitlist(self) -> list:
        hitlist: list = [CharacterClassType.TRACEUR,
        CharacterClassType.MEDIC,
        CharacterClassType.MARKSMAN,
        CharacterClassType.BUILDER,
        CharacterClassType.DEMOLITIONIST,
        CharacterClassType.NORMAL]
        
        return hitlist
    
