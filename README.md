# Sopel Bot Prompts

A module that connects to a bot prompt repository, such as [#lowtech botprompts](https://botprompts.lowtech.io)
and enables people to use different personas for ChatGPT and other conversational bots.

## Installation

Tested on Ubuntu 22.04 LTS. Requires python 3.7 and [Sopel 7.1](https://github.com/sopel-irc/sopel),
and [OpenAI](https://platform.openai.com/docs/api-reference?lang=python)

Highly recommended to create a separate [pyenv environment](https://realpython.com/intro-to-pyenv/)
for the Sopel bot and use pip to install the repository. The plugin will be available to Sopel
as an [Entry point plugin](https://sopel.chat/docs/plugin.html#term-Entry-point-plugin)

```bash
pyenv virtualenv sopel_7_1
pip install sopel
cd ./sopel-botprompts
pip install .
pip install -r requirements.txt
```

## Configuration

The plugin has several configuration options with sensible defaults where appropriate

### openai_key

Type: `string`

This is the OpenAI API key to enable the bot to communicate with the [ChatGPT service](https://platform.openai.com/docs/api-reference?lang=python).

### botprompts_api

Type: `string`

This is the API endpoint for your Bot Prompts repository.

### freq_check_new_commands

Type: `float`

The frequency with which to check for new commands from the Bot Prompts repository. Default `15.0` seconds

### model

Type: `string`

This determines which ChatGPT model will be used. The most common one is `text-davinci-003`

### temperature

Type: `float`

The weight or [sampling temperature](https://platform.openai.com/docs/api-reference/completions/create#completions/create-temperature)

### top_p

Type: `float`

A probability of sampling called [nucleus sampling](https://platform.openai.com/docs/api-reference/completions/create#completions/create-top_p). Change either this value or the temperature, but not both.

### frequency_penalty

Type: `float`

Values between `-2.0` and `2.0` where [positive values penalize](https://platform.openai.com/docs/api-reference/completions/create#completions/create-frequency_penalty) repeating new tokens, resulting in more varied text

### max_tokens

Type: `int`

The [maximum number of tokens](https://platform.openai.com/docs/api-reference/completions/create#completions/create-max_tokens) that are requested to be returned. Note that older models are limited
to 2048, while newer models are limited to 4096.

### Alternative Configuration

For those who don't like running interactive `sopel -w` you need to add to the default.cfg file

```ini
[botprompts]
openai_key = YOUR-KEY-HERE
botprompts_api = https://botprompts.lowtech.io
freq_check_new_commands = 15.0
model = text-davinci-003
temperature = 1
top_p = 1
max_tokens = 2048
frequency_penalty = 1
```

## Usage

Use existing prompts at [#lowtech Bot Prompts](https://botprompts.lowtech.io) or create your own.

If you use a prompt called `eeyore` then in your irc channel, you can use a command, such as:

```irc
< you> .eeyore What should I do with this apple?
<+sopel-bot> you: (gpt) I have some things to tell you, brain the size of a planet..
```

### IRC commands

All non-ignored users can use a prompt command

## Testing

Tests are run via Python unittests and are stored in the `tests/` directory.

```bash
python -m unittest
```
