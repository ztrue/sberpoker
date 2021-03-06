import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.card import Card

MULT = 1

MIN = 0
MAX = 999999999

POS_SB = 105
POS_BB = 104
POS_BU = 103
POS_CO = 102
POS_MD = 101
POS_EA = 100

class Hero03(BasePokerPlayer):

    random_percent = 0
    small_stack_bb = 10

    bb = 0
    game_info = []
    start_seats = []

    def __init__(self, random_percent=0, small_stack_bb=10):
        self.random_percent = random_percent
        self.small_stack_bb = small_stack_bb

    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        rnd = random.randint(1,101)
        c1 = Card.from_str(hole_card[0])
        c2 = Card.from_str(hole_card[1])

        own_stack, avg_stack = self.count_stacks(round_state)
        blinds = min(own_stack, avg_stack) / self.bb

        if round_state['street'] == 'preflop':
            pair = c1.rank == c2.rank
            suited = c1.suit == c2.suit

            if blinds < 14:
                return self.push_fold(valid_actions, round_state, blinds, c1, c2)

            is_kk_plus = pair and c1.rank > 12

            is_low_k = min(c1.rank, c2.rank) == 13
            is_hi_a = max(c1.rank, c2.rank) == 14
            is_ak = is_low_k and is_hi_a
            is_aks = is_ak and suited

            if is_kk_plus or is_aks:
                # print('MONSTER', c1, c2)
                return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def push_fold(self, valid_actions, round_state, blinds, c1, c2):
        low = min(c1.rank, c2.rank)
        hi = max(c1.rank, c2.rank)
        pair = c1.rank == c2.rank
        suited = c1.suit == c2.suit

        seat = self.get_seat(round_state)
        pos = self.get_position_type(round_state, seat)

        raiser_seat = self.get_raiser_seat(round_state)
        if raiser_seat < 0:
            rpos = -1
        else:
            rpos = self.get_position_type(round_state, raiser_seat)

        pot = self.count_pot(round_state)
        pot_blinds = pot / self.bb

        medium = low >= 10 and hi >= 10
        big = low + hi >= 24
        monster = low + hi >= 26
        big_pair = pair and low >= 10

        push = False
        if rpos < 0:
            # AA-99
            if pair and low >= 9:
                push = True
            # 88-66
            elif pair and low >= 6:
                push = self.is_push(pos, blinds, { POS_EA: 10, POS_MD: MAX })
            # 55-22
            elif pair:
                push = self.is_push(pos, blinds, { POS_EA: 8, POS_MD: 10, POS_CO: MAX })
            # AK, AQ
            elif hi == 14 and low >= 12:
                push = True
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = self.is_push(pos, blinds, { POS_EA: 8, POS_MD: MAX })
            # A9s-A2s
            elif suited and hi == 14:
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 7, POS_CO: 10, POS_BU: 10, POS_SB: MAX })
            # AJo, ATo
            elif hi == 14 and low >= 10:
                push = self.is_push(pos, blinds, { POS_EA: 7, POS_MD: 8, POS_CO: 11, POS_BU: MAX })
            # A9o-A2o
            elif hi == 14:
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 5, POS_CO: 7, POS_BU: 9, POS_SB: MAX })
            # KQs-K9s, QJs-Q9s, JTs, J9s, T9s
            elif suited and low >= 9:
                push = self.is_push(pos, blinds, { POS_EA: 8, POS_MD: 10, POS_CO: MAX })
            # K8s-K4s, Q8s, J8s, T8s, 98s
            elif suited and (low >= 8 or hi == 13 and low >= 4):
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 6, POS_CO: 8, POS_BU: 9, POS_SB: MAX })
            # KQo-KTo, QJo-QTo, JTo
            elif low >= 10:
                push = self.is_push(pos, blinds, { POS_EA: 5, POS_MD: 8, POS_CO: 10, POS_BU: 10, POS_SB: MAX })
            # Q7s, Q6s
            elif suited and hi == 12 and low >= 6:
                push = self.is_push(pos, blinds, { POS_EA: 4, POS_MD: 5, POS_CO: 6, POS_BU: 7, POS_SB: MAX })
            # 97s, 96s, 86s, 76s, 75s, 65s
            elif suited and ((low == 6 or low == 5) and (hi == 9 or hi == 8 or hi == 7) or low == 5 and (hi == 6 or hi == 7)):
                push = self.is_push(pos, blinds, { POS_EA: 4, POS_MD: 5, POS_CO: 6, POS_BU: 7, POS_SB: MAX })
        elif pos < POS_SB:
            # AA-JJ
            if pair and low >= 11:
                push = True
            # TT, 99
            elif pair and low >= 9:
                push = self.is_push(rpos, blinds, { POS_EA: 8, POS_MD: 9, POS_CO: 11 })
            # 88, 77
            elif pair and low >= 7:
                push = self.is_push(rpos, blinds, { POS_MD: 5, POS_CO: 7 })
            # AK
            elif low == 13 and hi == 14:
                push = True
            # AQ
            elif low == 12 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_EA: 8, POS_MD: 9, POS_CO: 11 })
            # AJs, ATs
            elif suited and low >= 10 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: 6, POS_CO: 9 })
            # AJo
            elif low == 11 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: 5, POS_CO: 7 })
            # ATo, A9s
            elif low == 10 and hi == 14 or suited and low == 9 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_CO: 6 })
        elif pos == POS_SB:
            # AA-JJ
            if pair and low >= 11:
                push = True
            # TT, 99
            elif pair and low >= 9:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # 88, 77
            elif pair and low >= 8:
                push = self.is_push(rpos, blinds, { POS_MD: 7, POS_CO: MAX })
            # 66, 55
            elif pair and low >= 5:
                push = self.is_push(rpos, blinds, { POS_CO: 5, POS_BU: 8 })
            # AK
            elif hi == 14 and low == 13:
                push = True
            # AQ
            elif hi == 14 and low == 12:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = self.is_push(rpos, blinds, { POS_MD: 7, POS_CO: MAX })
            # AJo
            elif hi == 14 and low == 11:
                push = self.is_push(rpos, blinds, { POS_MD: 6, POS_CO: MAX })
            # ATo, A9s
            elif hi == 14 and (suited and low == 9 or low == 10):
                push = self.is_push(rpos, blinds, { POS_MD: 4, POS_CO: 8, POS_BU: 10 })
            # A8s-A4s, A9o-A7o
            elif hi == 14 and (suited and low >= 4 or low >= 7):
                push = self.is_push(rpos, blinds, { POS_CO: 4, POS_BU: 6 })
            # KQs, KJs, KQo
            elif hi == 13 and (suited and low >= 11 or low >= 12):
                push = self.is_push(rpos, blinds, { POS_CO: 4, POS_BU: 6 })
        elif pos == POS_BB:
            # AA-JJ
            if pair and low >= 11:
                push = True
            # TT, 99
            elif pair and low >= 9:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # 88, 77
            elif pair and low >= 7:
                push = self.is_push(rpos, blinds, { POS_MD: 8, POS_CO: MAX })
            # 66, 55
            elif pair and low >= 5:
                push = self.is_push(rpos, blinds, { POS_MD: 5, POS_CO: 8, POS_BU: 10, POS_SB: MAX })
            # 44, 33
            elif pair and low >= 3:
                push = self.is_push(rpos, blinds, { POS_MD: 4, POS_CO: 5, POS_BU: 6, POS_SB: 7 })
            # AK
            elif low == 13 and hi == 14:
                push = True
            # AQ
            elif low == 13 and hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: MAX })
            # AJs, ATs
            elif suited and hi == 14 and low >= 10:
                push = self.is_push(rpos, blinds, { POS_MD: 8, POS_CO: MAX })
            # AJo
            elif hi == 14 and low == 11:
                push = self.is_push(rpos, blinds, { POS_MD: 7, POS_CO: MAX })
            # ATo, A9s
            elif hi == 14 and low == 10 or suited and hi == 14 and low == 9:
                push = self.is_push(rpos, blinds, { POS_MD: 6, POS_CO: 10, POS_BU: MAX })
            # A8s-A4s, A9o-A7o
            elif hi == 14 and (suited and low >= 4 or low >= 7):
                push = self.is_push(rpos, blinds, { POS_MD: 3, POS_CO: 6, POS_BU: 8, POS_SB: MAX })
            # A3s, A2s, A6o-A2o
            elif hi == 14:
                push = self.is_push(rpos, blinds, { POS_MD: 2, POS_CO: 5, POS_BU: 6, POS_SB: 8 })
            # KQs, KJs, KQo
            elif hi == 13 and (suited and low >= 11 or low == 12):
                push = self.is_push(rpos, blinds, { POS_MD: 4, POS_CO: 5, POS_BU: 8, POS_SB: MAX })
            # KTs, K9s, QJs, KJo, KTo
            elif hi == 13 and (suited and low >= 9 or low >= 10) or hi == 12 and low == 11:
                push = self.is_push(rpos, blinds, { POS_MD: 3, POS_CO: 4, POS_BU: 6, POS_SB: 10 })

        if push:
            # if rpos >= 0:
            #     print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', blinds, pos, rpos, c1.rank, c2.rank, suited)
            return self.raise_or_call(valid_actions, MAX)
        return self.check_or_fold(valid_actions)

    def is_push(self, pos, blinds, m):
        for key in m:
            if pos >= key and blinds <= m[key]:
                return True
        return False

    def get_position_type(self, round_state, seat):
        pos_end = self.get_position_end(round_state, seat)

        if seat == round_state['small_blind_pos']:
            return POS_SB
        if seat == round_state['big_blind_pos']:
            return POS_BB
        if seat == round_state['dealer_btn']:
            if pos_end != 0:
                print(seat, pos_end)
                print(json.dumps(round_state, indent=2, sort_keys=True))
                raise RuntimeError('pos_end != 0')
            return POS_BU
        if pos_end == 0:
            print(seat, pos_end)
            print(json.dumps(round_state, indent=2, sort_keys=True))
            raise RuntimeError('pos_end == 0')
        if pos_end == 1:
            return POS_CO
        if pos_end < 5:
            return POS_MD
        return POS_EA

    def get_position_end(self, round_state, seat):
        count = 0
        i = 0
        while i < len(self.start_seats):
            s = self.start_seats[i]
            if s['stack'] > 0:
                count += 1
            i += 1
        return count - 1 - self.get_position(round_state, seat)

    def get_position(self, round_state, seat):
        position = 0
        found = False
        i = round_state['small_blind_pos']
        while i < len(self.start_seats):
            if i == seat:
                found = True
                break
            s = self.start_seats[i]
            if s['stack'] > 0:
                position += 1
            i += 1
        if not found:
            i = 0
            while i < round_state['small_blind_pos']:
                if i == seat:
                    found = True
                    break
                s = self.start_seats[i]
                if s['stack'] > 0:
                    position += 1
                i += 1
        if not found:
            raise RuntimeError('Position not found')
        return position

    def get_seat(self, round_state):
        i = 0
        while i < len(self.start_seats):
            seat = self.start_seats[i]
            if seat['uuid'] == self.uuid:
                return i
            i += 1
        raise RuntimeError('Seat not found')

    def get_raiser_seat(self, round_state):
        uuid = self.get_raiser_uuid(round_state)
        if uuid == '':
            return -1
        i = 0
        while i < len(self.start_seats):
            if self.start_seats[i]['uuid'] == uuid:
                return i
            i += 1
        raise RuntimeError('Raiser seat not found')

    def get_raiser_uuid(self, round_state):
        i = 0
        while i < len(round_state['action_histories']['preflop']):
            action = round_state['action_histories']['preflop'][i]
            if action['action'] == 'RAISE':
                return action['uuid']
            i += 1
        return ''

    def raise_or_call(self, valid_actions, val):
        if valid_actions[2]['amount']['max'] < 0:
            return 'call', valid_actions[1]['amount']
        elif valid_actions[2]['amount']['max'] < val:
            return 'raise', valid_actions[2]['amount']['max']
        elif val < valid_actions[2]['amount']['min']:
            return 'raise', valid_actions[2]['amount']['min']
        return 'raise', val

    def check_or_fold(self, valid_actions):
        if valid_actions[1]['amount'] > 0:
            return 'fold', 0
        return 'call', 0

    def count_stacks(self, round_state):
        own_stack = 0
        other_sum = 0
        other_num = 0

        i = 0
        while i < len(self.start_seats):
            seat = self.start_seats[i]
            if seat['uuid'] == self.uuid:
                own_stack = seat['stack']
            else:
                other_sum += seat['stack']
                other_num += 1
            i += 1

        if other_num > 0:
            avg_stack = other_sum / other_num
        else:
            avg_stack = 0

        return own_stack, avg_stack

    def count_pot(self, round_state):
        total = round_state['pot']['main']['amount']
        i = 0
        while i < len(round_state['pot']['side']):
            total += round_state['pot']['side'][i]['amount']
            i += 1
        return total

    def receive_game_start_message(self, game_info):
        self.game_info = game_info
        self.bb = self.game_info['rule']['small_blind_amount'] * 2

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.start_seats = seats

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
