import random

class Game21: #handles all the game logic
    def __init__(self):
        # keep tracks of the statistics
        self.player_wins = 0
        self.dealer_wins = 0
        self.pushes = 0

        self.new_round()

    def new_round(self):

        #creates new deck and shuffles it
        self.deck = self.create_deck()
        random.shuffle(self.deck)

        self.deck_position = 0
        self.player_hand = []
        self.dealer_hand = []


        self.dealer_hidden_revealed = False

    def deal_initial_cards(self):
        self.player_hand = [self.draw_card(), self.draw_card()]
        self.dealer_hand = [self.draw_card(), self.draw_card()]

    def create_deck(self):
        ranks = ["A"] + [str(n) for n in range(2, 11)] + ["J", "Q", "K"]
        suits = ["hearts", "diamonds", "clubs", "spades"]
        return [f"{rank}_{suit}" for rank in ranks for suit in suits]

    def draw_card(self):
        card = self.deck[self.deck_position]
        self.deck_position += 1
        return card

    def card_value(self, card):
        card = card.strip()
        rank = card.split("_")[0].upper()

        if rank in ["J", "Q", "K"]:
            return 10
        if rank == "A":
            return 11
        try:
            return int(rank)
        except ValueError:
            return 0

    def hand_total(self, hand):
        total = 0
        ace_count = 0

        for card in hand:
            value = self.card_value(card)
            total += value
            if card.strip().split("_")[0].upper() == "A":
                ace_count += 1

        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        return total


    def player_hit(self):

        card = self.draw_card()
        self.player_hand.append(card)
        return card

    def player_total(self):
        return self.hand_total(self.player_hand)


    def reveal_dealer_card(self):

        self.dealer_hidden_revealed = True

    def dealer_total(self):
        return self.hand_total(self.dealer_hand)

    def play_dealer_turn(self):

        while self.dealer_total() < 17:
            self.dealer_hand.append(self.draw_card())


    def decide_winner(self):
        player_total = self.player_total()
        dealer_total = self.dealer_total()

        if player_total > 21:
            self.dealer_wins += 1
            return "Player went over 21. Dealer wins!"

        if dealer_total > 21:
            self.player_wins += 1
            return "Dealer went over 21. Player wins!"

        if player_total > dealer_total:
            self.player_wins += 1
            return "Player wins!"

        if dealer_total > player_total:
            self.dealer_wins += 1
            return "Dealer wins!"

        self.pushes += 1
        return "Draw"
