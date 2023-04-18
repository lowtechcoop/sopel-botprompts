from sopel.config.types import StaticSection, ValidatedAttribute


class BotPromptsConfigSection(StaticSection):
    """
    Configuration class for Sopel config file.
    """

    openai_key = ValidatedAttribute("openai_key", parse=str, default="")

    botprompts_api = ValidatedAttribute("botprompts_api", parse=str, default="")

    freq_check_new_commands = ValidatedAttribute("freq_check_new_commands", parse=float, default=15)

    model = ValidatedAttribute("model", parse=str, default="")

    temperature = ValidatedAttribute("temperature", parse=float, default=1)

    top_p = ValidatedAttribute("top_p", parse=float, default=1)

    frequency_penalty = ValidatedAttribute("frequency_penalty", parse=float, default=1)

    max_tokens = ValidatedAttribute("max_tokens", parse=int, default=2048)

