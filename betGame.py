import random
from telegram import Update
from telegram.ext import ApplicationBuilder, Updater, CommandHandler, MessageHandler, filters, CallbackContext
from config import TOKEN

# Lista de jogadores e número secreto
players = []
current_game = {
    "active": False,
    "number": None,
    "turn_index": 0,
}

def join_game(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if user.id not in players:
        players.append(user.id)
        update.message.reply_text(f"{user.first_name} entrou no jogo!")
    else:
        update.message.reply_text("Você já está no jogo!")

def start_game(update: Update, context: CallbackContext) -> None:
    if not players:
        update.message.reply_text("Ninguém entrou no jogo ainda! Use /joinGame para participar.")
        return

    if current_game["active"]:
        update.message.reply_text("O jogo já está em andamento!")
        return

    # Inicia o jogo
    current_game["active"] = True
    current_game["number"] = random.randint(1, 100)
    current_game["turn_index"] = 0
    update.message.reply_text("O jogo começou! O número secreto foi escolhido entre 1 e 100.")
    announce_turn(update, context)

def announce_turn(update: Update, context: CallbackContext) -> None:
    player_id = players[current_game["turn_index"]]
    player_name = context.bot.get_chat(player_id).first_name
    context.bot.send_message(chat_id=player_id, text="É a sua vez! Tente adivinhar o número.")
    context.bot.send_message(chat_id=update.message.chat_id, text=f"É a vez de {player_name}!")

def handle_guess(update: Update, context: CallbackContext) -> None:
    if not current_game["active"]:
        update.message.reply_text("Não há um jogo em andamento. Use /startGuessGame para começar.")
        return

    user = update.message.from_user
    if user.id != players[current_game["turn_index"]]:
        update.message.reply_text("Não é a sua vez!")
        return

    try:
        guess = int(update.message.text)
    except ValueError:
        update.message.reply_text("Por favor, envie um número válido!")
        return

    if guess == current_game["number"]:
        update.message.reply_text(f"Parabéns, {user.first_name}! Você acertou o número {guess}!")
        current_game["active"] = False
        players.clear()  # Limpa a lista de jogadores
    elif guess < current_game["number"]:
        update.message.reply_text("O número é maior! Tente novamente.")
    else:
        update.message.reply_text("O número é menor! Tente novamente.")

    # Passa a vez para o próximo jogador
    if current_game["active"]:
        current_game["turn_index"] = (current_game["turn_index"] + 1) % len(players)
        announce_turn(update, context)

def run():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("joinGame", join_game))
    app.add_handler(CommandHandler("startGuessGame", start_game))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
    app.run_polling()