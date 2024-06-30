import os
import time
from datetime import datetime
from telethon import TelegramClient, events, sync, Button
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import UserAlreadyParticipantError, ChannelPrivateError, FloodWaitError, RPCError, SecurityError
from colorama import init, Fore, Style
from config import api_id, api_hash, phone_number

init()

client = TelegramClient('session_name', api_id, api_hash)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def log_message(message, color):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'{color}[{current_time}] {message}{RESET}')

async def get_channel_usernames():
    log_message("Fetching usernames of channels...", BLUE)
    dialogs = await client.get_dialogs()
    channels = []
    for dialog in dialogs:
        try:
            entity = await client.get_entity(dialog.entity.id)
            if hasattr(entity, 'username') and entity.username and entity.megagroup:
                channels.append(entity.username)
        except AttributeError:
            continue
        except Exception as e:
            log_message(f"Error while fetching channel {dialog.entity.id}: {e}", RED)
    
    with open('Mychannels.txt', 'w', encoding='utf-8') as file:
        for channel in channels:
            file.write(f"{channel}\n")
    
    log_message("Usernames of channels saved in Mychannels.txt.", BLUE)

async def get_joined_channels():
    log_message("Fetching joined channels...", BLUE)
    joined_channels = set()
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel and dialog.entity.username:
            joined_channels.add('@' + dialog.entity.username)
    
    log_message("Fetching joined channels completed.", BLUE)
    return joined_channels

def compare_channels(joined_channels, all_channels):
    log_message("Comparing channels...", BLUE)
    
    new_channels = all_channels - joined_channels
    
    with open('newChannels.txt', 'w') as file:
        for channel in new_channels:
            file.write(channel + '\n')
    
    log_message("Comparison complete. New channels have been written to 'newChannels.txt'.", BLUE)

async def join_channels():
    log_message("Starting the process of joining channels...", BLUE)
    try:
        with open('newChannels.txt', 'r') as file:
            channels = file.readlines()
    except FileNotFoundError:
        log_message("newChannels.txt does not exist. Please run option 2 to create the file.", RED)
        time.sleep(3)
        return

    for channel in channels:
        channel = channel.strip()
        if channel:
            try:
                await client(JoinChannelRequest(channel))
                log_message(f'Successfully joined {channel}', GREEN)
            except UserAlreadyParticipantError:
                log_message(f'Already a member in {channel}', GREEN)
            except ChannelPrivateError:
                log_message(f'Failed to join {channel}: Channel is private', RED)
            except FloodWaitError as e:
                log_message(f'Rate limited. Waiting for {e.seconds} seconds.', RED)
                time.sleep(e.seconds)
                continue
            except RPCError as e:
                log_message(f'RPCError encountered: {e}', RED)
            except Exception as e:
                log_message(f'Failed to join {channel}: {e}', RED)

            time.sleep(240)
    log_message("All channels have been joined successfully.", BLUE)

async def send_message_periodically(channels, message, pub_interval):
    log_message("Starting periodic message sending...", BLUE)
    while True:
        for channel in channels:
            try:
                if channel.startswith('https://t.me/'):
                    parts = channel.split('/')
                    channel_username = parts[-2]
                    message_id = int(parts[-1])
                    entity = await client.get_entity(channel_username)
                    await client.send_message(entity, message, reply_to=message_id)
                elif channel.startswith('@'):
                    entity = await client.get_entity(channel)
                    await client.send_message(entity, message)
                else:
                    log_message(f"Ignored invalid channel: {channel}", YELLOW)
                    continue
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message(f"Message sent to {channel} at {current_time}", GREEN)
            except SecurityError as e:
                log_message(f"Security error while sending message: {e}", RED)
                continue
            except Exception as e:
                error_message = str(e)
                if "A wait of" in error_message:
                    wait_time = int(error_message.split("A wait of ")[1].split(" seconds")[0])
                    if wait_time > 3600:
                        log_message(f"Your account got rate limited for {wait_time} seconds. Waiting for the end of the limitation to continue advertising...", RED)
                        time.sleep(wait_time)
                    else:
                        log_message(f"Cooldown of {wait_time} seconds for {channel}.", YELLOW)
                elif "You're banned from sending messages" in error_message or "You can't write in this chat" in error_message:
                    log_message(f"Error sending to channel {channel}: {e}", RED)
                else:
                    log_message(f"Unknown error sending to channel {channel}: {e}", RED)
            time.sleep(4)
        log_message(f"{pub_interval} seconds before resending the advertisement", BLUE)
        time.sleep(pub_interval)

def get_channel_list(file_path):
    log_message(f"Fetching channel list from {file_path}...", BLUE)
    with open(file_path, 'r', encoding='utf-8') as file:
        channels = [line.strip() for line in file.readlines()]
    log_message("Fetching channel list completed.", BLUE)
    return channels

def define_ad_message():
    log_message('Enter your ad message. Type "END" at the end and press ENTER:', BLUE)
    ad_message = []
    
    while True:
        line = input()
        if line == "END":
            break
        ad_message.append(line)
    
    ad_message = "\n".join(ad_message)
    log_message("Ad message defined.", BLUE)
    return ad_message

def display_main_menu():
    log_message(f"Welcome Ethan! What would you like to do?", BLUE)
    print("1: Account Management")
    print("2: Channel Management")
    print("3: Advertising")
    print("4: Quit")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def main():
    await client.start(phone_number)
    me = await client.get_me()
    
    ad_message = ""
    pub_interval = 600

    while True:
        clear_screen()
        display_main_menu()
        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == '1':
            clear_screen()
            log_message("Account Management options (Not yet implemented)", BLUE)
            # To do
        elif choice == '2':
            while True:
                clear_screen()
                log_message("Channel Management options:", BLUE)
                print("1: Fetch and save @ usernames of channels")
                print("2: Fetch list of channels not joined from the provided list")
                print("3: Join channels not yet joined")
                print("4: Go back")
                channel_choice = input("Enter your choice (1, 2, 3, or 4): ")

                if channel_choice == '1':
                    await get_channel_usernames()
                elif channel_choice == '2':
                    if not os.path.exists('channels.txt'):
                        log_message("channels.txt does not exist. Please create the file with the list of channels.", RED)
                        time.sleep(3)
                        continue
                    joined_channels = await get_joined_channels()
                    all_channels = set(get_channel_list('channels.txt'))
                    compare_channels(joined_channels, all_channels)
                    log_message("Comparison complete. New channels have been written to 'newChannels.txt'.", BLUE)
                elif channel_choice == '3':
                    await join_channels()
                elif channel_choice == '4':
                    break
                else:
                    log_message("Invalid choice. Please try again.", RED)

        elif choice == '3':
            while True:
                clear_screen()
                log_message("Advertising options:", BLUE)
                print("1: Define the ad message")
                print("2: Define the interval between each ad messages")
                print("3: Send your ad")
                print("4: Go back")
                ad_choice = input("Enter your choice (1, 2, 3, or 4): ")

                if ad_choice == '1':
                    ad_message = define_ad_message()
                elif ad_choice == '2':
                    pub_interval = int(input("Enter the interval between ad messages in seconds: "))
                    log_message(f"Interval between ad messages set to {pub_interval} seconds.", BLUE)
                elif ad_choice == '3':
                    file_name = input("Enter the name of the file containing the list of channels to which you want to send your ad (Mychannels.txt for all your channels, or another text file if you want to select your own channels. Make sure you put your text file in the folder running the code.): ")
                    if not os.path.exists(file_name):
                        log_message(f"{file_name} does not exist. Please make sure the file is in the correct folder.", RED)
                        time.sleep(3)
                        continue
                    if not ad_message.strip():
                        log_message("Ad message is empty. Please define the ad message first.", RED)
                        time.sleep(3)
                        continue
                    channels = get_channel_list(file_name)
                    await send_message_periodically(channels, ad_message, pub_interval)
                elif ad_choice == '4':
                    break
                else:
                    log_message("Invalid choice. Please try again.", RED)

        elif choice == '4':
            log_message("Goodbye!", BLUE)
            break
        else:
            log_message("Invalid choice. Please try again.", RED)

if __name__ == '__main__':
    clear_screen()
    with client:
        client.loop.run_until_complete(main())
