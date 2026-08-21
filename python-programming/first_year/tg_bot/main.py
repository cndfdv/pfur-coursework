import asyncio
import logging
import sys
import random
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message

TOKEN = os.environ.get("BOT_API")
dp = Dispatcher()
user_data = {}
hidden_number = None

# Главная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Угадай число")],
        [KeyboardButton(text="Блэкджек")]
    ],
    resize_keyboard=True
)

# Клавиатура числовая
number_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
        [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")],
        [KeyboardButton(text="7"), KeyboardButton(text="8"), KeyboardButton(text="9")],
        [KeyboardButton(text="0")],
        [KeyboardButton(text="Удалить последнюю цифру"), KeyboardButton(text="Отправить")]
    ],
    resize_keyboard=True
)

blackjack_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Взять карту"), KeyboardButton(text="Остановиться")]
    ],
    resize_keyboard=True
)

bet_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="100"), KeyboardButton(text="500"), KeyboardButton(text="1000")],
        [KeyboardButton(text="Очистить ставку"), KeyboardButton(text="Подтвердить ставку")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        "balance": 1000,
        "input": "",
        "bet": 0,
        "player_cards": [],
        "dealer_cards": [],
        "game_in_progress": False
    }
    await message.answer("Добро пожаловать! Выберите игру:", reply_markup=main_keyboard)


#УГАДАЙ ЧИСЛО 
@dp.message(lambda m: m.text == "Угадай число")
async def start_number_game(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["game_in_progress"]='guesser'
    global hidden_number
    hidden_number = random.randint(1, 100)
    user_data[message.from_user.id]["input"] = ""
    await message.answer("Я загадал число от 1 до 100. Попробуй угадать!", reply_markup=number_keyboard)

@dp.message(lambda m: m.text in [str(i) for i in range(10)] and user_data[m.from_user.id]["game_in_progress"]=='guesser')
async def handle_digit(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["input"] += message.text
    await message.answer(f"Текущее число: {user_data[user_id]['input']}")

@dp.message(lambda m: m.text == "Удалить последнюю цифру" and user_data[m.from_user.id]["game_in_progress"]=='guesser')
async def handle_delete(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["input"] = user_data[user_id]["input"][:-1]
    await message.answer(f"Текущее число: {user_data[user_id]['input']}")

@dp.message(lambda m: m.text == "Отправить" and user_data[m.from_user.id]["game_in_progress"]=='guesser')
async def handle_guess(message: Message):
    user_id = message.from_user.id
    text = user_data[user_id]["input"]
    if not text.isdigit():
        await message.answer("Введите число!")
        return

    guess = int(text)
    if guess == hidden_number:
        await message.answer("Ты угадал!", reply_markup=main_keyboard)
    elif guess < hidden_number:
        await message.answer("Больше!")
    else:
        await message.answer("Меньше!")

    user_data[user_id]["input"] = ""


#БЛЭКДЖЕК
def draw_card():
    card = random.choice(["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"])
    return card

def card_value(card):
    if card in ["J", "Q", "K"]:
        return 10
    elif card == "A":
        return 11
    return int(card)

def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = hand.count("A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

@dp.message(lambda m: m.text == "Блэкджек")
async def start_blackjack(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["game_in_progress"]='blackjack'
    balance = user_data[user_id]["balance"]
    user_data[user_id]["input"] = ""
    await message.answer(f"У тебя {balance}₽. Выбери ставку:", reply_markup=bet_keyboard)

@dp.message(lambda m: m.text in ["100", "500", "1000"] and user_data[m.from_user.id]["game_in_progress"]=='blackjack')
async def handle_bet_input(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["input"] += message.text
    await message.answer(f"Текущая ставка: {user_data[user_id]['input']}₽")

@dp.message(lambda m: m.text == "Очистить ставку" and user_data[m.from_user.id]["game_in_progress"]=='blackjack')
async def clear_bet(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["input"] = ""
    await message.answer("Ставка сброшена.")

@dp.message(lambda m: m.text == "Подтвердить ставку" and user_data[m.from_user.id]["game_in_progress"]=='blackjack')
async def confirm_bet(message: Message):
    user_id = message.from_user.id
    text = user_data[user_id]["input"]

    if not text.isdigit():
        await message.answer("Ставка должна быть числом.")
        return

    bet = int(text)
    balance = user_data[user_id]["balance"]

    if bet <= 0 or bet > balance:
        await message.answer("Некорректная ставка.")
        return

    user_data[user_id]["bet"] = bet
    user_data[user_id]["balance"] -= bet
    user_data[user_id]["player_cards"] = [draw_card(), draw_card()]
    user_data[user_id]["dealer_cards"] = [draw_card()]
    user_data[user_id]["game_in_progress"] = 'blackjack'
    user_data[user_id]["input"] = ""

    await message.answer(
        f"Твои карты: {', '.join(user_data[user_id]['player_cards'])} (сумма: {hand_value(user_data[user_id]['player_cards'])})\n"
        f"Карта дилера: {user_data[user_id]['dealer_cards'][0]}\n\n"
        f"Выбери действие:",
        reply_markup=blackjack_keyboard
    )


@dp.message(lambda m: m.text == "Взять карту" and user_data[m.from_user.id]["game_in_progress"]=='blackjack')
async def hit_card(message: Message):
    user_id = message.from_user.id
    if not user_data[user_id]["game_in_progress"]:
        return

    user_data[user_id]["player_cards"].append(draw_card())
    total = hand_value(user_data[user_id]["player_cards"])

    if total > 21:
        user_data[user_id]["game_in_progress"] = False
        await message.answer(
            f"Ты перебрал! Твои карты: {', '.join(user_data[user_id]['player_cards'])} (сумма: {total})\n"
            f"Ты проиграл {user_data[user_id]['bet']}₽.",
            reply_markup=main_keyboard
        )
    else:
        await message.answer(
            f"Твои карты: {', '.join(user_data[user_id]['player_cards'])} (сумма: {total})\n"
            f"Карта дилера: {user_data[user_id]['dealer_cards'][0]}\n\n"
            f"Выбери действие:",
            reply_markup=blackjack_keyboard
        )

@dp.message(lambda m: m.text == "Остановиться" and user_data[m.from_user.id]["game_in_progress"]=='blackjack')
async def stand(message: Message):
    user_id = message.from_user.id
    if not user_data[user_id]["game_in_progress"]:
        return

    # Дилер добирает карты
    dealer = user_data[user_id]["dealer_cards"]
    while hand_value(dealer) < 17:
        dealer.append(draw_card())

    player_total = hand_value(user_data[user_id]["player_cards"])
    dealer_total = hand_value(dealer)
    bet = user_data[user_id]["bet"]
    result = ""

    if dealer_total > 21 or player_total > dealer_total:
        winnings = bet * 2
        user_data[user_id]["balance"] += winnings
        result = f"Ты победил! +{winnings}₽"
    elif player_total == dealer_total:
        user_data[user_id]["balance"] += bet
        result = "Ничья. Ставка возвращена."
    else:
        result = f"Ты проиграл {bet}₽."

    user_data[user_id]["game_in_progress"] = False
    await message.answer(
        f"Твои карты: {', '.join(user_data[user_id]['player_cards'])} (сумма: {player_total})\n"
        f"Карты дилера: {', '.join(dealer)} (сумма: {dealer_total})\n\n"
        f"{result}\nТвой баланс: {user_data[user_id]['balance']}₽",
        reply_markup=main_keyboard
    )


@dp.message()
async def handle_unknown_message(message: Message):
    await message.answer("Я не понял команду. Пожалуйста, выбери один из вариантов на клавиатуре.")

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
