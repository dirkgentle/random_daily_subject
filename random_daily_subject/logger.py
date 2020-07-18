from datetime import datetime

from config import BasicConfig


def output_log(text: str, debug_mode: bool = False) -> None:
    """
    Used to see the bot output.
    """
    date_text = datetime.today().strftime("%Y_%m")
    output_log_path = f"{BasicConfig.logs_folder}/{date_text}_output_log.txt"
    with open(output_log_path, "a") as myLog:
        date_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s = f"[{date_text}] {text}\n"
        myLog.write(s)
    if debug_mode:
        print(text)
