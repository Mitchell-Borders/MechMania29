from strategy.random_strategy import RandomStrategy
from strategy.simple_human_strategy import SimpleHumanStrategy
from strategy.simple_zombie_mod import SimpleZombieModification
from strategy.simple_zombie_strategy import SimpleZombieStrategy
from strategy.base_zombie_strategy import BaseZombieStrategy
from strategy.base_human_strategy import BaseHumanStrategy
from strategy.stunlock_human_strategy import StunlockHumanStrategy
from strategy.strategy import Strategy


def choose_strategy(is_zombie: bool) -> Strategy:
    if is_zombie:
        return SimpleZombieModification()
    else:
        #return BaseHumanStrategy()
        return StunlockHumanStrategy()
