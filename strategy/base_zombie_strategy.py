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
        # Iterates over a single zombie's possible attacks
        #NEED TO DO:
        # - only assign one append to the choices array in here
        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:
                continue
            
            # humans = []  # holds humans that are in range
            
            
            # # Gather list of humans in range
            # for a in attacks:
            #     if a.type is AttackActionType.CHARACTER:
            #         humans.append(a)
            #         human = game_state.characters[a.attacking_id]

            # for a in attacks:
            #     if a.attacking_id == human.id:
            #         choices.append(a)

            # # Initialize a list of what we can attack
            # attackList : game_state.characters.values() = []

            # Generate hitlist
            hitlist = self.hitlist()

            humans = []
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    
                    human = game_state.characters[a.attacking_id]
                    humans.append(human)
            if not len(humans) == 0: # // attack a target with regards to class and hitpoint
                 for x in humans:
                      for h in hitlist:
                           if x.class_type == h:
                                if x.health == 1:
                                     for a in attacks:
                                         if a.attacking_id == x.id:
                                            choices.append(a)
                                     break
                 if len(choices) == 0: # // attack a target indiscrimate of hit points
                    for x in humans:
                        for h in hitlist:
                            if x.class_type == h:
                                 for a in attacks:
                                      if a.attacking_id == x.id:
                                           choices.append(a)
                                 break
            elif(len(choices) == 0):  # The targets in range must be terrain. May as well attack one.
                choices.append(random.choice(attacks))
            
            
            # # Iterate and get all characters in game_state
            # for i in game_state.characters.values():
                
            #     # For all in chev distance, append it to the attackList
            #     for x in range(-1, 2):
            #          for y in range(-1, 2):
            #             self.find_attack(i, x, y, game_state, character_id, attackList)

            # Choice who to attack based on health and class type, prioritizing people with low hitpoints, then
            # Tracuers, Medics, Marksmen, etc.
            # if not len(attackList) == 0: # // attack a target with regards to class and hitpoint
            #      for x in attackList:
            #           for h in hitlist:
            #                if x.class_type == h:
            #                     if x.health == 1:
            #                          choices.append(AttackAction(character_id, x.id))
            #                          break
            #      if len(choices) == 0: # // attack a target indiscrimate of hit points
            #         for x in attackList:
            #             for h in hitlist:
            #                 if x.class_type == h:
            #                      choices.append(AttackAction(character_id, x.id))
            #                      break
            # elif(len(choices) == 0):  # The targets in range must be terrain. May as well attack one.
            #     choices.append(random.choice(attacks))
        # print("____________________________________________________________________________")
        # print("Choices: " + choices)
        # print("Humans: " + humans)
        # print("AttackList: " + attackList)
        # print('End of decide attacks')
        return choices
    
    # Calculate manhattan_distance for movement
    def manhattan_distance(self, target, pos) -> int:
        distance = abs(target.position.x - pos.x) + abs(target.position.y - pos.y)

        return distance
    
    # Append any character that is not a zombie and is in range for attack to the list
    def find_attack(self, target, x, y, game_state, character_id, attackList):
        target.position.x = target.position.x + x
        target.position.y = target.position.y + y
        if target.position.x == game_state.characters[character_id].position.x and target.position.y == game_state.characters[character_id].position.y and not target.is_zombie: 
            attackList.append(target)
    
    # Create priority list for who to attack first
    def hitlist(self) -> list:
        hitlist: list = [CharacterClassType.TRACEUR,
        CharacterClassType.MEDIC,
        CharacterClassType.MARKSMAN,
        CharacterClassType.BUILDER,
        CharacterClassType.DEMOLITIONIST,
        CharacterClassType.NORMAL]
        
        return hitlist
    
