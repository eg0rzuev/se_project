# DTM SE Project
This is a project created for a DTM Software Engineering course. The Telegram bot enables users to calculate shared expenses between friends.

## Getting Started
To use the bot, simply add it to your Telegram group and activate it with `/start` command. To include you in a bot database use `/add_me` command. New users are added to the bot automatically. Bot supports English, Italian and Russian languages.

## Technologies Used
The bot is built using the python3 library `pyTelegramBotAPI` and is deployed in a **Docker container** hosted on a **Google Cloud virtual machine**. The data is stored in **Google Cloud SQL (PostgreSQL)**.

## Commands
- `/start` – start the bot and receive **Start message**
- `/add_me` - use this command to enable calculations with you, otherwise bot does not know you are in the chat.
- `/set_lang` <i>language</i> – set the bot language, _language_ is an obligatory two letter language code. Languages available are: **en, it, ru**
- `/loan_oneline` _borrower_uname lender_uname amount [comment]_ – use this command to change the balance of borrower by negative _amount_ and lender's balance by positive _amount_. All parameters are obligatory except for _comment_ which can be up to 1000 characters long. 
- `/current_state` – the bot prints the current balance of each user.
- `/show_transactions` – each balance change is considered a transaction. This command prints all the transactions of the current chat.
- `/finalize` – print the amounts to be transferred to other people to make their balances zero
- `/new_loan` – add a new loan in an interactive manner by replying to bot's messages. 

## Creation steps
- Generate the bot Token with BotFather and launch the basic telegram bot
- Write a Dockerfile and launch the same bot locally
- Set up the Google Cloud account with Google SQL, Virtual Machine
- Create a GitHub actions pipeline (builds Docker image and deploys it inside a virtual machine)
- Launch the bot in a Docker container inside the Virtual Machine
- Write the rest of the bot code
- Write the documentation

## Additional Information

For more details on the project structure and files, please refer to the **Details** folder in this repository.

## Possible upgrades

- Monitoring and logging the bot with ELK Stack
- Asynchronous bot
- Running app in Kubernetes with other services (for example, DB cleaner)
- UI for adding new user messages in several languages
- Adding more languages using automated translation
