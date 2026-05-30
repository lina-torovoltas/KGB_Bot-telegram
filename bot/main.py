import re
import telebot
import asyncio
import fortune
import json
import random
import logging
import sys

from os import getenv
from antiswear import *
from datetime import datetime, timezone
from difflib import SequenceMatcher
from telebot.async_telebot import AsyncTeleBot

# preparing
open("users.txt", "a").close() 


nullbot = AsyncTeleBot(getenv('TOKEN', ''))

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Saving time at the moment of bot start
start_time = datetime.now(timezone.utc)


# Loads the question-and-answer database
db_file = "db.json"

def load_db():
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_db(db):
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

db = load_db()



# User verification function for administrator rights
async def is_user_admin(chat_id, user_id):
    admin_statuses = ["creator", "administrator"]
    if str(user_id) == "YOUR_ID": # God mode hehe:3
        return 1
    result = await nullbot.get_chat_member(chat_id, user_id)
    if result.status in admin_statuses:
        return 1
    return 0


# Finds the most similar question from the database
def find_best_match(question):
    question = question.lower()
    best_match = None
    best_ratio = 0.5
    
    logging.info(f"Finding an answer to the question: {question}")
    
    for item in db:
        ratio = SequenceMatcher(None, question, item["question"]).ratio()
        logging.info(f"Comparison with: {item['question']} (match {ratio:.2f})")
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = item
        elif ratio == best_ratio and best_match:
            best_match = random.choice([best_match, item])
    
    if best_match:
        logging.info(f"Selected answer: {best_match['answer']} (match {best_ratio:.2f})")
    else:
        logging.info("No suitable answer was found.")
    
    return best_match


# Checks a question-answer pair for duplicates
def is_duplicate(question, answer):
    question = question.lower()
    answer = answer.strip()
    for item in db:
        if SequenceMatcher(None, question, item["question"]).ratio() > 0.9 and SequenceMatcher(None, answer, item["answer"]).ratio() > 0.9:
            return True
    return False



# Command to add a new question-answer pair
@nullbot.message_handler(commands=["teach"])
async def teach(message):
    if "=" not in message.text:
        await nullbot.reply_to(message, "Usage: /teach Question=Answer")
        return
    
    _, data = message.text.split("/teach", 1)
    question, answer = data.strip().split("=", 1)
    question = question.strip().lower()
    answer = answer.strip()
    if not question or not answer:
        await nullbot.reply_to(message, "Question and Answer cannot be empty!")
        return
    
    if not is_duplicate(question, answer):
        db.append({"question": question, "answer": answer})
        save_db(db)
        logging.info(f"A new pair has been added: {question} = {answer}")
        await nullbot.reply_to(message, "Got it!")
    else:
        await nullbot.reply_to(message, "Such a question-answer pair already exists.")


# Command to ask the bot a question
@nullbot.message_handler(commands=["ask"])
async def ask(message):
    if len(message.text.strip().split()) < 2:
        await nullbot.reply_to(message, "Usage: /ask your question")
        return
    _, question = message.text.split("/ask", 1)
    question = question.strip().lower()
    best_match = find_best_match(question)
    
    if best_match:
        await nullbot.reply_to(message, best_match["answer"])
    else:
        await nullbot.reply_to(message, "I don't know the answer to that.")


# Sending a quote
@nullbot.message_handler(commands=['quote'])
async def quote(message):
    fortun = fortune.get_random_fortune('quotes.txt')
    
    await nullbot.reply_to(message,f'`{fortun}`')


# Adding a user to the users monitoring list
@nullbot.message_handler(commands=['add_user'])
async def add_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    result = await is_user_admin(chat_id, user_id)

    # Checking a user for administrator rights
    if result == 0:
        await nullbot.reply_to(message, "You do not have permission to run this command.")
        return
    # Checking a command for an argument
    args = message.text.split()
    if len(args) < 2:
        await nullbot.reply_to(message, "Please enter a user ID. \nExample: /add_user 123123123")
        return

    user_to_add = args[1]
    print(f"Attempting to add user: {user_to_add}") # Debugging to the console

    # Handling errors and adding a user to the list
    try:
        with open('users.txt', 'r') as file:
            existing_users = file.read().splitlines()

        # Sending an error message that the user is already on the list
        if user_to_add in (user.lower() for user in existing_users):
            await nullbot.reply_to(message, f"The user ID '{user_to_add}' already exists in the list.")
            return

        # Adding a user to the list
        with open('users.txt', 'a') as file:
            file.write(f'{user_to_add}\n')

        # Sending a message that the user has been successfully added to the list
        await nullbot.reply_to(message, f"User ID '{user_to_add}' added.")
    # Sending an error message
    except Exception as e:
        await nullbot.reply_to(message, f"An error occurred: {str(e)}")


# Removing a user from the users monitoring list
@nullbot.message_handler(commands=['remove_user'])
async def remove_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    result = await is_user_admin(chat_id, user_id)

    # Checking a user for administrator rights
    if result == 0:
        await nullbot.reply_to(message, "You do not have permission to run this command.")
        return
    # Checking a command for an argument
    args = message.text.split()
    if len(args) < 2:
        await nullbot.reply_to(message, "Please enter user ID. \nExample: /remove_user 123123123")
        return

    user_id_to_remove = args[1]
    print(f"Removing a user: ID = {user_id_to_remove}")  # Debugging to the console

    # Handling errors and removing a user from the list
    try:
        with open('users.txt', 'r') as file:
            users = file.readlines()
            
        # Removing a user from the list
        with open('users.txt', 'w') as file:
            for user in users:
                if user.strip() != user_id_to_remove:
                    file.write(user)

        # Sending a message that the user has been successfully removed from the list
        await nullbot.reply_to(message, f"User ID: {user_id_to_remove} has been removed.")
    # Sending an error message that the file with the list of users was not found
    except FileNotFoundError:
        await nullbot.reply_to(message, "User list not found.")
    # Sending an error message
    except Exception as e:
        await nullbot.reply_to(message, f"An error occurred: {str(e)}")


# Command to find out how long the bot has been running
@nullbot.message_handler(commands=['uptime'])
async def send_uptime(message):
    current_time = datetime.now(timezone.utc)
    uptime_duration = current_time - start_time

    # Getting days hours and minutes from bot running time
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Formatting and sending a message to a user
    uptime_str = f"{days} days, {hours} hours, {minutes} minutes."
    await nullbot.send_message(message.chat.id, f'The bot has been running for: \n{uptime_str}')


# Function for searching and removing swear words from users in the monitoring list
@nullbot.message_handler(func=lambda message: True)
async def checking_messages(message):
    text = message.text
    user_id = str(message.from_user.id)
    text_cleaning = re.split(r'[,.\n? ]+', text)
    user_name = message.from_user.username

    # Handling errors and searching/removing swear words from users from the monitoring list
    try:
        # Reading files with a list of users
        with open("users.txt", "r") as user_content:
            users_check = user_content.read().split()

        logging.info(f"Message checking: ID = {user_id}, Username = @{user_name}")  # Debugging to the console

        # Searching for a user in the list of users to monitoring
        if user_id in users_check:
            # Searching for swear words in user's text
            for word in text_cleaning:
                if check(word):
                    logging.info(f"Message removed, word '{word}', message {text_cleaning}")   # Debugging to the console
                    await nullbot.delete_message(message.chat.id, message.id)
                    return
    # Sending an error message that files were not found
    except FileNotFoundError as e:
        logging.info(f"File not found: {str(e)}")
    # Sending an error message
    except Exception as e:
        logging.info(f"An error occurred while checking messages: {str(e)}")



# Running a bot
if __name__ == '__main__':
    print("0xNULL Bot is turned on!")
    asyncio.run(nullbot.polling())
