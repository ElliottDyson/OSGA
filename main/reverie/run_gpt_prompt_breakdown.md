# A Breakdown For Methods of Prompting

Prompt functions (the main functions that are called to interact with LLM)

Prompt (create) input functions (functions to generate/gather information to send to LLM)

Prompt validate functions (validate answers that are recieved from LLM)

Clean-up functions (data extraction and manipulation to clean-up the LLM output for processing purposes)

## get_random_alphanumeric()

    Purpose:

    Generates a random alphanumeric string with a length between i and j.

Input:

i: Minimum length of the string.

    j: Maximum length of the string.

    Output:

A random number for wake up time between 'i' and 'j'

## run_gpt_prompt_wake_up_hour()

    Purpose:

    Given a persona object, this function returns an integer that indicates the hour when the persona wakes up.

Input:

persona: An instance of the Persona class.

    test_input: Optional test input.

    verbose: A boolean flag for verbose output.

    Output:

Get the LLM to return a number for their wake-up time. [containing the integer]

## create_prompt_input()

    Purpose:

    Nested function within run_gpt_prompt_wake_up_hour. It creates the input for the GPT prompt based on the persona.

Input:

persona: An instance of the Persona class.

    test_input: Optional test input.

    Output:

An array containing the various relevant persona related information to be sent as a prompt.

## __func_clean_up()

    Purpose:

    Another nested function within run_gpt_prompt_wake_up_hour. It processes the GPT response to extract the wake-up hour.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

An extracted integer representing the wake-up hour.

## __func_validate()

    Purpose:

    Nested function within run_gpt_prompt_wake_up_hour. Validates the GPT response.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

Boolean value indicating if the response is valid. [yes/no]

## run_gpt_prompt_wake_up_hour()

    Operations:

Defines GPT parameters.

    Creates the GPT prompt.

    Calls safe_generate_response to get the GPT response.

    Outputs the result.

    Chunk 8: run_gpt_prompt_daily_plan()

    Purpose:

    Generates a list of daily actions for the persona.

## run_gpt_prompt_daily_plan()

    Purpose:

    Generates a list of daily actions for the persona.

Input:

persona: An instance of the Persona class.

    wake_up_hour: The hour when the persona wakes up.

    test_input: Optional test input.

    verbose: A boolean flag for verbose output.

    Output:

A list of daily actions.

create_prompt_input() (for run_gpt_prompt_daily_plan)

    Purpose:

    Nested function within run_gpt_prompt_daily_plan. Creates the input for the GPT prompt based on the persona and wake_up_hour.

Input:

persona: An instance of the Persona class.

    wake_up_hour: The hour when the persona wakes up.

    test_input: Optional test input.

    Output:

An array containing various persona-based strings and wake-up hour.

    Chunk 10: __func_clean_up() (for run_gpt_prompt_daily_plan)

    Purpose:

    Nested function within run_gpt_prompt_daily_plan. Processes the GPT response to extract daily plans.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

A list containing the daily plans.

__func_clean_up() (for run_gpt_prompt_daily_plan)

    Purpose:

    Nested function within run_gpt_prompt_daily_plan. Processes the GPT response to extract daily plans.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

A processed list containing the daily plans.

__func_validate() (for run_gpt_prompt_daily_plan)

    Purpose:

    Nested function within run_gpt_prompt_daily_plan. Validates the GPT response.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

Boolean value indicating if the response is valid.

## run_gpt_prompt_generate_hourly_schedule()

    Purpose:

    Generates an hourly schedule for the persona.

Input:

    Various parameters including persona, current hour, prior schedule, etc.

Output:

    An schedule specific to the current hour, based on information of what came before in the schedule.

create_prompt_input() (for run_gpt_prompt_generate_hourly_schedule)

    Purpose:

    Nested function within run_gpt_prompt_generate_hourly_schedule. Creates the input for the GPT prompt based on multiple parameters.

Input:

    Several parameters including persona, current hour, prior schedule, etc.

Output:

    An array containing various strings for the prompt.

__func_clean_up() (for run_gpt_prompt_generate_hourly_schedule)

    Purpose:

    Nested function within run_gpt_prompt_generate_hourly_schedule. Cleans up the GPT response.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

A cleaned-up version of the GPT response.

__func_validate() (for run_gpt_prompt_generate_hourly_schedule)

    Purpose:

    Nested function within run_gpt_prompt_generate_hourly_schedule. Validates the GPT response.

Input:

gpt_response: The response from the GPT model.

    prompt: The prompt string (unused).

    Output:

Boolean value indicating if the response is valid.

    Chunk 17: Partial Continuation of run_gpt_prompt_generate_hourly_schedule()

    Operations:

Defines a fail-safe value.

    A commented-out section hints at a possible extension for ChatGPT plugin. Which would explain v3 run_gpt_prompt_summarize_conversation

