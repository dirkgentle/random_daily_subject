import os

import useful_scripts


if __name__ == "__main__":
    os.system("git checkout master")
    if not os.system("git pull"):
        useful_scripts.update_bot_db()
