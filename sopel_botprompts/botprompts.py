import json
from threading import Timer
from typing import List

import requests
from sopel import tools

log = tools.get_logger("botprompts")


class BotPromptsDataProvider:
    """
    Stateful data provider for BotPrompts.
    """

    botprompts_api: str

    commands_url: str

    prompt_url_template: str

    commands: List[str]

    timer: Timer

    freq_check_new_commands: float

    def __init__(
        self, botprompts_api: str, freq_check_new_commands: float = 15
    ) -> None:
        log.debug("Initializing bot prompts from %s", botprompts_api)

        self.botprompts_api = f"{botprompts_api}/api/v1"

        self.commands_url = f"{self.botprompts_api}/prompts/commands"

        self.prompt_url_template = "{}/{}/{}".format(
            self.botprompts_api,
            "prompts/detail",
            "{}",
        )

        self.freq_check_new_commands = freq_check_new_commands
        self.__reset_timer()

    def __reset_timer(self):
        """
        Reset the timer that checks for the commands list.
        """

        self.timer = Timer(self.freq_check_new_commands, self.__update_commands_list)
        self.timer.start()

    def __update_commands_list(self):
        """
        Call to update the commands list.
        """

        result = self.__make_get_api_call(self.commands_url)
        if "error" in result:
            # Disable all API commands because something has gone wrong
            self.commands = []
        else:
            self.commands = result["commands"]

        self.__reset_timer()

    def __make_get_api_call(self, url):
        """
        Make an API call with the specified URL.
        """

        try:
            result = requests.get(
                url, headers={"Content-Type": "application/json", "Accept": "*/*"}
            )

            if result.status_code == 200:
                return result.json()

            else:
                log.error("Error in making call: %s", str(result.content))
                return {"error": True, "detail": str(result.content)}

        except json.decoder.JSONDecodeError as e:
            log.error("Error trying to get data: %s", e.msg)
            return {"error": True, "detail": e.msg}

    def get_available_commands(self) -> List[str]:
        """
        Get available commands.
        """

        log.debug("Available bot prompts for ChatGPT: %s", self.commands)
        return self.commands

    def get_prompt_text(self, prompt_name) -> str:
        """
        Get the prompt text for a specific prompt.
        """

        prompt_url = self.prompt_url_template.format(prompt_name)
        log.debug("Making prompt call to %s", prompt_url)

        result = self.__make_get_api_call(prompt_url)
        if result is None:
            return "API Error, something went very wrong."

        elif "error" in result:
            return result["detail"]

        return result["revision"]["prompt_text"]

    def shutdown(self):
        """
        Notifies internal timers to shut down.
        """

        self.timer.cancel()
