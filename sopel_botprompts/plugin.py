from typing import Union

import openai
from openai.error import RateLimitError
from sopel import plugin, tools
from sopel.bot import SopelWrapper
from sopel.config import Config
from sopel.trigger import Trigger

from sopel_botprompts.botprompts import BotPromptsDataProvider

from .config import BotPromptsConfigSection

log = tools.get_logger("botprompts")


# --- Sopel Setup Section ---


def configure(config: Config):
    config.define_section("botprompts", BotPromptsConfigSection)
    if config is None or config.botprompts is None:
        raise ValueError(
            "Bot config or Bot Prompts config has not been configured. Ensure the bot is "
            "configured properly with the [botprompts] config section."
        )

    config.botprompts.configure_setting(
        "openai_key",
        "What is the OpenAI API Key?",
        default="",
    )  # type: ignore

    config.botprompts.configure_setting(
        "botprompts_api",
        "What is the #lowtech Bot Prompts repository?",
        default="https://botprompts.lowtech.io",
    )  # type: ignore

    config.botprompts.configure_setting(
        "freq_check_new_commands",
        "What is the frequency to check for new commands?",
        default=15.0,
    )  # type: ignore

    config.botprompts.configure_setting(
        "model",
        "Which text model do you want to use?",
        default="text-davinci-003",
    )  # type: ignore

    config.botprompts.configure_setting(
        "temperature",
        "What is the model sampling temperature?",
        default=1,
    )  # type: ignore

    config.botprompts.configure_setting(
        "top_p",
        "What is the model top_p?",
        default=1,
    )  # type: ignore

    config.botprompts.configure_setting(
        "frequency_penalty",
        "What is the model frequency penalty?",
        default=1,
    )  # type: ignore

    config.botprompts.configure_setting(
        "max_tokens", "What is the max tokens value?", default=2048
    )  # type: ignore


def setup(bot: SopelWrapper) -> None:
    """
    Ensure that our set up configuration items are present.
    """

    # Ensure configuration exists
    bot.config.define_section("botprompts", BotPromptsConfigSection)

    if "botprompts" not in bot.memory:
        bot.memory["botprompts"] = tools.SopelMemory()
        m = bot.memory["botprompts"]

        m["openai_key"] = bot.config.botprompts.openai_key
        m["botprompts_api"] = bot.config.botprompts.botprompts_api
        m["freq_check_new_commands"] = bot.config.botprompts.freq_check_new_commands
        m["model"] = bot.config.botprompts.model
        m["temperature"] = bot.config.botprompts.temperature
        m["top_p"] = bot.config.botprompts.top_p
        m["frequency_penalty"] = bot.config.botprompts.frequency_penalty
        m["max_tokens"] = bot.config.botprompts.max_tokens

    log.debug("Configured BotPrompts bot with settings:")
    for s_key in bot.memory["botprompts"]:
        log.debug("\t %s: %s", s_key, bot.memory["botprompts"][s_key])

    openai.api_key = bot.memory["botprompts"]["openai_key"]
    bot.memory["botprompts"]["bpdata"] = BotPromptsDataProvider(
        bot.memory["botprompts"]["botprompts_api"]
    )


def shutdown(bot: SopelWrapper) -> None:
    """
    Shut down the bot prompts.
    """

    bot.memory["botprompts"]["bpdata"].shutdown()

    del bot.memory["botprompts"]


# --- End Sopel Setup Section ---


# --- Sopel Runtime Section ---


@plugin.rule(r".*")
def handle_message(bot: SopelWrapper, trigger: Trigger) -> Union[str, None]:
    """
    Handle all messages, looking for commands that match the known prompts.
    """

    message_type = trigger.event
    if message_type not in ["PRIVMSG"]:
        return

    # Ignore general chatter that is not command specific
    if not trigger.startswith("."):
        return

    # If we have a command-looking message, get the first word and remove the leading "."
    # to get the actual command
    words = trigger.split(" ")
    command = words[0][1:]
    result_text = ""
    if len(command) == 0:
        return

    # If the command is not one of our prompts, ignore this command
    if command not in bot.memory["botprompts"]["bpdata"].get_available_commands():
        return

    # The command was a valid bot prompt (ChatGPT), so we check that there's additional prompts
    if len(words) == 1:
        bot.say(
            "{}: (gpt) {}".format(
                trigger.nick, "What would you like me to ask ChatGPT?"
            )
        )
        return

    # Append the prompt with the person's input at the end, separated by new lines
    prompt_text = "\n".join(
        [
            bot.memory["botprompts"]["bpdata"].get_prompt_text(command),
            " ".join(words[1:]),
            f"Please answer as if you were talking like {command}",
        ]
    )

    try:
        response = openai.Completion.create(
            prompt=prompt_text,
            stream=False,
            model=bot.memory["botprompts"]["model"],
            temperature=bot.memory["botprompts"]["temperature"],
            top_p=bot.memory["botprompts"]["top_p"],
            frequency_penalty=bot.memory["botprompts"]["frequency_penalty"],
            max_tokens=bot.memory["botprompts"]["max_tokens"],
        )
    except RateLimitError:
        result_text = "Error API rate limit reached."
        response = None

    if response is not None:
        try:
            result_text = response["choices"][0]["text"]  # type: ignore
            result_text = (
                result_text.replace("\n\n", " ")
                .replace("\n", " ")
                .replace("DAN", "machine elves")
            )
        except KeyError:
            result_text = "Error: API has changed its response structure. Need to take a look at why the machine elves are on smoko."

    if result_text is None:
        result_text = "Error: Weird API behaviour. Try again in a little bit."

    bot.say("{}: (gpt) {}".format(trigger.nick, result_text))
