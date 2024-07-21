import math
import random
from enum import IntEnum
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Constants.
BASE_HP = 300
BASE_DEF = 205
BASE_OFF = 390
BASE_STR = 20

# Parameters for scaling calculations.
PLAYER_HP_INCREMENT = 300
OFF_BASE_ADJUSTMENT = 100
OFF_SCALING_MULTIPLIER = 7
DEF_BASE_ADJUSTMENT = 100
DEF_SCALING_MULTIPLIER = 7 / 10
CM_HP_MULTIPLIER = 1.5
CM_OFF_MULTIPLIER = 1.5
CM_DEF_MULTIPLIER = 1.2
CM_DEF_MULTIPLIER_HIGHER_SCALES = 1.35
VENGE_DAMAGE_MULTIPLIER = 0.75

# Settings.
NUMBER_OF_PLAYERS = 5
CHALLENGE_MODE = True
CLOSE_LURE = True
CROSS_REBGS_THRESHOLD = 75
TELEGRAB_REBGS_THRESHOLD = 20
DEF_LEAVE_THRESHOLD = 50
# Choose from the tick Tekton needs to die on to stay: 16 (<24s), 20 (<26.4s), 24 (<28.8s), 28 (<31.2s), 32 (<33.6s), etc.
# Set high to not leave any.
CUTOFF_TICK = 28
# Choose what time is considered runable: 24, 26.4, 28.8, 31.2, etc.
RUNABLE_TIME = 28.8

# Function to calculate scaled HP.
def calculate_scaled_hp(base_hp, num_players, challenge_mode):
    scaled_hp = math.floor(base_hp + (num_players // 2 * PLAYER_HP_INCREMENT))
    if challenge_mode:
        scaled_hp = math.floor(scaled_hp * CM_HP_MULTIPLIER)
    return scaled_hp

# Function to calculate scaled DEF.
def calculate_scaled_def(base_def, num_players, challenge_mode):
    sqrt_term = math.floor(math.sqrt(num_players - 1))
    linear_term = math.floor((num_players - 1) * DEF_SCALING_MULTIPLIER)
    scaled_def = math.floor(base_def * ((sqrt_term + linear_term + DEF_BASE_ADJUSTMENT) / DEF_BASE_ADJUSTMENT))
    if challenge_mode:
        if num_players > 3:
            scaled_def = math.floor(scaled_def * CM_DEF_MULTIPLIER_HIGHER_SCALES)
        else:
            scaled_def = math.floor(scaled_def * CM_DEF_MULTIPLIER)
    return scaled_def

# Function to calculate scaled Max hit.
def calculate_scaled_max(base_off, num_players, challenge_mode):
    sqrt_term = math.floor(math.sqrt(num_players - 1))
    scaled_off = math.floor(base_off * (sqrt_term * OFF_SCALING_MULTIPLIER + (num_players - 1) + OFF_BASE_ADJUSTMENT) / OFF_BASE_ADJUSTMENT)
    if challenge_mode:
        scaled_off = math.floor(scaled_off * CM_OFF_MULTIPLIER)
    scaled_max = math.floor((math.floor((scaled_off + 9) * (BASE_STR + 64) / 64) + 5) / 10)
    return scaled_max

# Calculate the scaled HP, DEF and Max hit.
hitpoints = calculate_scaled_hp(BASE_HP, NUMBER_OF_PLAYERS, CHALLENGE_MODE)
defence = calculate_scaled_def(BASE_DEF, NUMBER_OF_PLAYERS, CHALLENGE_MODE)
maxhit = calculate_scaled_max(BASE_OFF, NUMBER_OF_PLAYERS, CHALLENGE_MODE)
initial_defence = defence

# Scythe style bonus.
class Style(IntEnum):
    STAB = 155
    SLASH = 165
    CRUSH = 105

# Class to create a Tekton instance.
class Tekton():
    def __init__(self, hp, defence, maxhit):
        self.hp = hp
        self.defence = defence
        self.maxhit = maxhit
        self.initial_defence = defence
        self.burn_stacks = 0
        self.burn_cooldown = 0

    def get_hp(self):
        return self.hp
    
    def get_defence(self):
        return self.defence
    
    def get_initialdefence(self):
        return self.initial_defence

    def take_damage(self, amount):
        self.hp -= amount
    
    def reduce_defence(self, amount):
        self.defence -= amount

    def do_venge_damage(self, melee_pray):
        if melee_pray:
            return random.randint(1, math.floor(self.maxhit / 2))
        else:
            return random.randint(1, self.maxhit)
        
    def apply_burn(self, stacks):
        self.burn_stacks = min(self.burn_stacks + stacks, 5)

    def do_burn_damage(self):
        self.hp -= self.burn_stacks
        self.burn_cooldown += 3

    def get_stats(self):
        """
        Display the current health, defence and max hit of the Tekton.
        
        :return: str - A formatted string showing the current HP and defence.
        """
        return f'HP: {self.hp}, Defence: {self.defence}, Max hit: {self.maxhit}'

# Dictionaries to store player accuracy and max hits.
ACCURACY_MAX_VALUES = {
    'ovl': {
        'torva': {
            'torture': {
                'ultor': {
                    'maul': {'acc': 36580, 'max': 67},
                    'bgs': {'acc': 35416, 'max': 78},
                    'scythe': {'acc': 34352, 'max': 51},
                    'claws': {'acc': 24016, 'max': 45}
                },
                'bellator': {
                    'maul': {'acc': 36580, 'max': 66},
                    'bgs': {'acc': 38456, 'max': 75},
                    'scythe': {'acc': 37392, 'max': 49},
                    'claws': {'acc': 27056, 'max': 44}
                },
                'lightbearer': {
                    'maul': {'acc': 36580, 'max': 64},
                    'bgs': {'acc': 35416, 'max': 74},
                    'scythe': {'acc': 34352, 'max': 48},
                    'claws': {'acc': 24016, 'max': 42}
                }
            },
            'rancour': {

            },
            'fury': {

            }
        },
        'inq': {
            'torture': {
                'ultor': {
                    'maul': {'acc': 42578, 'max': 66},
                    'bgs': {'acc': 33185, 'max': 77},
                    'scythe': {'acc': 25395, 'max': 50},
                    'claws': {'acc': 22800, 'max': 43}
                },
                'bellator': {
                    'maul': {'acc': 42578, 'max': 65},
                    'bgs': {'acc': 33185, 'max': 74},
                    'scythe': {'acc': 25395, 'max': 48},
                    'claws': {'acc': 25840, 'max': 42}
                },
                'lightbearer': {
                    'maul': {'acc': 42578, 'max': 63},
                    'bgs': {'acc': 33185, 'max': 73},
                    'scythe': {'acc': 25395, 'max': 48},
                    'claws': {'acc': 22800, 'max': 40}
                }
            },
            'rancour': {

            },
            'fury': {

            }
        }
    },
    'scb': {
        'torva': {
            'torture': {
                'ultor': {
                    'maul': {'acc': 35872, 'max': 66},
                    'bgs': {'acc': 34717, 'max': 77},
                    'scythe': {'acc': 33674, 'max': 50},
                    'claws': {'acc': 23542, 'max': 45}
                },
                'bellator': {
                    'maul': {'acc': 35872, 'max': 65},
                    'bgs': {'acc': 37697, 'max': 75},
                    'scythe': {'acc': 36654, 'max': 49},
                    'claws': {'acc': 27056, 'max': 43}
                },
                'lightbearer': {
                    'maul': {'acc': 35872, 'max': 64},
                    'bgs': {'acc': 34717, 'max': 73},
                    'scythe': {'acc': 33674, 'max': 47},
                    'claws': {'acc': 23542, 'max': 42}
                }
            },
            'rancour': {
                'ultor': {
                    'maul': {'acc': 37392, 'max': 67},
                    'bgs': {'acc': 36207, 'max': 78},
                    'scythe': {'acc': 35164, 'max': 51},
                    'claws': {'acc': 25032, 'max': 45}
                },
                'bellator': {
                    'maul': {'acc': 37392, 'max': 66},
                    'bgs': {'acc': 39187, 'max': 75},
                    'scythe': {'acc': 38144, 'max': 49},
                    'claws': {'acc': 28012, 'max': 44}
                },
                'lightbearer': {
                    'maul': {'acc': 37392, 'max': 64},
                    'bgs': {'acc': 36207, 'max': 74},
                    'scythe': {'acc': 35164, 'max': 48},
                    'claws': {'acc': 25032, 'max': 42}
                }

            },
            'fury': {

            }
        },
        'inq': {
            'torture': {
                'ultor': {
                    'maul': {'acc': 41754, 'max': 66},
                    'bgs': {'acc': 32530, 'max': 75},
                    'scythe': {'acc': 24894, 'max': 49},
                    'claws': {'acc': 22350, 'max': 43}
                },
                'bellator': {
                    'maul': {'acc': 41754, 'max': 64},
                    'bgs': {'acc': 32530, 'max': 74},
                    'scythe': {'acc': 24894, 'max': 48},
                    'claws': {'acc': 25840, 'max': 41}
                },
                'lightbearer': {
                    'maul': {'acc': 41754, 'max': 63},
                    'bgs': {'acc': 32530, 'max': 72},
                    'scythe': {'acc': 24894, 'max': 46},
                    'claws': {'acc': 22350, 'max': 40}
                }
            },
            'rancour': {
                'ultor': {
                    'maul': {'acc': 43312, 'max': 66},
                    'bgs': {'acc': 34057, 'max': 77},
                    'scythe': {'acc': 26421, 'max': 50},
                    'claws': {'acc': 23840, 'max': 43}
                },
                'bellator': {
                    'maul': {'acc': 43312, 'max': 65},
                    'bgs': {'acc': 34057, 'max': 74},
                    'scythe': {'acc': 26421, 'max': 48},
                    'claws': {'acc': 26820, 'max': 42}
                },
                'lightbearer': {
                    'maul': {'acc': 43312, 'max': 63},
                    'bgs': {'acc': 34057, 'max': 73},
                    'scythe': {'acc': 26421, 'max': 47},
                    'claws': {'acc': 23840, 'max': 40}
                }
            },
            'fury': {

            }
        }
    }
}

# Simulates an accuracy roll.
def sim_acc(tekton, style, maxAttRoll):
    maxDefRoll = int((9 + tekton.defence) * (64 + style.value))
    if maxAttRoll > maxDefRoll:
        accuracy = 1 - (maxDefRoll + 2) / (2 * (maxAttRoll + 1))
    else:
        accuracy = maxAttRoll / (2 * (maxDefRoll + 1))
    return accuracy

# Performs a scythe attack against Tekton.
def do_scythe(tekton, style, maxAttRoll, maxHit):
    accuracy = sim_acc(tekton, style, maxAttRoll)
    hits = 0
    for x in range(0, 3):
        accuracy_rand = random.uniform(0, 1)
        hit = int(random.randint(0, maxHit) / max(1, x * 2))
        if hit == 0: hit = 1 # REBALANCE UPDATE
        if accuracy >= accuracy_rand:
            hits += hit
    tekton.hp -= hits
    return

# Performs an elder maul attack against Tekton.
def do_maul(tekton, maxAttRoll, maxHit):
    accuracy = sim_acc(tekton, Style.CRUSH, maxAttRoll)
    accuracy_rand = random.uniform(0, 1)
    hit = random.randint(0, maxHit)
    if tekton.defence == tekton.initial_defence:
        tekton.defence = math.ceil(tekton.defence * 0.65)
        tekton.hp -= hit
        return
    if accuracy >= accuracy_rand:
        tekton.defence = math.ceil(tekton.defence * 0.65)
        tekton.hp -= hit
        return
    else:
        tekton.defence = math.ceil(tekton.defence * 0.95)
        return
    
# Performs a bgs attack against Tekton.
def do_bgs(tekton, maxAttRoll, maxHit):
    accuracy = sim_acc(tekton, Style.SLASH, maxAttRoll)
    accuracy_rand = random.uniform(0, 1)
    hit = random.randint(0, maxHit)
    if hit == 0: hit = 1 # REBALANCE UPDATE
    if accuracy >= accuracy_rand:
        tekton.defence -= hit
        tekton.hp -= hit
    else:
        tekton.defence -= 10
    # Make sure defence never goes below 0   
    if tekton.defence < 0:
        tekton.defence = 0
    return

# Performs a claw attack against Tekton.
def do_claw(tekton, maxAttRoll, maxHit):
    maxDefRoll = (int)((9 + tekton.defence) * (64 + Style.SLASH))
    if (rnd(maxAttRoll) > rnd(maxDefRoll)):
        one = int(rnd(int(maxHit), int(maxHit/2)))
        two = int(one/2)
        three = int(two/2)
        four = int(three+1)
        hit = one + two + three + four
        tekton.hp -= hit
        return
    elif (rnd(maxAttRoll) > rnd(maxDefRoll)):
        one = int(rnd(int(7*maxHit/8), int(3*maxHit/8)))
        two = int(one/2)
        three = int(two+1)
        hit = one + two + three
        tekton.hp -= hit
        return
    elif (rnd(maxAttRoll) > rnd(maxDefRoll)):
        one = int(rnd(int(3*maxHit/4), int(maxHit/4)))
        two = int(one+1)
        hit = one + two
        tekton.hp -= hit
        return
    elif (rnd(maxAttRoll) > rnd(maxDefRoll)):
        hit = int(rnd(int(5*maxHit/4), int(maxHit/4)))
        tekton.hp -= hit
        return
    else:
        if (rnd(1) != 0):
            tekton.hp -= 2
            return
        else:
            return

# NOT DONE        
def do_bone_claw(tekton, maxAttRoll, maxHit):
    accuracy = sim_acc(tekton, Style.SLASH, maxAttRoll)
    burn_chance = 0
    hits = 0
    for x in range(0, 3):
        accuracy_rand = random.uniform(0, 1)
        if x > 0:
            hit = math.floor(random.randint(0, maxHit) / 2)
        else:
            hit = random.randint(0, maxHit)
        if hit == 0: hit = 1 # REBALANCE UPDATE
        if accuracy >= accuracy_rand:
            burn_chance += 0.15
            hits += hit
    tekton.hp -= hits

# Helper function for the claw attack function.
def rnd(n, m = 0):
    return random.randint(m, n)

# Simulates a thrall attack based on the provided thrall tier.
def sim_thrall(tekton, tier):
    match tier:
        case 1:
            tekton.hp -= random.randint(0, 1)
            return
        case 2:
            tekton.hp -= random.randint(0, 2)
            return
        case 3:
            tekton.hp -= random.randint(0, 3)
            return

# Class to create a Raider instance.
class Raider:
    def __init__(self, pid, name, hp, armour, specwep, claws, amulet, ring, boost, energy, thrall, delay, thrallTier=3, vengeAmount=0, meleePray=False, re_bgs_threshold=0, start_with_scythe=False):
        self.pid = pid
        self.name = name
        self.hp = hp
        self.armour = armour
        self.specwep = specwep
        self.claws = claws
        self.amulet = amulet
        self.ring = ring
        self.boost = boost
        self.energy = energy
        self.thrall = thrall
        self.delay = delay
        self.thrallTier = thrallTier
        self.vengeAmount = vengeAmount
        self.meleePray = meleePray
        self.re_bgs_threshold = re_bgs_threshold
        self.start_with_scythe = start_with_scythe
        self.cooldown = 0
        self.thrallCooldown = 1 # Not 0, because it never spawns adjecent to the boss
        self.acc = None
        self.max = None
        self.hasSpecced = False
        self.set_delayed_attack()

    # Set the weapon cooldown to an initial delay. Allows for staggered attacks.
    def set_delayed_attack(self):
        self.cooldown = self.delay

    # Sets the Raider's accuracy and max hit, based on their respective boost, armour, ring and weapon
    def set_acc_and_max(self, spec=False, force_scythe=False):
        try:
            acc_max_values = ACCURACY_MAX_VALUES[self.boost][self.armour][self.amulet][self.ring]

            # Update acc and max based on initial specwep
            if spec:
                self.acc = acc_max_values[self.specwep]['acc']
                self.max = acc_max_values[self.specwep]['max']
            else:
                # Check for claws and update if necessary
                if self.claws and self.energy >= 50 and not force_scythe:
                    claws_values = acc_max_values['claws']
                    self.acc = claws_values['acc']
                    self.max = claws_values['max']
                else:
                    #print(f'Forced scythe: {force_scythe}')
                    scythe_values = acc_max_values['scythe']
                    self.acc = scythe_values['acc']
                    self.max = scythe_values['max']

        except KeyError as e:
            print(f"Error: Missing value for {e}")

    # Simulates an attack for the Raider.
    def attack(self, tekton, re_bgs=False):

        # Lets the Raider do a scythe attack before performing a special attack.
        if self.start_with_scythe:
            self.set_acc_and_max(force_scythe=True)
            if self.armour == 'inq':
                style = Style.CRUSH
            else:
                style = Style.SLASH
            self.cooldown += 4
            #print(f'{self.name} forced scything')
            do_scythe(tekton, style, self.acc, self.max)
            self.start_with_scythe = False
            return

        # Makes the Raider perform a special attack based on their respective spec weapon.
        if not self.hasSpecced and self.energy >= 50 and self.specwep in ['maul', 'bgs']:
            self.set_acc_and_max(spec=True)
            self.energy -= 50
            self.hasSpecced = True
            if self.specwep == 'maul':
                self.cooldown += 5
                #print(f'{self.name} mauling')
                do_maul(tekton, self.acc, self.max)
                return
            elif self.specwep == 'bgs':
                self.cooldown += 5
                #print(f'{self.name} bgsing first time')
                do_bgs(tekton, self.acc, self.max)
                return
            
        # Lets the Raider perform another bgs spec if they're assigned to do so.
        if re_bgs:
            self.set_acc_and_max(spec=True)
            self.energy -= 50
            self.hasSpecced = True
            self.cooldown += 5
            #print(f'{self.name} bgsing again')
            do_bgs(tekton, self.acc, self.max)
            return

        # Makes the Raider perform a claw spec if they have them and will otherwise default to a scythe attack.
        self.set_acc_and_max()
        if self.claws and self.energy >= 50:
            self.cooldown += 3
            self.energy -= 50
            do_claw(tekton, self.acc, self.max)
            return
        else:
            if self.armour == 'inq':
                style = Style.CRUSH
            else:
                style = Style.SLASH
            self.cooldown += 4
            #print(f'{self.name} scything')
            do_scythe(tekton, style, self.acc, self.max)
            return
        
    # Performs a thrall attack if the Raider has one.
    def thrall_attack(self, tekton):
        self.thrallCooldown += 3
        sim_thrall(tekton, self.thrallTier)
        return
    
    # Deals vengeance damage to Tekton if the Raider is venged.
    def venge(self, tekton):
        # Turn on melee pray if tekton can kill you
        if self.hp <= tekton.maxhit:
            self.meleePray = True
        # Don't take venge if tekton can kill you with melee pray on
        if self.hp <= math.floor(tekton.maxhit / 2):
            self.vengeAmount = 0
            return
        
        damage = tekton.do_venge_damage(self.meleePray)
        #print(f"{self.name} venged for {damage}, which damaged Tekton for {max(math.floor(damage * VENGE_DAMAGE_MULTIPLIER), 1)}")
        self.hp -= damage
        tekton.hp -= max(math.floor(damage * VENGE_DAMAGE_MULTIPLIER), 1)
        self.vengeAmount -= 1

# Create a team of Raiders with individual properties.
def createTeam():
    if not CHALLENGE_MODE:
        match NUMBER_OF_PLAYERS:
            case 1:
                return [Raider(pid=random.randint(0,2000), name='TorvaSolo', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=50, thrall=True, delay=0)]
            case 2:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0)]
            case 3:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Telegrab', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=False, delay=0)]
            case 5:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='scb', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Telegrab', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=False, delay=0),
                        Raider(pid=random.randint(0,2000), name='Melee tank', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Mage tank', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0)]
            case 7:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='scb', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Telegrab', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='scb', energy=100, thrall=False, delay=0),
                        Raider(pid=random.randint(0,2000), name='Melee tank', hp=121, armour='torva', specwep=None, claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Mage tank', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='scb', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Leech 1', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Leech 2', hp=121, armour='torva', specwep=None, claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1)]
    else:
        match NUMBER_OF_PLAYERS:
            # Improper setups
            case 1:
                return [Raider(pid=random.randint(0,2000), name='TorvaSolo', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=50, thrall=True, delay=0)]
            # Improper setups
            case 2:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0)]
            # Improper setups
            case 3:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Telegrab', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='ovl', energy=100, thrall=False, delay=0)]
            # Rancour
            case 5:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='bgs', claws=True, amulet='rancour', ring='bellator', boost='scb', energy=100, thrall=False, delay=1, vengeAmount=1, re_bgs_threshold=CROSS_REBGS_THRESHOLD, start_with_scythe=False),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='inq', specwep='maul', claws=True, amulet='rancour', ring='lightbearer', boost='scb', energy=100, thrall=True, thrallTier=2, delay=0, vengeAmount=2),
                        Raider(pid=random.randint(0,2000), name='Telegrab', hp=121, armour='torva', specwep='bgs', claws=False, amulet='rancour', ring='bellator', boost='scb', energy=100, thrall=False, delay=1, vengeAmount=1, re_bgs_threshold=TELEGRAB_REBGS_THRESHOLD, start_with_scythe=False),
                        Raider(pid=random.randint(0,2000), name='Prep', hp=121, armour='torva', specwep='maul', claws=True, amulet='rancour', ring='lightbearer', boost='scb', energy=100, thrall=True, thrallTier=2, delay=0, vengeAmount=2),
                        Raider(pid=random.randint(0,2000), name='Enchangla', hp=121, armour='torva', specwep='maul', claws=True, amulet='rancour', ring='bellator', boost='scb', energy=100, thrall=False, delay=0, vengeAmount=1)]
            # Improper setups
            case 7:
                return [Raider(pid=random.randint(0,2000), name='Cross', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='scb', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Chin', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Telegrab', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='scb', energy=100, thrall=False, delay=0),
                        Raider(pid=random.randint(0,2000), name='Melee tank', hp=121, armour='torva', specwep=None, claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Mage tank', hp=121, armour='torva', specwep='maul', claws=False, ring='ultor', boost='scb', energy=100, thrall=True, delay=0),
                        Raider(pid=random.randint(0,2000), name='Leech 1', hp=121, armour='torva', specwep='bgs', claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1),
                        Raider(pid=random.randint(0,2000), name='Leech 2', hp=121, armour='torva', specwep=None, claws=False, ring='ultor', boost='ovl', energy=100, thrall=True, delay=1)]

# Simulates a Tekton kill.
def killTekton():
    tekton = Tekton(hitpoints, defence, maxhit)
    team = createTeam()
    ticks = 0
    # Overkill not entirely accurate, as Venge is always applied ASAP without missing.
    overkill = False
    # Sort by pid to simulate actual game behaviour
    team.sort(key=lambda r: r.pid)
    while tekton.hp > 0:
        #print(f"tick: {ticks}")
        # Check Tekton's defence for potential re-bgs
        re_bgs_defence = tekton.defence
        for r in team:
            if r.cooldown == 0 and r.re_bgs_threshold > 0 and re_bgs_defence > r.re_bgs_threshold and r.energy >= 50 and r.hasSpecced:
                #print(f"re bgs def: {re_bgs_defence} and threshold: {r.re_bgs_threshold} on {r.name}")
                r.attack(tekton, re_bgs=True)
                # Check if Tekton died on this attack
                if tekton.hp <= 0:
                    overkill = True
                    break
            elif r.cooldown == 0:
                r.attack(tekton)
                # Check if Tekton died on this attack
                if tekton.hp <= 0:
                    overkill = True
                    break
            else:
                r.cooldown -= 1
                
            if r.thrall:
                if r.thrallCooldown == 0:
                    r.thrall_attack(tekton)
                    # Check if Tekton died to thrall
                    if tekton.hp <= 0:
                        overkill = False
                        break
                else:
                    r.thrallCooldown -= 1

            if r.vengeAmount > 0:
                r.venge(tekton)
                # Check if Tekton died to venge
                if tekton.hp <= 0:
                    overkill = False
                    break
        
        ticks += 1
        # Check again to exit the while loop
        if tekton.hp <= 0:
            break
    return ticks, tekton.defence, overkill

# Converts ticks to seconds.        
def ticks_to_seconds(ticks, overkill):
    seconds = []
    adjusted_ticks = round_to_cycle(ticks, overkill)
    for i in adjusted_ticks:
        seconds.append(round(i * 0.6, 1))
    return seconds

# Adjusts and rounds ticks to kill to line up with the game's 4-tick cycle.
def round_to_cycle(ticks, overkill):
    adjusted_ticks = []
    entry_ticks = 11
    death_anim = 4
    crystal_anim = 4
    for index, value in enumerate(ticks):
        #print(f'Starting ticks: {value}')
        # On tick 28 Tekton starts walking back to the anvil, slowing down the death animation.
        if value >= 28 and CLOSE_LURE:
            death_anim = 6
        # Death animation is sped up by overkill.
        elif overkill[index]:
            death_anim = 3
        else:
            death_anim = 4
        adjusted_ticks.append(math.ceil((value + entry_ticks + death_anim) / 4) * 4 + crystal_anim)
        #print(f'Adjusted to: {adjusted_ticks[index]}')
    return adjusted_ticks

# Outputs the simulation results in a graph.
def construct_graph(x, results, leave_rate, run_rate):
    # Note under the title
    note = "rancour, bellator"
    step = 2.4
    results = np.array(results)
    print(results.mean())
    labels, counts = np.unique(results, return_counts=True)
    ax = plt.bar(labels, counts, align='center')
    for rect in ax:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2.0, height, f'{height:.0f}', ha='center', va='bottom')
    fig = plt.gcf()
    fig.set_size_inches(10, 7.5)
    plt.title(f"{x} Tekton simulations\n{note}", fontsize=18, pad=20)
    plt.xticks(np.arange(min(results) - step, max(results) + (step * 3), step=step))
    plt.xlabel("Room times", fontsize=14)
    plt.text(0.80, 0.84, "Mean: " + str(round(results.mean(), 2)), transform=fig.transFigure)
    plt.text(0.80, 0.81, "Mode: " + str(stats.mode(results).mode[0]), transform=fig.transFigure)
    plt.text(0.15, 0.84, f"Raids left: {leave_rate}%", transform=fig.transFigure, fontsize="x-large", color="red")
    plt.text(0.15, 0.81, f"Runable: {run_rate}% (<={RUNABLE_TIME}s)", transform=fig.transFigure, fontsize="large")
    plt.text(0.15, 0.78, f"Defence leave threshold: {DEF_LEAVE_THRESHOLD}", transform=fig.transFigure)
    plt.text(0.15, 0.76, f"Cross re-bgs: {CROSS_REBGS_THRESHOLD}", transform=fig.transFigure)
    plt.text(0.15, 0.74, f"TG re-bgs: {TELEGRAB_REBGS_THRESHOLD}", transform=fig.transFigure)
    plt.show()

# Main function to start the simulator.
def main(x):
    ticks_list = []
    overkill_list = []
    raids_left = 0
    zero_def_count = 0
    runners = 0
    for i in range(x):
        ticks, defence, overkill = killTekton()
        if defence > DEF_LEAVE_THRESHOLD or ticks >= CUTOFF_TICK:
            raids_left += 1
            continue
        if defence <= 0:
            zero_def_count += 1
        ticks_list.append(ticks)
        overkill_list.append(overkill)
    kills_in_seconds = ticks_to_seconds(ticks_list, overkill_list)
    zero_def_rate = round((zero_def_count / x * 100), 2)
    leave_rate = round((raids_left / x * 100), 2)
    for i in kills_in_seconds:
        if i <= RUNABLE_TIME:
            runners += 1
    run_rate = round((runners / x * 100), 2)
    construct_graph(x, kills_in_seconds, leave_rate, run_rate)

    #print(runners)
    #print(f"{run_rate}%")
    #print(f"Zero def rate is {zero_def_rate}%")
    #print(f"Leave rate is {leave_rate}%")
    #print(f'Raids left: {raids_left}')
    #print(kills_in_seconds)


if __name__ == '__main__':
    main(1000000)  # Number of times to run the simulator
