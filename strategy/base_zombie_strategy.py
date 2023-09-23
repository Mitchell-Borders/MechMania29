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

    # method to decide move choice
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
        already_targeted_human_ids = [] 
        counter: int = 0  # counter for spliting zombies
        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue
            # print(f"character_id:{character_id}   Moves: {moves}")
            # position of current zombie
            current_pos = game_state.characters[character_id].position
            # Set positions for starting SPLIT STRAT
            middle_left_pos = Position(30, 65)
            middle_right_pos = Position(70, 65)
            top_middle_pos = Position(50, 50)

            # SPLIT STRAT - DON'T TARGET TRACERS
            if game_state.turn < 30:
                # Split to middle left for first zombie
                if counter == 0:
                    move_choice = self.move_to_destination(
                        middle_left_pos, current_pos, moves)
                    choices.append(move_choice)

                # Split to middle right for last zombie
                elif counter == 4:
                    move_choice = self.move_to_destination(
                        middle_right_pos, current_pos, moves)
                    choices.append(move_choice)
            
            if game_state.turn < 18:
                # Split to middle for three zombies
                if counter >= 1 and counter <= 3:
                    move_choice = self.move_to_destination(
                        top_middle_pos, current_pos, moves)
                    choices.append(move_choice)

            # TARGET WEAK STRAT
            else:

                # Determine if human and within manhattan distance of 6
                characters = game_state.characters.values()
                humans = filter(lambda c: not c.is_zombie, characters)
                # sort humans by class type where self.hitlist() is the priority
                #humans = sorted(humans, key=lambda h: self.hitlist()[::-1].index(h.class_type))
                #print(f"humans sorted: {humans}")
                # sort characters by health, lowest health first
                humans = sorted(humans, key=lambda h: h.health)

                # get the closest human to the zombie
                closest_human = sorted(
                    humans, key=lambda h: self.manhattan_distance(h.position, current_pos))[0]

                # reverse the hitlist so that we target the weakest first
                hitlistWeak = self.hitlist()
                hitlistWeak.pop()
                # create a list of already targeted humans so multiple zombies don't chase the same human
                               # priority: little distance, little health (sorted), weak class_type
                for c in humans:
                    # if there are less than 7 humans left, reset the already_targeted_human_ids list so we can swarm humans
                    if len(humans) < 7:
                         already_targeted_human_ids = []
                    distance = self.manhattan_distance(
                        c.position, current_pos)
                    if distance <= 6:
                       # for h in hitlistWeak:
                           # if c.class_type == h:
                                # print(f"already targeted: {already_targeted_human_ids}")
                           
                                if c.id in already_targeted_human_ids:
                                    # print(f"already targeted: {c.id}")
                                    # print(f"already targeted: {already_targeted_human_ids}")
                                    continue
                                move_choice = self.move_to_destination(
                                    c.position, current_pos, moves)
                                already_targeted_human_ids.append(c.id)
                                choices.append(move_choice)
                                break
                    elif distance > 6 and distance <= 12:
                        #for h in hitlistWeak:
                           # if c.class_type == h:
                                if c.id in already_targeted_human_ids:
                                    continue
                                move_choice = self.move_to_destination(
                                    c.position, current_pos, moves)
                                already_targeted_human_ids.append(c.id)
                                choices.append(move_choice)
                                break
                    elif distance > 12 and distance <= 24:
                       # for h in hitlistWeak:
                          #  if c.class_type == h:
                                if c.id in already_targeted_human_ids:
                                    continue
                                move_choice = self.move_to_destination(
                                    c.position, current_pos, moves)
                                already_targeted_human_ids.append(c.id)
                                choices.append(move_choice)
                                break
                    # if no human within distance of 24 and no choice made, target closest human
                    else:
                        if c.id in already_targeted_human_ids:
                            continue
                        move_choice = self.move_to_destination(
                            closest_human.position, current_pos, moves)
                        already_targeted_human_ids.append(c.id)
                        choices.append(move_choice)

            counter += 1

        return choices

    # method to decide attack choice
    def decide_attacks(
            self,
            possible_attacks: dict[str, list[AttackAction]],
            game_state: GameState
    ) -> list[AttackAction]:

        choices = []  # our attack
        # Iterates over a single zombie's possible attacks
        # NEED TO DO:
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
            if not len(humans) == 0:  # // attack a target with regards to class and hitpoint
                for x in humans:
                    for h in hitlist:
                        if x.class_type == h:
                            if x.health == 1:
                                for a in attacks:
                                    if a.attacking_id == x.id:
                                        choices.append(a)
                                break
                if len(choices) == 0:  # // attack a target indiscrimate of hit points
                    for x in humans:
                        for h in hitlist:
                            if x.class_type == h:
                                for a in attacks:
                                    if a.attacking_id == x.id:
                                        choices.append(a)
                                break
            # The targets in range must be terrain. May as well attack one.
            elif (len(choices) == 0):
                choices.append(random.choice(attacks))

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

        return hitlist[::-1]
