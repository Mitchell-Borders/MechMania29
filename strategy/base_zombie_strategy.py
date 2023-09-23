import random
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.game_state import GameState
from game.character.action.attack_action_type import AttackActionType
from game.character.character_class_type import CharacterClassType
from game.character.character import Character
from game.util.position import Position
from strategy.strategy import Strategy



class BaseZombieStrategy(Strategy):
    

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        # SIMPLE ZOMBIE STRATEGY FOR MOVEMENT, CHANGE!!

        choices = []
        
        # character_ids = []
        # for character_id, moves in possible_moves.items():
        #     if character_id not in character_ids:
        #         character_ids.append(character_ids)
        # game_state[character_ids[0]]

        # GET ALL MOVES FOR A CHARACTER_ID
        
        counter: int = 0 # counter for spliting zombies
        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue
            #print(f"character_id:{character_id}   Moves: {moves}")
            current_pos = game_state.characters[character_id].position # position of current zombie
            # Set positions for starting SPLIT STRAT
            middle_left_pos = Position(35, 50)
            middle_right_pos = Position(65, 50)
            top_middle_pos = Position(50, 30)

            # SPLIT STRAT - DON'T TARGET TRACERS
            if game_state.turn < 30:
                # Split to middle left for first two zombies
                if counter <= 1:
                    move_choice = self.move_to_destination(middle_left_pos, current_pos, moves)
                    choices.append(move_choice)

                # Split to top middle for third zombie
                elif counter == 2:
                    move_choice = self.move_to_destination(top_middle_pos, current_pos, moves)
                    choices.append(move_choice)

                # Split to middle right for last two zombies
                elif counter >= 3 and counter <= 4:
                    move_choice = self.move_to_destination(middle_right_pos, current_pos, moves)
                    choices.append(move_choice)

            # TARGET WEAK STRAT
            else:
                pass
                
            counter += 1
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
            
        return choices
    
    # Calculate manhattan_distance for movement
    def manhattan_distance(self, target_pos: Position, current_pos: Position) -> int:
        distance = abs(target_pos.x - current_pos.x) + abs(target_pos.y - current_pos.y)

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
    
