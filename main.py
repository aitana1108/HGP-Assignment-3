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
        self.setGeometry(200, 200, 400, 400)

        self.game = Game21()
        self.dark_mode = False
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout()
        central_widget.setLayout(root_layout)

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

        table_widget = QWidget()
        table_widget.setStyleSheet("background-color: #0b6b1a;")
        table_layout = QVBoxLayout()
        table_widget.setLayout(table_layout)

        title = QLabel("Blackjack")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e40ff;")
        table_layout.addWidget(title)

        dealer_label = QLabel("Dealer")
        dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dealer_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        dealer_label.setStyleSheet("color: gold;")

        self.dealerTotalLabel = QLabel("")
        self.dealerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dealerTotalLabel.setStyleSheet("color: white;")

        self.dealerCardsLayout = QHBoxLayout()

        table_layout.addWidget(dealer_label)
        table_layout.addWidget(self.dealerTotalLabel)
        table_layout.addLayout(self.dealerCardsLayout)

        self.feedbackLabel = QLabel("")
        self.feedbackLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedbackLabel.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.feedbackLabel.setStyleSheet("color: yellow;")
        table_layout.addWidget(self.feedbackLabel)

        player_label = QLabel("Player")
        player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        player_label.setStyleSheet("color: gold;")

        self.playerTotalLabel = QLabel("Total: 0")
        self.playerTotalLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playerTotalLabel.setStyleSheet("color: white;")

        self.playerCardsLayout = QHBoxLayout()

        table_layout.addWidget(player_label)
        table_layout.addWidget(self.playerTotalLabel)
        table_layout.addLayout(self.playerCardsLayout)

        root_layout.addWidget(table_widget, 4)

        right_layout = QVBoxLayout()

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

        right_layout.addWidget(score_title)
        right_layout.addWidget(self.statsLabel)
        right_layout.addStretch()

        root_layout.addLayout(right_layout, 1)

        self.new_round_setup()


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
            if len(self.game.dealer_hand) >= 2:
                self.add_card(self.dealerCardsLayout, "??")  # hidden card
                self.add_card(self.dealerCardsLayout, self.game.dealer_hand[1])  # visible card
            elif len(self.game.dealer_hand) == 1:
                self.add_card(self.dealerCardsLayout, "??")

            self.dealerTotalLabel.setText("Total: ?")

    def new_round_setup(self):
        self.clear_layout(self.playerCardsLayout)
        self.clear_layout(self.dealerCardsLayout)

        self.feedbackLabel.setText("")

        self.game.deal_initial_cards()

        for card in self.game.player_hand:
            self.add_card(self.playerCardsLayout, card)

        self.playerTotalLabel.setText(
            f"Total: {self.game.player_total()}"
        )

        self.update_dealer_cards(full=False)

        self.hitButton.setEnabled(True)
        self.standButton.setEnabled(True)

        player_total = self.game.player_total()
        dealer_total = self.game.dealer_total()

        if player_total == 21 and dealer_total == 21:
            self.update_dealer_cards(full=True)
            self.feedbackLabel.setText("Draw! Both have Blackjack (21).")
            self.game.pushes += 1
            self.end_round()
            return

        if player_total == 21:
            self.update_dealer_cards(full=True)
            self.feedbackLabel.setText("Blackjack! Player wins (21)")
            self.game.player_wins += 1
            self.end_round()
            return

        if dealer_total == 21:
            self.update_dealer_cards(full=True)
            self.feedbackLabel.setText("Dealer Blackjack! Dealer wins (21)")
            self.game.dealer_wins += 1
            self.end_round()
            return

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
            QPushButton {
                background-color: #ddd;
                border: 1px solid #aaa;
                padding: 6px;
            }
            QPushButton:hover { background-color: #ccc; }
        """)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #666;
                padding: 6px;
            }
            QPushButton:hover { background-color: #444; }
        """)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
