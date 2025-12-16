from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import sys

from game_logic import Game21

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game of 21")
        self.setGeometry(200, 200, 900, 500)

        self.game = Game21()
        self.dark_mode = False
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout()
        central_widget.setLayout(root_layout)

        # ---------------- LEFT BUTTONS ----------------
        left_layout = QVBoxLayout()

        self.hitButton = QPushButton("Hit")
        self.standButton = QPushButton("Stand")
        self.newRoundButton = QPushButton("New Round")
        self.themeButton = QPushButton("Toggle Theme")

        for btn in (self.hitButton, self.standButton, self.newRoundButton):
            btn.setMinimumHeight(40)
            left_layout.addWidget(btn)

        left_layout.addStretch()
        left_layout.addWidget(self.themeButton)

        self.hitButton.clicked.connect(self.on_hit)
        self.standButton.clicked.connect(self.on_stand)
        self.newRoundButton.clicked.connect(self.on_new_round)
        self.themeButton.clicked.connect(self.toggle_theme)

        root_layout.addLayout(left_layout, 1)

        # ---------------- GREEN TABLE ----------------
        table_widget = QWidget()
        table_widget.setStyleSheet("background-color: #0b6b1a;")
        root_layout.addWidget(table_widget, 5)

        table_outer_layout = QHBoxLayout()
        table_widget.setLayout(table_outer_layout)

        # -------- GAME AREA (LEFT SIDE OF TABLE) --------
        game_layout = QVBoxLayout()
        table_outer_layout.addLayout(game_layout, 4)

        title = QLabel("Blackjack")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e40ff;")
        game_layout.addWidget(title)

        dealer_label = QLabel("Dealer")
        dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dealer_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        dealer_label.setStyleSheet("color: gold;")

        self.dealerTotalLabel = QLabel("")
        self.dealerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dealerTotalLabel.setStyleSheet("color: white;")

        self.dealerCardsLayout = QHBoxLayout()

        game_layout.addWidget(dealer_label)
        game_layout.addWidget(self.dealerTotalLabel)
        game_layout.addLayout(self.dealerCardsLayout)

        self.feedbackLabel = QLabel("")
        self.feedbackLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedbackLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.feedbackLabel.setStyleSheet("color: yellow;")
        game_layout.addWidget(self.feedbackLabel)

        player_label = QLabel("Player")
        player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        player_label.setStyleSheet("color: gold;")

        self.playerTotalLabel = QLabel("Total: 0")
        self.playerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playerTotalLabel.setStyleSheet("color: white;")

        self.playerCardsLayout = QHBoxLayout()

        game_layout.addWidget(player_label)
        game_layout.addWidget(self.playerTotalLabel)
        game_layout.addLayout(self.playerCardsLayout)

        game_layout.addStretch()

        # -------- SCORE AREA (RIGHT SIDE OF TABLE) --------
        score_layout = QVBoxLayout()
        table_outer_layout.addLayout(score_layout, 1)

        score_title = QLabel("Score")
        score_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        score_title.setStyleSheet("color: gold;")

        self.statsLabel = QLabel("Wins: 0\nLosses: 0\nPushes: 0")
        self.statsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statsLabel.setFont(QFont("Arial", 12))
        self.statsLabel.setStyleSheet("""
            QLabel {
                border: 2px solid gold;
                padding: 10px;
                background-color: #0b6b1a;
                color: white;
            }
        """)

        score_layout.addWidget(score_title)
        score_layout.addWidget(self.statsLabel)
        score_layout.addStretch()

        self.new_round_setup()

    # ---------------- GAME LOGIC (UNCHANGED) ----------------

    def on_hit(self):
        card = self.game.player_hit()
        self.add_card(self.playerCardsLayout, card)

        total = self.game.player_total()
        self.playerTotalLabel.setText(f"Total: {total}")

        if total == 21:
            self.update_dealer_cards(full=True)
            self.feedbackLabel.setText("Blackjack! Player wins (21).")
            self.game.player_wins += 1
            self.end_round()
            return

        if total > 21:
            self.update_dealer_cards(full=True)
            self.feedbackLabel.setText("Bust! Dealer wins.")
            self.game.dealer_wins += 1
            self.end_round()

    def on_stand(self):
        self.game.reveal_dealer_card()
        self.game.play_dealer_turn()

        self.update_dealer_cards(full=True)
        self.dealerTotalLabel.setText(f"Total: {self.game.dealer_total()}")

        result = self.game.decide_winner()
        self.feedbackLabel.setText(result)

        self.end_round()

    def on_new_round(self):
        self.game.new_round()
        self.new_round_setup()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def card_to_image_path(self, card_text):
        rank_map = {"A": "ace", "J": "jack", "Q": "queen", "K": "king"}
        rank, suit = card_text.split("_")
        rank_name = rank_map.get(rank, rank)
        return f"assets/cards/{rank_name}_of_{suit}.png"

    def add_card(self, layout, card_text):
        label = QLabel()

        if card_text == "??":
            pixmap = QPixmap("assets/cards/back-card.png")
        else:
            pixmap = QPixmap(self.card_to_image_path(card_text))

        pixmap = pixmap.scaled(
            80, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        label.setPixmap(pixmap)
        layout.addWidget(label)

    def update_dealer_cards(self, full=False):
        self.clear_layout(self.dealerCardsLayout)

        if full:
            for card in self.game.dealer_hand:
                self.add_card(self.dealerCardsLayout, card)
            self.dealerTotalLabel.setText(f"Total: {self.game.dealer_total()}")
        else:
            self.add_card(self.dealerCardsLayout, "??")
            self.add_card(self.dealerCardsLayout, self.game.dealer_hand[1])
            self.dealerTotalLabel.setText("Total: ?")

    def new_round_setup(self):
        self.clear_layout(self.playerCardsLayout)
        self.clear_layout(self.dealerCardsLayout)

        self.feedbackLabel.setText("")

        self.game.deal_initial_cards()

        for card in self.game.player_hand:
            self.add_card(self.playerCardsLayout, card)

        self.playerTotalLabel.setText(f"Total: {self.game.player_total()}")
        self.update_dealer_cards(full=False)

        self.hitButton.setEnabled(True)
        self.standButton.setEnabled(True)

    def end_round(self):
        self.hitButton.setEnabled(False)
        self.standButton.setEnabled(False)

        self.statsLabel.setText(
            f"Wins: {self.game.player_wins}\n"
            f"Losses: {self.game.dealer_wins}\n"
            f"Pushes: {self.game.pushes}"
        )

    def apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QPushButton { background-color: #ddd; }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QPushButton { background-color: #333; color: white; }
        """)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_dark_theme() if self.dark_mode else self.apply_light_theme()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
