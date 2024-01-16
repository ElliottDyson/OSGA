"""
Original Author: Joon Sung Park (joonspk@stanford.edu)
New Authors/Editors: OSGA Community, OSGA Community Organiser: Elliott Dyson (elliottdysondesigns@gmail.com)

File: run_gpt_prompt.py
Description: Defines all run gpt prompt functions. These functions directly
interface with the safe_generate_response function.
"""
import re
import datetime
import sys
import traceback
#Logging Setup
import logging
import time
from utils import *

debug_level = debug_run_gpt_prompt # Set in utils.py
logging.basicConfig(level=debug_level)
"""
logging.debug('This is a debug message.')
logging.info('This is an info message.')
logging.warning('This is a warning message.')
logging.error('This is an error message.')
logging.critical('This is a critical message.')
"""
#Logging Setup

sys.path.append('../../')

from global_methods import *
from persona.prompt_template.gpt_structure import *
from persona.prompt_template.print_prompt import *

def get_random_alphanumeric(i=6, j=6): 
  """
  Returns a random alpha numeric strength that has the length of somewhere
  between i and j. 

  INPUT: 
    i: min_range for the length
    j: max_range for the length
  OUTPUT: 
    an alpha numeric str with the length of somewhere between i and j.
  """
  k = random.randint(i, j)
  x = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
  return x

def temp_sleep(seconds=0.0):
    time.sleep(seconds)

def adjust_durations(tasks, total_allowed):
    total_duration = sum(duration for _, duration in tasks)

    if total_duration == total_allowed:
        return tasks  # No adjustment needed if durations match

    adjusted_tasks = tasks.copy()

    if total_duration < total_allowed:
        # Distribute additional time when total duration is less
        additional_time = total_allowed - total_duration
        for i in range(additional_time):
            adjusted_tasks[i % len(tasks)][1] += 1
    else:
        # Adjust durations proportionally when total duration is more
        factor = total_allowed / total_duration
        adjusted_tasks = [[task, int(duration * factor)] for task, duration in tasks]

        # Distribute any rounding differences
        total_adjusted = sum(duration for _, duration in adjusted_tasks)
        i = 0
        while total_adjusted < total_allowed:
            adjusted_tasks[i][1] += 1
            total_adjusted += 1
            i = (i + 1) % len(adjusted_tasks)

    return adjusted_tasks

def extract_quoted_text(gpt_response, default=""):
    # The regular expression now matches text inside double quotes ("") or single quotes ('')
    match = re.search(r'"([^"]*)"|\'([^\']*)\'', gpt_response)
    if match:
        # Group 1 is for double quotes, group 2 is for single quotes
        value = match.group(1) if match.group(1) else match.group(2)
        return value
    else:
        return (default)

##############################################################################
# CHAPTER 1: Run GPT Prompt
##############################################################################

def run_gpt_prompt_wake_up_hour(persona, test_input=None, verbose=False): 
  """
  Given the persona, returns an integer that indicates the hour when the 
  persona wakes up.  

  INPUT: 
    persona: The Persona class instance 
  OUTPUT: 
    integer for the wake up hour.
  """
  def create_prompt_input(persona, test_input=None): 
    if test_input: return test_input
    prompt_input = [persona.scratch.get_str_iss(),
                    persona.scratch.get_str_lifestyle(),
                    persona.scratch.get_str_firstname()]
    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    cleaned_response = gpt_response.lower().strip()
    if "am" in cleaned_response:
        cleaned_response = cleaned_response.split("am")[0].strip()  # Remove the 'am'
    if ":" in cleaned_response:
        cleaned_response = cleaned_response.split(":")[0].strip()  # Extract the hour portion
    cr = int(cleaned_response)
    return cr

  def get_fail_safe(): 
    fs = 8
    return fs

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 5, 
             "temperature": 0, "top_p": 1, "stream": False,
             "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
  prompt_template = "persona/prompt_template/v2/wake_up_hour_v1.txt"
  prompt_input = create_prompt_input(persona, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()
  
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_wake_up_hour")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_daily_plan(persona, 
                              wake_up_hour, 
                              test_input=None, 
                              verbose=False):
  """
  Basically the long term planning that spans a day. Returns a list of actions
  that the persona will take today. Usually comes in the following form: 
  'wake up and complete the morning routine at 6:00 am', 
  'eat breakfast at 7:00 am',.. 
  Note that the actions come without a period. 

  INPUT: 
    persona: The Persona class instance 
  OUTPUT: 
    a list of daily actions in broad strokes.
  """
  def create_prompt_input(persona, wake_up_hour, test_input=None):
    if test_input: return test_input
    prompt_input = []
    prompt_input += [persona.scratch.get_str_iss()]
    prompt_input += [persona.scratch.get_str_lifestyle()]
    prompt_input += [persona.scratch.get_str_curr_date_str()]
    prompt_input += [persona.scratch.get_str_firstname()]
    prompt_input += [f"{str(wake_up_hour)}:00 am"]
    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    """
      Parses the provided text to extract activities and their corresponding times or notes, ensuring all activities are captured.

      Args:
      input_text (str): A string containing activities with time schedules or notes.

      Returns:
      list of tuples: A list where each tuple contains an activity and its corresponding time or note.
      """
    activities = []

    # Adjusted regex pattern for activities with times or notes
    activity_pattern = r'(\d+)\) (.*?)(?=\n\d+\)|$)'

    matches = re.finditer(activity_pattern, gpt_response, re.DOTALL)

    for match in matches:
        activity_number = int(match.group(1))
        activity_description = match.group(2).strip()
        activities.append(activity_description)

    return activities

  def get_fail_safe(): 
    fs = ['wake up and complete the morning routine at 6:00 am', 
          'eat breakfast at 7:00 am', 
          'read a book from 8:00 am to 12:00 pm', 
          'have lunch at 12:00 pm', 
          'take a nap from 1:00 pm to 4:00 pm', 
          'relax and watch TV from 7:00 pm to 8:00 pm', 
          'go to bed at 11:00 pm'] 
    return fs
  
  gpt_param = {"engine": "text-davinci-003", "max_tokens": 500, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/daily_planning_v6.txt"
  prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()

  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
          
  output = ([f"wake up and complete the morning routine at {wake_up_hour}:00 am"]
              + output)

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  
  # TODO: doesnt provide full day. 
    
  # TODO: doesnt provide full day. 
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_generate_hourly_schedule(persona, 
                                            curr_hour_str,
                                            p_f_ds_hourly_org, 
                                            hour_str,
                                            intermission2=None,
                                            test_input=None, 
                                            verbose=False): 
  def create_prompt_input(persona, 
                          curr_hour_str, 
                          p_f_ds_hourly_org,
                          hour_str,
                          intermission2=None,
                          test_input=None): 
    if test_input: return test_input
    schedule_format = ""
    for i in hour_str: 
      schedule_format += f"[{persona.scratch.get_str_curr_date_str()} -- {i}]"
      schedule_format += f" Activity: [Fill in]\n"
    schedule_format = schedule_format[:-1]

    intermission_str = f"Here is some of what"
    intermission_str += f" {persona.scratch.get_str_firstname()} wants to get done today: "
    for count, i in enumerate(persona.scratch.daily_req): 
      intermission_str += f"{str(count+1)}) {i}, "
    intermission_str = intermission_str[:-2]

    prior_schedule = ""
    if p_f_ds_hourly_org: 
      prior_schedule = "\n"
      for count, i in enumerate(p_f_ds_hourly_org): 
        #prior_schedule += f"[(ID:{get_random_alphanumeric()})" Commented out since there is not reason that can be seen for it to be here, and it was causing bad quality outputs
        prior_schedule += f" {persona.scratch.get_str_curr_date_str()} --"
        prior_schedule += f" {hour_str[count]}] Activity:"
        prior_schedule += f" {persona.scratch.get_str_firstname()}"
        prior_schedule += f" is {i}\n"

    #prompt_ending = f"[(ID:{get_random_alphanumeric()})" Commented out since there is not reason that can be seen for it to be here, and it was causing bad quality outputs
    prompt_ending = f" {persona.scratch.get_str_curr_date_str()}" # Adjusted from '+=' to '=' due to removal of 'get_random_alphanumeric()'
    prompt_ending += f" -- {curr_hour_str}] Activity:"
    prompt_ending += f" {persona.scratch.get_str_firstname()} is"

    if intermission2: 
      intermission2 = f"\n{intermission2}"

    prompt_input = []
    prompt_input += [schedule_format]
    prompt_input += [persona.scratch.get_str_iss()]

    prompt_input += [prior_schedule + "\n"]
    prompt_input += [intermission_str]
    if intermission2: 
      prompt_input += [intermission2]
    else: 
      prompt_input += [""]
    prompt_input += [prompt_ending]

    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    cr = gpt_response.strip()
    if cr[-1] == ".":
      cr = cr[:-1]
    return cr

  def get_fail_safe(): 
    fs = "asleep"
    return fs

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 50, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0.5, "stop": ["\n"]}
  prompt_template = "persona/prompt_template/v2/generate_hourly_schedule_v2.txt"
  prompt_input = create_prompt_input(persona, 
                                     curr_hour_str, 
                                     p_f_ds_hourly_org,
                                     hour_str, 
                                     intermission2,
                                     test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()
  
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_generate_hourly_schedule")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
  
  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_task_decomp(persona, 
                               task, 
                               duration, 
                               test_input=None, 
                               verbose=False): 
  def create_prompt_input(persona, task, duration, test_input=None):

    """
    Today is Saturday June 25. From 00:00 ~ 06:00am, Maeve is 
    planning on sleeping, 06:00 ~ 07:00am, Maeve is 
    planning on waking up and doing her morning routine, 
    and from 07:00am ~08:00am, Maeve is planning on having breakfast.  
    """
      
    curr_f_org_index = persona.scratch.get_f_daily_schedule_hourly_org_index()
    all_indices = []
    # if curr_f_org_index > 0: 
    #   all_indices += [curr_f_org_index-1]
    all_indices += [curr_f_org_index]
    if curr_f_org_index+1 <= len(persona.scratch.f_daily_schedule_hourly_org): 
      all_indices += [curr_f_org_index+1]
    if curr_f_org_index+2 <= len(persona.scratch.f_daily_schedule_hourly_org): 
      all_indices += [curr_f_org_index+2]

    curr_time_range = ""

    print ("DEBUG")
    print (persona.scratch.f_daily_schedule_hourly_org)
    print (all_indices)

    summ_str = f'Today is {persona.scratch.curr_time.strftime("%B %d, %Y")}. '
    summ_str += f'From '
    for index in all_indices: 
      print ("index", index)
      if index < len(persona.scratch.f_daily_schedule_hourly_org): 
        start_min = 0
        for i in range(index): 
          start_min += persona.scratch.f_daily_schedule_hourly_org[i][1]
        end_min = start_min + persona.scratch.f_daily_schedule_hourly_org[index][1]
        start_time = (datetime.datetime.strptime("00:00:00", "%H:%M:%S") 
                      + datetime.timedelta(minutes=start_min)) 
        end_time = (datetime.datetime.strptime("00:00:00", "%H:%M:%S") 
                      + datetime.timedelta(minutes=end_min)) 
        start_time_str = start_time.strftime("%H:%M%p")
        end_time_str = end_time.strftime("%H:%M%p")
        summ_str += f"{start_time_str} ~ {end_time_str}, {persona.name} is planning on {persona.scratch.f_daily_schedule_hourly_org[index][0]}, "
        if curr_f_org_index+1 == index:
          curr_time_range = f'{start_time_str} ~ {end_time_str}'
    summ_str = summ_str[:-2] + "."

    prompt_input = []
    prompt_input += [persona.scratch.get_str_iss()]
    prompt_input += [summ_str]
    prompt_input += [persona.scratch.get_str_firstname()]
    prompt_input += [persona.scratch.get_str_firstname()]
    prompt_input += [task]
    prompt_input += [curr_time_range]
    prompt_input += [duration]
    prompt_input += [persona.scratch.get_str_firstname()]
    return prompt_input

  def __func_clean_up(gpt_response, duration):
    pattern = r"\d+[\.\)]\s*(.+?)\s*\(duration in minutes:\s*(\d+),\s*minutes left:\s*\d+\)"

    parsed_data = re.findall(pattern, gpt_response)
    formatted_data = [[task, int(duration)] for task, duration in parsed_data]

    total_expected_min = int(duration)
    
    return adjust_durations(formatted_data, total_expected_min)

  def get_fail_safe(): 
    fs = [["asleep", 0]]
    return fs

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 1500, 
             "temperature": 0.2, "top_p": 0.1, "stream": False,
             "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/task_decomp_v3.txt"
  prompt_input = create_prompt_input(persona, task, duration)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()

  print ("?????")
  print (prompt)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, duration)
          #TODO: Maybe check times
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  # TODO THERE WAS A BUG HERE... 
  # This is for preventing overflows...
  """
  File "/Users/joonsungpark/Desktop/Stanford/Projects/
  generative-personas/src_exploration/reverie_simulation/
  brain/get_next_action_v3.py", line 364, in run_gpt_prompt_task_decomp
  fin_output[-1][1] += (duration - ftime_sum)
  IndexError: list index out of range
  """

  print ("IMPORTANT VVV DEBUG")

  # print (prompt_input)
  # print (prompt)
  print (output)

  task_decomp = output
  ret = []
  for decomp_task, duration in task_decomp: 
    ret += [[f"{task} ({decomp_task})", duration]]
  output = ret

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_action_sector(action_description, 
                                persona, 
                                maze, 
                                test_input=None, 
                                verbose=False):
  def create_prompt_input(action_description, persona, maze, test_input=None): 
    act_world = f"{maze.access_tile(persona.scratch.curr_tile)['world']}"
    
    prompt_input = []
    
    prompt_input += [persona.scratch.get_str_name()]
    prompt_input += [persona.scratch.living_area.split(":")[1]]
    x = f"{act_world}:{persona.scratch.living_area.split(':')[1]}"
    prompt_input += [persona.s_mem.get_str_accessible_sector_arenas(x)]


    prompt_input += [persona.scratch.get_str_name()]
    prompt_input += [f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"]
    x = f"{act_world}:{maze.access_tile(persona.scratch.curr_tile)['sector']}"
    prompt_input += [persona.s_mem.get_str_accessible_sector_arenas(x)]

    if persona.scratch.get_str_daily_plan_req() != "": 
      prompt_input += [f"\n{persona.scratch.get_str_daily_plan_req()}"]
    else: 
      prompt_input += [""]

    # MAR 11 TEMP -                     What is all this?
    accessible_sector_str = persona.s_mem.get_str_accessible_sectors(act_world)
    curr = accessible_sector_str.split(", ")
    fin_accessible_sectors = []
    for i in curr: 
      if "'s house" in i: 
        if persona.scratch.last_name in i: 
          fin_accessible_sectors += [i]
      else: 
        fin_accessible_sectors += [i]
    accessible_sector_str = ", ".join(fin_accessible_sectors)
    # END MAR 11 TEMP

    prompt_input += [accessible_sector_str]

    action_description_1 = action_description
    action_description_2 = action_description
    if "(" in action_description: 
      action_description_1 = action_description.split("(")[0].strip()
      action_description_2 = action_description.split("(")[-1][:-1]
    prompt_input += [persona.scratch.get_str_name()]
    prompt_input += [action_description_1]

    prompt_input += [action_description_2]
    prompt_input += [persona.scratch.get_str_name()]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return extract_quoted_text(gpt_response, "kitchen")
  
  def get_fail_safe(): 
    fs = ("kitchen")
    return fs

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 15, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v1/action_location_sector_v1.txt"
  prompt_input = create_prompt_input(action_description, persona, maze)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  act_world = f"{maze.access_tile(persona.scratch.curr_tile)['world']}"
  accessible_sector_str = persona.s_mem.get_str_accessible_sectors(act_world)
  curr = accessible_sector_str.split(", ")
  fin_accessible_sectors = []
  for i in curr: 
    if "'s house" in i: 
      if persona.scratch.last_name in i: 
        fin_accessible_sectors += [i]
    else: 
      fin_accessible_sectors += [i]

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_action_sector")
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
          
  y = f"{maze.access_tile(persona.scratch.curr_tile)['world']}"
  x = [i.strip() for i in persona.s_mem.get_str_accessible_sectors(y).split(",")]
  if output not in x: 
    # output = random.choice(x)
    output = persona.scratch.living_area.split(":")[1]

  print ("DEBUG", random.choice(x), "------", output)

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)

  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_action_arena(action_description, 
                                persona, 
                                maze, act_world, act_sector,
                                test_input=None, 
                                verbose=False):
  def create_prompt_input(action_description, persona, maze, act_world, act_sector, test_input=None): 
    prompt_input = []
    # prompt_input += [persona.scratch.get_str_name()]
    # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
    # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["sector"]]
    prompt_input += [persona.scratch.get_str_name()]
    x = f"{act_world}:{act_sector}"
    prompt_input += [act_sector]

    # MAR 11 TEMP
    accessible_arena_str = persona.s_mem.get_str_accessible_sector_arenas(x)
    curr = accessible_arena_str.split(", ")
    fin_accessible_arenas = []
    for i in curr: 
      if "'s room" in i: 
        if persona.scratch.last_name in i: 
          fin_accessible_arenas += [i]
      else: 
        fin_accessible_arenas += [i]
    accessible_arena_str = ", ".join(fin_accessible_arenas)
    # END MAR 11 TEMP

    prompt_input += [accessible_arena_str]

    action_description_1 = action_description
    action_description_2 = action_description
    if "(" in action_description: 
      action_description_1 = action_description.split("(")[0].strip()
      action_description_2 = action_description.split("(")[-1][:-1]
    prompt_input += [persona.scratch.get_str_name()]
    prompt_input += [action_description_1]

    prompt_input += [action_description_2]
    prompt_input += [persona.scratch.get_str_name()]

    prompt_input += [act_sector]

    prompt_input += [accessible_arena_str]

    prompt_input = []
    prompt_input += [action_description]
    prompt_input += [accessible_arena_str]
    
    # prompt_input += [maze.access_tile(persona.scratch.curr_tile)["arena"]]
    # x = f"{maze.access_tile(persona.scratch.curr_tile)['world']}:{maze.access_tile(persona.scratch.curr_tile)['sector']}:{maze.access_tile(persona.scratch.curr_tile)['arena']}"
    # prompt_input += [persona.s_mem.get_str_accessible_arena_game_objects(x)]

    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    return extract_quoted_text(gpt_response, "kitchen")
  
  def get_fail_safe(): 
    fs = ("kitchen")
    return fs

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 15, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v1/action_location_object_vMar11.txt"
  prompt_input = create_prompt_input(action_description, persona, maze, act_world, act_sector)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          # if "}" not in output:
          #   raise Exception("'}' was not found in the response")
          # if len(output.strip()) < 1: 
          #   raise Exception("The length of the stripped output was less than 1")
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
  print (output)
  # y = f"{act_world}:{act_sector}"
  # x = [i.strip() for i in persona.s_mem.get_str_accessible_sector_arenas(y).split(",")]
  # if output not in x: 
  #   output = random.choice(x)

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)

  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_action_game_object(action_description, 
                                      persona, 
                                      maze,
                                      temp_address,
                                      test_input=None, 
                                      verbose=False): 
  def create_prompt_input(action_description, 
                          persona, 
                          temp_address, 
                          test_input=None): 
    prompt_input = []
    if "(" in action_description: 
      action_description = action_description.split("(")[-1][:-1]
      
    prompt_input += [action_description]
    prompt_input += [persona
                     .s_mem.get_str_accessible_arena_game_objects(temp_address)]
    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    return extract_quoted_text(gpt_response, "bed")

  def get_fail_safe(): 
    fs = ("bed")
    return fs

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 15, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v1/action_object_v2.txt"
  prompt_input = create_prompt_input(action_description, 
                                     persona, 
                                     temp_address, 
                                     test_input)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_action_game_object")
          
          output = generate_response(prompt, gpt_param)
          if len(output.strip()) < 1: 
            raise Exception("The length of the stripped output was less than 1")
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  x = [i.strip() for i in persona.s_mem.get_str_accessible_arena_game_objects(temp_address).split(",")]
  if output not in x: 
    output = random.choice(x)

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_pronunciation(action_description, persona, verbose=False): 
  def create_prompt_input(action_description): 
    if "(" in action_description: 
      action_description = action_description.split("(")[-1].split(")")[0]
    prompt_input = [action_description]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    cr = gpt_response.strip()
    if len(cr) > 3:
      cr = cr[:3]
    return cr

  def get_fail_safe(): 
    fs = "😋"
    return fs

  gpt_param = {"engine": "text-davinci-002", "max_tokens": 15, 
               "temperature": 0.2, "top_p": 0.5, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/generate_pronunciation_v1.txt"
  prompt_input = create_prompt_input(action_description)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          if len(output.strip()) == 0: 
            raise Exception("The length of the stripped output was 0")
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
      print_run_prompts(prompt_template, persona, gpt_param, 
                        prompt_input, prompt, output)

  return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_event_triple(action_description, persona, verbose=False): 
  def create_prompt_input(action_description, persona): 
    if "(" in action_description: 
      action_description = action_description.split("(")[-1].split(")")[0]
    prompt_input = [persona.name, 
                    action_description,
                    persona.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    # The regular expression matches all text inside double quotes ("") or single quotes ('')
    matches = re.findall(r'"(.*?)"|\'(.*?)\'', gpt_response, re.DOTALL)
    if matches:
        # Extracting all matched groups, considering both double and single quotes
        all_quotes = [match[0] or match[1] for match in matches]
        return all_quotes
    else:
        # If no quotes are found, return the original gpt_response
        return (persona.name, "is", "idle")

  def get_fail_safe(persona): 
    fs = (persona.name, "is", "idle")
    return fs

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 100, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/generate_event_triple_v1.txt"
  prompt_input = create_prompt_input(action_description, persona)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe(persona)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          #TODO: FAILS STILL
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          if len(output) < 2: 
            raise Exception("The length of the output was not 2")
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
          
  output = (persona.name, output[0], output[1])

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                       prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]


def run_gpt_prompt_act_obj_desc(act_game_object, act_desp, persona, verbose=False): 
  def create_prompt_input(act_game_object, act_desp, persona): 
    prompt_input = [act_game_object, 
                    persona.name,
                    act_desp,
                    act_game_object,
                    act_game_object]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    cr = gpt_response.strip()
    if cr[-1] == ".": cr = cr[:-1]
    return cr

  def get_fail_safe(act_game_object): 
    fs = f"{act_game_object} is idle"
    return fs

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 100, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
  prompt_template = "persona/prompt_template/v2/generate_obj_event_v1.txt"
  prompt_input = create_prompt_input(act_game_object, act_desp, persona)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe(act_game_object)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_act_obj_desc")
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_act_obj_event_triple(act_game_object, act_obj_desc, persona, verbose=False): 
  def create_prompt_input(act_game_object, act_obj_desc): 
    prompt_input = [act_game_object, 
                    act_obj_desc,
                    act_game_object]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    # The regular expression matches all text inside double quotes ("") or single quotes ('')
    matches = re.findall(r'"(.*?)"|\'(.*?)\'', gpt_response, re.DOTALL)
    if matches:
        # Extracting all matched groups, considering both double and single quotes
        all_quotes = [match[0] or match[1] for match in matches]
        return all_quotes
    else:
        # If no quotes are found, return the original gpt_response
        return (act_game_object, "is", "idle")

  def get_fail_safe(act_game_object): 
    fs = (act_game_object, "is", "idle")
    return fs

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 100, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": ["\n"]}
  prompt_template = "persona/prompt_template/v2/generate_event_triple_v1.txt"
  prompt_input = create_prompt_input(act_game_object, act_obj_desc)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe(act_game_object)
  max_retries = 3

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          #TODO: Fix this it fails sometimes
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          if len(output) < 2: 
            raise Exception("The length of the output was not 2")
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
          
  output = (act_game_object, output[0], output[1])

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_new_decomp_schedule(persona, 
                                       main_act_dur, 
                                       truncated_act_dur, 
                                       start_time_hour,
                                       end_time_hour, 
                                       inserted_act,
                                       inserted_act_dur,
                                       test_input=None, 
                                       verbose=False): 
  def create_prompt_input(persona, 
                           main_act_dur, 
                           truncated_act_dur, 
                           start_time_hour,
                           end_time_hour, 
                           inserted_act,
                           inserted_act_dur,
                           test_input=None): 
    persona_name = persona.name
    start_hour_str = start_time_hour.strftime("%H:%M %p")
    end_hour_str = end_time_hour.strftime("%H:%M %p")

    original_plan = ""
    for_time = start_time_hour
    for i in main_act_dur: 
      original_plan += f'{for_time.strftime("%H:%M")} ~ {(for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M")} -- ' + i[0]
      original_plan += "\n"
      for_time += datetime.timedelta(minutes=int(i[1]))

    new_plan_init = ""
    for_time = start_time_hour
    for count, i in enumerate(truncated_act_dur): 
      new_plan_init += f'{for_time.strftime("%H:%M")} ~ {(for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M")} -- ' + i[0]
      new_plan_init += "\n"
      if count < len(truncated_act_dur) - 1: 
        for_time += datetime.timedelta(minutes=int(i[1]))

    new_plan_init += (for_time + datetime.timedelta(minutes=int(i[1]))).strftime("%H:%M") + " ~"

    prompt_input = [persona_name, 
                    start_hour_str,
                    end_hour_str,
                    original_plan,
                    persona_name,
                    inserted_act,
                    inserted_act_dur,
                    persona_name,
                    start_hour_str,
                    end_hour_str,
                    end_hour_str,
                    new_plan_init]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    new_schedule = prompt + " " + gpt_response.strip()
    new_schedule = new_schedule.split("The revised schedule:")[-1].strip().replace("</s>", "")

    # Strict regular expression pattern to extract only valid schedule lines
    strict_pattern = r'^\d{2}:\d{2} ~ \d{2}:\d{2} -- .+?\(.*?\)$'
    
    # Split the text into lines and filter out empty lines
    lines = [line.strip() for line in new_schedule.split('\n') if line.strip() and re.match(strict_pattern, line.strip())]

    tasks = []

    # Process each valid line
    for line in lines:
        # Extract time and task details
        start_time_str, end_time_str, task = re.findall(r'(\d{2}:\d{2})', line)[:2] + [re.search(r'-- (.+)$', line).group(1)]
        start_time = datetime.datetime.strptime(start_time_str, "%H:%M")
        end_time = datetime.datetime.strptime(end_time_str, "%H:%M")

        # Calculate duration in minutes
        duration = abs(int((end_time - start_time).total_seconds() / 60))
        tasks.append([task, duration])

    return tasks

  def get_fail_safe(main_act_dur, truncated_act_dur): 
    dur_sum = 0
    for act, dur in main_act_dur: dur_sum += dur

    ret = truncated_act_dur[:]
    ret += main_act_dur[len(ret)-1:]

    # If there are access, we need to trim... 
    ret_dur_sum = 0
    count = 0
    over = None
    for act, dur in ret: 
      ret_dur_sum += dur
      if ret_dur_sum == dur_sum: 
        break
      if ret_dur_sum > dur_sum: 
        over = ret_dur_sum - dur_sum
        break
      count += 1 

    if over: 
      ret = ret[:count+1]
      ret[-1][1] -= over

    return ret

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 1000, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/new_decomp_schedule_v1.txt"
  prompt_input = create_prompt_input(persona, 
                                     main_act_dur, 
                                     truncated_act_dur, 
                                     start_time_hour,
                                     end_time_hour, 
                                     inserted_act,
                                     inserted_act_dur,
                                     test_input)
  prompt = generate_prompt(prompt_input, prompt_template)
  fail_safe = get_fail_safe(main_act_dur, truncated_act_dur)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          dur_sum = 0
          for act, dur in output: 
            dur_sum += dur
            if str(type(act)) != "<class 'str'>":
              return False 
            if str(type(dur)) != "<class 'int'>":
              return False
          x = prompt.split("\n")[0].split("originally planned schedule from")[-1].strip()[:-1]
          x = [datetime.datetime.strptime(i.strip(), "%H:%M %p") for i in x.split(" to ")]
          delta_min = int((x[1] - x[0]).total_seconds()/60)
          if int(dur_sum) != int(delta_min):
            output = adjust_durations(output, int(delta_min))
            
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
  
  # print ("* * * * output")
  # print (output)
  # print ('* * * * fail_safe')
  # print (fail_safe)

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_decide_to_talk(persona, target_persona, retrieved,test_input=None, 
                                       verbose=False): 
  def create_prompt_input(init_persona, target_persona, retrieved, 
                          test_input=None): 
    last_chat = init_persona.a_mem.get_last_chat(target_persona.name)
    last_chatted_time = ""
    last_chat_about = ""
    if last_chat: 
      last_chatted_time = last_chat.created.strftime("%B %d, %Y, %H:%M:%S")
      last_chat_about = last_chat.description

    context = ""
    for c_node in retrieved["events"]: 
      curr_desc = c_node.description.split(" ")
      curr_desc[2:3] = ["was"]
      curr_desc = " ".join(curr_desc)
      context +=  f"{curr_desc}. "
    context += "\n"
    for c_node in retrieved["thoughts"]: 
      context +=  f"{c_node.description}. "

    curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
    init_act_desc = init_persona.scratch.act_description
    if "(" in init_act_desc: 
      init_act_desc = init_act_desc.split("(")[-1][:-1]
    
    if len(init_persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc: 
      init_p_desc = f"{init_persona.name} is already {init_act_desc}"
    elif "waiting" in init_act_desc:
      init_p_desc = f"{init_persona.name} is {init_act_desc}"
    else: 
      init_p_desc = f"{init_persona.name} is on the way to {init_act_desc}"

    target_act_desc = target_persona.scratch.act_description
    if "(" in target_act_desc: 
      target_act_desc = target_act_desc.split("(")[-1][:-1]
    
    if len(target_persona.scratch.planned_path) == 0 and "waiting" not in init_act_desc: 
      target_p_desc = f"{target_persona.name} is already {target_act_desc}"
    elif "waiting" in init_act_desc:
      target_p_desc = f"{init_persona.name} is {init_act_desc}"
    else: 
      target_p_desc = f"{target_persona.name} is on the way to {target_act_desc}"


    prompt_input = []
    prompt_input += [context]

    prompt_input += [curr_time]

    prompt_input += [init_persona.name]
    prompt_input += [target_persona.name]
    prompt_input += [last_chatted_time]
    prompt_input += [last_chat_about]


    prompt_input += [init_p_desc]
    prompt_input += [target_p_desc]
    prompt_input += [init_persona.name]
    prompt_input += [target_persona.name]
    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    # Regular expression pattern to find 'yes' or 'no' (case-insensitive)
    pattern = r'\b(?:yes|no)\b'
    matches = re.findall(pattern, gpt_response.lower(), re.IGNORECASE)

    # Return the first match if any, otherwise return None
    return matches[0] if matches else "yes"
  

  def get_fail_safe(): 
    fs = "yes"
    return fs

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 200, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/decide_to_talk_v2.txt"
  prompt_input = create_prompt_input(persona, target_persona, retrieved,
                                     test_input)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          if output not in ["yes", "no"]: 
            raise Exception("The answer did not contain either 'yes', nor 'no'")
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_decide_to_react(persona, target_persona, retrieved,test_input=None, 
                                       verbose=False): 
  def create_prompt_input(init_persona, target_persona, retrieved, 
                          test_input=None): 
    context = ""
    for c_node in retrieved["events"]: 
      curr_desc = c_node.description.split(" ")
      curr_desc[2:3] = ["was"]
      curr_desc = " ".join(curr_desc)
      context +=  f"{curr_desc}. "
    context += "\n"
    for c_node in retrieved["thoughts"]: 
      context +=  f"{c_node.description}. "

    curr_time = init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S %p")
    init_act_desc = init_persona.scratch.act_description
    if "(" in init_act_desc: 
      init_act_desc = init_act_desc.split("(")[-1][:-1]
    if len(init_persona.scratch.planned_path) == 0: 
      loc = ""
      if ":" in init_persona.scratch.act_address:
        loc = init_persona.scratch.act_address.split(":")[-1] + " in " + init_persona.scratch.act_address.split(":")[-2]
      init_p_desc = f"{init_persona.name} is already {init_act_desc} at {loc}"
    else: 
      loc = ""
      if ":" in init_persona.scratch.act_address:
        loc = init_persona.scratch.act_address.split(":")[-1] + " in " + init_persona.scratch.act_address.split(":")[-2]
      init_p_desc = f"{init_persona.name} is on the way to {init_act_desc} at {loc}"

    target_act_desc = target_persona.scratch.act_description
    if "(" in target_act_desc: 
      target_act_desc = target_act_desc.split("(")[-1][:-1]
    if len(target_persona.scratch.planned_path) == 0: 
      loc = ""
      if ":" in target_persona.scratch.act_address:
        loc = target_persona.scratch.act_address.split(":")[-1] + " in " + target_persona.scratch.act_address.split(":")[-2]
      target_p_desc = f"{target_persona.name} is already {target_act_desc} at {loc}"
    else: 
      loc = ""
      if ":" in target_persona.scratch.act_address:
        loc = target_persona.scratch.act_address.split(":")[-1] + " in " + target_persona.scratch.act_address.split(":")[-2]
      target_p_desc = f"{target_persona.name} is on the way to {target_act_desc} at {loc}"

    prompt_input = []
    prompt_input += [context]
    prompt_input += [curr_time]
    prompt_input += [init_p_desc]
    prompt_input += [target_p_desc]

    prompt_input += [init_persona.name]
    prompt_input += [init_act_desc]
    prompt_input += [target_persona.name]
    prompt_input += [target_act_desc]

    prompt_input += [init_act_desc]
    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split("Answer: Option")[-1].strip().lower() 

  def get_fail_safe(): 
    fs = "3"
    return fs

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 100, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/decide_to_react_v1.txt"
  prompt_input = create_prompt_input(persona, target_persona, retrieved,
                                     test_input)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          
          print("run_gpt_prompt_decide_to_react")
          output = generate_response(prompt, gpt_param)
          if output.split("Answer: Option")[-1].strip().lower() not in ["3", "2", "1"]: 
            raise Exception("The answer did not contain an option selection '1', '2', nor '3'")
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_create_conversation(persona, target_persona, curr_loc,
                                       test_input=None, verbose=False): 
  def create_prompt_input(init_persona, target_persona, curr_loc, 
                          test_input=None): 

    prev_convo_insert = "\n"
    if init_persona.a_mem.seq_chat: 
      for i in init_persona.a_mem.seq_chat: 
        if i.object == target_persona.scratch.name: 
          v1 = int((init_persona.scratch.curr_time - i.created).total_seconds()/60)
          prev_convo_insert += f'{str(v1)} minutes ago, they had the following conversation.\n'
          for row in i.filling: 
            prev_convo_insert += f'{row[0]}: "{row[1]}"\n'
          break
    if prev_convo_insert == "\n": 
      prev_convo_insert = ""
    if init_persona.a_mem.seq_chat: 
      if int((init_persona.scratch.curr_time - init_persona.a_mem.seq_chat[-1].created).total_seconds()/60) > 480: 
        prev_convo_insert = ""


    init_persona_thought_nodes = init_persona.a_mem.retrieve_relevant_thoughts(target_persona.scratch.act_event[0],
                                target_persona.scratch.act_event[1],
                                target_persona.scratch.act_event[2])
    init_persona_thought = ""
    for i in init_persona_thought_nodes: 
      init_persona_thought += f"-- {i.description}\n"

    target_persona_thought_nodes = target_persona.a_mem.retrieve_relevant_thoughts(init_persona.scratch.act_event[0],
                                init_persona.scratch.act_event[1],
                                init_persona.scratch.act_event[2])
    target_persona_thought = ""
    for i in target_persona_thought_nodes: 
      target_persona_thought += f"-- {i.description}\n"

    init_persona_curr_desc = ""
    if init_persona.scratch.planned_path: 
      init_persona_curr_desc = f"{init_persona.name} is on the way to {init_persona.scratch.act_description}"
    else: 
      init_persona_curr_desc = f"{init_persona.name} is {init_persona.scratch.act_description}"

    target_persona_curr_desc = ""
    if target_persona.scratch.planned_path: 
      target_persona_curr_desc = f"{target_persona.name} is on the way to {target_persona.scratch.act_description}"
    else: 
      target_persona_curr_desc = f"{target_persona.name} is {target_persona.scratch.act_description}"
 

    curr_loc = curr_loc["arena"]

    prompt_input = []
    prompt_input += [init_persona.scratch.get_str_iss()]
    prompt_input += [target_persona.scratch.get_str_iss()]

    prompt_input += [init_persona.name]
    prompt_input += [target_persona.name]
    prompt_input += [init_persona_thought]

    prompt_input += [target_persona.name]
    prompt_input += [init_persona.name]
    prompt_input += [target_persona_thought]

    prompt_input += [init_persona.scratch.curr_time.strftime("%B %d, %Y, %H:%M:%S")]

    prompt_input += [init_persona_curr_desc]
    prompt_input += [target_persona_curr_desc]

    prompt_input += [prev_convo_insert]

    prompt_input += [init_persona.name]
    prompt_input += [target_persona.name]

    prompt_input += [curr_loc]
    prompt_input += [init_persona.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    # print ("???")
    # print (gpt_response)


    gpt_response = (prompt + gpt_response).split("What would they talk about now?")[-1].strip()
    content = re.findall('"([^"]*)"', gpt_response)

    speaker_order = []
    for i in gpt_response.split("\n"): 
      name = i.split(":")[0].strip() 
      if name: 
        speaker_order += [name]

    ret = []
    for count, speaker in enumerate(speaker_order): 
      ret += [[speaker, content[count]]]

    return ret

  def get_fail_safe(init_persona, target_persona): 
    convo = [[init_persona.name, "Hi!"], 
             [target_persona.name, "Hi!"]]
    return convo

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 1000, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/create_conversation_v2.txt"
  prompt_input = create_prompt_input(persona, target_persona, curr_loc, 
                                     test_input)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe(persona, target_persona)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          
          print("run_gpt_prompt_create_conversation")
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_summarize_conversation(persona, conversation, test_input=None, verbose=False): 
  def create_prompt_input(conversation, test_input=None): 
    convo_str = ""
    for row in conversation: 
      convo_str += f'{row[0]}: "{row[1]}"\n'

    prompt_input = [convo_str]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    ret = "conversing about " + gpt_response.strip()
    return ret

  def get_fail_safe(): 
    return "conversing with a housemate about morning greetings"

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 50, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/summarize_conversation_v1.txt"
  prompt_input = create_prompt_input(conversation, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          
          print("run_gpt_prompt_summarize_conversation")
          # output = generate_response(prompt, gpt_param)
          # output = __func_clean_up(output, prompt=prompt)
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]

  

def run_gpt_prompt_extract_keywords(persona, description, test_input=None, verbose=False): 
  def create_prompt_input(description, test_input=None): 
    if "\n" in description: 
      description = description.replace("\n", " <LINE_BREAK> ")
    prompt_input = [description]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    print ("???")
    print (gpt_response)
    gpt_response = gpt_response.strip().split("Emotive keywords:")
    factual = [i.strip() for i in gpt_response[0].split(",")]
    emotive = [i.strip() for i in gpt_response[1].split(",")]
    all_keywords = factual + emotive
    ret = []
    for i in all_keywords: 
      if i: 
        i = i.lower()
        if i[-1] == ".": 
          i = i[:-1]
        ret += [i]
    print (ret)
    return set(ret)

  def get_fail_safe(): 
    return []

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 50, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/get_keywords_v1.txt"
  prompt_input = create_prompt_input(description, test_input)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_extract_keywords")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_keyword_to_thoughts(persona, keyword, concept_summary, test_input=None, verbose=False): 
  def create_prompt_input(persona, keyword, concept_summary, test_input=None): 
    prompt_input = [keyword, concept_summary, persona.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    gpt_response = gpt_response.strip()
    return gpt_response

  def get_fail_safe(): 
    return ""

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 40, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/keyword_to_thoughts_v1.txt"
  prompt_input = create_prompt_input(persona, keyword, concept_summary)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_keyword_to_thoughts")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_convo_to_thoughts(persona, 
                                    init_persona_name,  
                                    target_persona_name,
                                    convo_str,
                                    fin_target, test_input=None, verbose=False): 
  def create_prompt_input(init_persona_name,  
                                    target_persona_name,
                                    convo_str,
                                    fin_target, test_input=None): 
    prompt_input = [init_persona_name,
                    target_persona_name,
                    convo_str,
                    init_persona_name,
                    fin_target]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    gpt_response = gpt_response.strip()
    return gpt_response

  def get_fail_safe(): 
    return ""

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 40, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/convo_to_thoughts_v1.txt"
  prompt_input = create_prompt_input(init_persona_name,  
                                    target_persona_name,
                                    convo_str,
                                    fin_target)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_convo_to_thoughts")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_event_poignancy(persona, event_description, test_input=None, verbose=False): 
  def create_prompt_input(persona, event_description, test_input=None): 
    prompt_input = [persona.scratch.name,
                    persona.scratch.get_str_iss(),
                    persona.scratch.name,
                    event_description]
    return prompt_input
  
  def get_fail_safe(): 
    return 4

  def __func_clean_up(gpt_response, prompt=""):
    # Regular expression to find a number within single quotes
    pattern = r"(\d+)"
    
    # Search for the pattern in the text
    match = re.search(pattern, gpt_response)
    
    # If a match is found, return the number, otherwise return None
    if match:
        return int(match.group(1))
    else:
        return get_fail_safe()

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 3, 
              "temperature": 0.2, "top_p": 0.1, "stream": False,
              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/poignancy_event_v1.txt"
  prompt_input = create_prompt_input(persona, event_description)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
          
  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_thought_poignancy(persona, event_description, test_input=None, verbose=False): 
  def create_prompt_input(persona, event_description, test_input=None): 
    prompt_input = [persona.scratch.name,
                    persona.scratch.get_str_iss(),
                    persona.scratch.name,
                    event_description]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    gpt_response = int(gpt_response.strip())
    return gpt_response

  def get_fail_safe(): 
    return 4

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 3, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/poignancy_thought_v1.txt"
  prompt_input = create_prompt_input(persona, event_description)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_thought_poignancy")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_chat_poignancy(persona, event_description, test_input=None, verbose=False): 
  def create_prompt_input(persona, event_description, test_input=None): 
    prompt_input = [persona.scratch.name,
                    persona.scratch.get_str_iss(),
                    persona.scratch.name,
                    event_description]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    # Regular expression to find a number within single quotes
    pattern = r"(\d+)"
    
    # Search for the pattern in the text
    match = re.search(pattern, gpt_response)
    
    # If a match is found, return the number, otherwise return None
    if match:
        return int(match.group(1))
    else:
        return get_fail_safe()

  def get_fail_safe(): 
    return 4

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 3, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/poignancy_chat_v1.txt"
  prompt_input = create_prompt_input(persona, event_description)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_chat_poignancy")
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_focal_pt(persona, statements, n, test_input=None, verbose=False): 
  def create_prompt_input(persona, statements, n, test_input=None): 
    prompt_input = [statements, str(n)]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    # Applying the regex pattern to the text
    pattern = r'\d+[.)]\s*(.+?)(?=\n\d+[.)]|\Z)'

    # Applying the updated regex pattern to the text
    parsed_questions = re.findall(pattern, gpt_response, re.DOTALL)
    return parsed_questions

  def get_fail_safe(n): 
    return ["Who am I"] * n

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 500, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/generate_focal_pt_v1.txt"
  prompt_input = create_prompt_input(persona, statements, n)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe(n)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]


  
def run_gpt_prompt_insight_and_guidance(persona, statements, n, test_input=None, verbose=False): 
  def create_prompt_input(persona, statements, n, test_input=None): 
    prompt_input = [statements, str(n)]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    """
    Parses the provided text to extract insights and their corresponding IDs.

    Args:
    gpt_response (str): A string containing insights and IDs in the specified format.

    Returns:
    list of tuples: A list where each tuple contains an insight and a list of its corresponding IDs.
    """
    insights = dict()

    # Regex pattern for extracting the insight text.
    insight_regex = r'Insight: (.*?)\|'
    # Regex pattern for extracting the IDs.
    id_regex = r'IDs: \[([0-9, ]+)\]'

    segments = re.split(r'\n\n', gpt_response)
    segments = [s for s in segments if s.strip()]  # Remove empty segments

    for segment in segments:
        insight_match = re.search(insight_regex, segment)
        id_matches = re.search(id_regex, segment)

        if insight_match and id_matches:
            insight = insight_match.group(1).strip()
            ids = [int(id.strip()) for id in id_matches.group(1).split(',')]
            insights[insight] = ids

    return insights

  def get_fail_safe(n): 
    return ["I am hungry"] * n

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 500, 
               "temperature": 0.5, "top_p": 0.5, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/insight_and_evidence_v1.txt"
  prompt_input = create_prompt_input(persona, statements, n)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe(n)
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_insight_and_guidance")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_agent_chat_summarize_ideas(persona, target_persona, statements, curr_context, test_input=None, verbose=False): 
  def create_prompt_input(persona, target_persona, statements, curr_context, test_input=None): 
    prompt_input = [persona.scratch.get_str_curr_date_str(), curr_context, persona.scratch.currently, 
                    statements, persona.scratch.name, target_persona.scratch.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 150, 
              "temperature": 0.5, "top_p": 0.5, "stream": False,
              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/summarize_chat_ideas_v1.txt"
  prompt_input = create_prompt_input(persona, target_persona, statements, curr_context)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_agent_chat_summarize_ideas")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output) 
     
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]
  


def run_gpt_prompt_agent_chat_summarize_relationship(persona, target_persona, statements, test_input=None, verbose=False): 
  def create_prompt_input(persona, target_persona, statements, test_input=None): 
    prompt_input = [statements, persona.scratch.name, target_persona.scratch.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 150, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/summarize_chat_relationship_v1.txt"
  prompt_input = create_prompt_input(persona, target_persona, statements)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]
  


def run_gpt_prompt_agent_chat(maze, persona, target_persona,
                               curr_context, 
                               init_summ_idea, 
                               target_summ_idea, test_input=None, verbose=False): 
  def create_prompt_input(persona, target_persona, curr_context, init_summ_idea, target_summ_idea, test_input=None): 
    prev_convo_insert = "\n"
    if persona.a_mem.seq_chat: 
      for i in persona.a_mem.seq_chat: 
        if i.object == target_persona.scratch.name: 
          v1 = int((persona.scratch.curr_time - i.created).total_seconds()/60)
          prev_convo_insert += f'{str(v1)} minutes ago, {persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation.'
          break
    if prev_convo_insert == "\n": 
      prev_convo_insert = ""
    if persona.a_mem.seq_chat: 
      if int((persona.scratch.curr_time - persona.a_mem.seq_chat[-1].created).total_seconds()/60) > 480: 
        prev_convo_insert = ""
    print (prev_convo_insert)

    curr_sector = f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"
    curr_arena= f"{maze.access_tile(persona.scratch.curr_tile)['arena']}"
    curr_location = f"{curr_arena} in {curr_sector}"
    

    prompt_input = [persona.scratch.currently, 
                    target_persona.scratch.currently, 
                    prev_convo_insert,
                    curr_context, 
                    curr_location,

                    persona.scratch.name,
                    init_summ_idea, 
                    persona.scratch.name,
                    target_persona.scratch.name,

                    target_persona.scratch.name,
                    target_summ_idea, 
                    target_persona.scratch.name,
                    persona.scratch.name,

                    persona.scratch.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    print (gpt_response)

    gpt_response = (prompt + gpt_response).split("Here is their conversation.")[-1].strip()
    content = re.findall('"([^"]*)"', gpt_response)

    speaker_order = []
    for i in gpt_response.split("\n"): 
      name = i.split(":")[0].strip() 
      if name: 
        speaker_order += [name]

    ret = []
    for count, speaker in enumerate(speaker_order): 
      ret += [[speaker, content[count]]]

    return ret

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 2000, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/agent_chat_v1.txt"
  prompt_input = create_prompt_input(persona, target_persona, curr_context, init_summ_idea, target_summ_idea)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          
          print("run_gpt_prompt_agent_chat")
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_summarize_ideas(persona, statements, question, test_input=None, verbose=False): 
  def create_prompt_input(persona, statements, question, test_input=None): 
    prompt_input = [statements, persona.scratch.name, question]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 150, 
               "temperature": 0.5, "top_p": 0.5, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/summarize_ideas_v1.txt"
  prompt_input = create_prompt_input(persona, statements, question)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_summarize_ideas")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]
 


def run_gpt_prompt_generate_next_convo_line(persona, interlocutor_desc, prev_convo, retrieved_summary, test_input=None, verbose=False): 
  def create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary, test_input=None): 
    prompt_input = [persona.scratch.name, 
                    persona.scratch.get_str_iss(),
                    persona.scratch.name, 
                    interlocutor_desc, 
                    prev_convo, 
                    persona.scratch.name,
                    retrieved_summary, 
                    persona.scratch.name,]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 250, 
               "temperature": 0.7, "top_p": 0.8, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/generate_next_convo_line_v1.txt"
  prompt_input = create_prompt_input(persona, interlocutor_desc, prev_convo, retrieved_summary)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_generate_next_convo_line")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
    
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_generate_whisper_inner_thought(persona, whisper, test_input=None, verbose=False): 
  def create_prompt_input(persona, whisper, test_input=None): 
    prompt_input = [persona.scratch.name, whisper]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 50, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/whisper_inner_thought_v1.txt"
  prompt_input = create_prompt_input(persona, whisper)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_memo_on_convo")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_planning_thought_on_convo(persona, all_utt, test_input=None, verbose=False): 
  def create_prompt_input(persona, all_utt, test_input=None): 
    prompt_input = [all_utt, persona.scratch.name, persona.scratch.name, persona.scratch.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 50, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/planning_thought_on_convo_v1.txt"
  prompt_input = create_prompt_input(persona, all_utt)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_memo_on_convo")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def run_gpt_prompt_memo_on_convo(persona, all_utt, test_input=None, verbose=False): 
  def create_prompt_input(persona, all_utt, test_input=None): 
    prompt_input = [all_utt, persona.scratch.name, persona.scratch.name, persona.scratch.name]
    return prompt_input
  
  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.split('"')[0].strip()

  def get_fail_safe(): 
    return "..."

  gpt_param = {"engine": "gpt-3.5-turbo-1106", "max_tokens": 50, 
               "temperature": 0.2, "top_p": 0.1, "stream": False,
               "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
  prompt_template = "persona/prompt_template/v2/memo_on_convo_v1.txt"
  prompt_input = create_prompt_input(persona, all_utt)
  prompt = generate_prompt(prompt_input, prompt_template)

  fail_safe = get_fail_safe()
  max_retries = 5

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          print("run_gpt_prompt_memo_on_convo")
          
          output = generate_response(prompt, gpt_param)
          output = __func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break

  if debug or verbose: 
    print_run_prompts(prompt_template, persona, gpt_param, 
                      prompt_input, prompt, output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]



def extract_first_json_dict(data_str):
    # Find the first occurrence of a JSON object within the string
    start_idx = data_str.find('{')
    end_idx = data_str.find('}', start_idx) + 1

    # Check if both start and end indices were found
    if start_idx == -1 or end_idx == 0:
        return None

    # Extract the first JSON dictionary
    json_str = data_str[start_idx:end_idx]

    try:
        # Attempt to parse the JSON data
        json_dict = json.loads(json_str)
        return json_dict
    except json.JSONDecodeError:
        logging.critical("JSON Decode Error: extract_first_json_dict")
        return None



def run_gpt_generate_iterative_chat_utt(maze, init_persona, target_persona, retrieved, curr_context, curr_chat, test_input=None, verbose=False): 
  def create_prompt_input(maze, init_persona, target_persona, retrieved, curr_context, curr_chat, test_input=None):
    persona = init_persona
    prev_convo_insert = "\n"
    if persona.a_mem.seq_chat: 
      for i in persona.a_mem.seq_chat: 
        if i.object == target_persona.scratch.name: 
          v1 = int((persona.scratch.curr_time - i.created).total_seconds()/60)
          prev_convo_insert += f'{str(v1)} minutes ago, {persona.scratch.name} and {target_persona.scratch.name} were already {i.description} This context takes place after that conversation.'
          break
    if prev_convo_insert == "\n": 
      prev_convo_insert = ""
    if persona.a_mem.seq_chat: 
      if int((persona.scratch.curr_time - persona.a_mem.seq_chat[-1].created).total_seconds()/60) > 480: 
        prev_convo_insert = ""
    print (prev_convo_insert)

    curr_sector = f"{maze.access_tile(persona.scratch.curr_tile)['sector']}"
    curr_arena= f"{maze.access_tile(persona.scratch.curr_tile)['arena']}"
    curr_location = f"{curr_arena} in {curr_sector}"

    retrieved_str = ""
    for key, vals in retrieved.items(): 
      for v in vals: 
        retrieved_str += f"- {v.description}\n"

    convo_str = ""
    for i in curr_chat:
      convo_str += ": ".join(i) + "\n"
    if convo_str == "": 
      convo_str = "[This feels awkward, they're just staring at each other, start talking!]"

    init_iss = f"Here is Here is a brief description of {init_persona.scratch.name}.\n{init_persona.scratch.get_str_iss()}"
    prompt_input = [init_iss, init_persona.scratch.name, retrieved_str, prev_convo_insert,
      curr_location, curr_context, init_persona.scratch.name, target_persona.scratch.name,
      convo_str, init_persona.scratch.name, target_persona.scratch.name,
      init_persona.scratch.name, init_persona.scratch.name,
      init_persona.scratch.name
      ]
    return prompt_input

  def __chat_func_clean_up(gpt_response, prompt=""): 
    gpt_response = extract_first_json_dict(gpt_response)

    cleaned_dict = dict()
    cleaned = []
    for key, val in gpt_response.items(): 
      cleaned += [val]
    cleaned_dict["utterance"] = cleaned[0]
    cleaned_dict["end"] = True
    if "f" in str(cleaned[1]) or "F" in str(cleaned[1]): 
      cleaned_dict["end"] = False

    return cleaned_dict

  def get_fail_safe():
    cleaned_dict = dict()
    cleaned_dict["utterance"] = "..."
    cleaned_dict["end"] = False
    return cleaned_dict

  print ("11")
  prompt_template = "persona/prompt_template/v3_ChatGPT/iterative_convo_v1.txt" 
  prompt_input = create_prompt_input(maze, init_persona, target_persona, retrieved, curr_context, curr_chat) 
  print ("22")
  prompt = generate_prompt(prompt_input, prompt_template)
  print (prompt)
  fail_safe = get_fail_safe() 
  max_retries = 5

  gpt_param = {"engine": "text-davinci-003", "max_tokens": 500, 
              "temperature": 0.5, "top_p": 0.5, "stream": False,
              "frequency_penalty": 0, "presence_penalty": 0, "stop": None}

  for attempt in range(max_retries): # Generating response, trying to clean up response, if clean up fails it tries again until max_retries is reached
      try:
          output = generate_response(prompt, gpt_param)
          output = __chat_func_clean_up(output, prompt=prompt)
          break
      except Exception as e:
          if attempt < max_retries - 1:  # i.e. if not the last attempt
              logging.warning(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
              continue
          else:
              logging.error(f"Attempt {attempt + 1} failed with error: {e}. Using failsafe: {fail_safe}.")
              output = fail_safe
              break
          
  print (output)
  
  return output, [output, prompt, gpt_param, prompt_input, fail_safe]