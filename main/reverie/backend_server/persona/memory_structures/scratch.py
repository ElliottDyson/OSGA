"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: scratch.py
Description: Defines the short-term memory module for generative agents.
"""
import datetime
import json
import sys
sys.path.append('../../')

from global_methods import *

class Scratch: 
  def __init__(self, f_saved): 
    # PERSONA HYPERPARAMETERS
    # <vision_r> denotes the number of tiles that the persona can see around 
    # them. 
    self.vision_r = 4
    # <att_bandwidth> TODO 
    self.att_bandwidth = 3
    # <retention> TODO 
    self.retention = 5

    # WORLD INFORMATION
    # Perceived world time. 
    self.curr_time = None
    # Current x,y tile coordinate of the persona. 
    self.curr_tile = None
    # Perceived world daily requirement. 
    self.daily_plan_req = None
    
    # THE CORE IDENTITY OF THE PERSONA 
    # Base information about the persona.
    self.name = None
    self.first_name = None
    self.last_name = None
    self.age = None
    # L0 permanent core traits.  
    self.innate = None
    # L1 stable traits.
    self.learned = None
    # L2 external implementation. 
    self.currently = None
    self.lifestyle = None
    self.living_area = None

    # REFLECTION VARIABLES
    self.concept_forget = 100
    self.daily_reflection_time = 60 * 3
    self.daily_reflection_size = 5
    self.overlap_reflect_th = 2
    self.kw_strg_event_reflect_th = 4
    self.kw_strg_thought_reflect_th = 4

    # New reflection variables
    self.recency_w = 1
    self.relevance_w = 1
    self.importance_w = 1
    self.recency_decay = 0.99
    self.importance_trigger_max = 150
    self.importance_trigger_curr = self.importance_trigger_max
    self.importance_ele_n = 0 
    self.thought_count = 5

    # PERSONA PLANNING 
    # <daily_req> is a list of various goals the persona is aiming to achieve
    # today. 
    # e.g., ['Work on her paintings for her upcoming show', 
    #        'Take a break to watch some TV', 
    #        'Make lunch for herself', 
    #        'Work on her paintings some more', 
    #        'Go to bed early']
    # They have to be renewed at the end of the day, which is why we are
    # keeping track of when they were first generated. 
    self.daily_req = []
    # <f_daily_schedule> denotes a form of long term planning. This lays out 
    # the persona's daily plan. 
    # Note that we take the long term planning and short term decomposition 
    # appoach, which is to say that we first layout hourly schedules and 
    # gradually decompose as we go. 
    # Three things to note in the example below: 
    # 1) See how "sleeping" was not decomposed -- some of the common events 
    #    really, just mainly sleeping, are hard coded to be not decomposable.
    # 2) Some of the elements are starting to be decomposed... More of the 
    #    things will be decomposed as the day goes on (when they are 
    #    decomposed, they leave behind the original hourly action description
    #    in tact).
    # 3) The latter elements are not decomposed. When an event occurs, the
    #    non-decomposed elements go out the window.  
    # e.g., [['sleeping', 360], 
    #         ['wakes up and ... (wakes up and stretches ...)', 5], 
    #         ['wakes up and starts her morning routine (out of bed )', 10],
    #         ...
    #         ['having lunch', 60], 
    #         ['working on her painting', 180], ...]
    self.f_daily_schedule = []
    # <f_daily_schedule_hourly_org> is a replica of f_daily_schedule
    # initially, but retains the original non-decomposed version of the hourly
    # schedule. 
    # e.g., [['sleeping', 360], 
    #        ['wakes up and starts her morning routine', 120],
    #        ['working on her painting', 240], ... ['going to bed', 60]]
    self.f_daily_schedule_hourly_org = []
    
    # CURR ACTION 
    # <address> is literally the string address of where the action is taking 
    # place.  It comes in the form of 
    # "{world}:{sector}:{arena}:{game_objects}". It is important that you 
    # access this without doing negative indexing (e.g., [-1]) because the 
    # latter address elements may not be present in some cases. 
    # e.g., "dolores double studio:double studio:bedroom 1:bed"
    self.act_address = None
    # <start_time> is a python datetime instance that indicates when the 
    # action has started. 
    self.act_start_time = None
    # <duration> is the integer value that indicates the number of minutes an
    # action is meant to last. 
    self.act_duration = None
    # <description> is a string description of the action. 
    self.act_description = None
    # <pronunciatio> is the descriptive expression of the self.description. 
    # Currently, it is implemented as emojis. 
    self.act_pronunciatio = None
    # <event_form> represents the event triple that the persona is currently 
    # engaged in. 
    self.act_event = (self.name, None, None)

    # <obj_description> is a string description of the object action. 
    self.act_obj_description = None
    # <obj_pronunciatio> is the descriptive expression of the object action. 
    # Currently, it is implemented as emojis. 
    self.act_obj_pronunciatio = None
    # <obj_event_form> represents the event triple that the action object is  
    # currently engaged in. 
    self.act_obj_event = (self.name, None, None)

    # <chatting_with> is the string name of the persona that the current 
    # persona is chatting with. None if it does not exist. 
    self.chatting_with = None
    # <chat> is a list of list that saves a conversation between two personas.
    # It comes in the form of: [["Dolores Murphy", "Hi"], 
    #                           ["Maeve Jenson", "Hi"] ...]
    self.chat = None
    # <chatting_with_buffer>  
    # e.g., ["Dolores Murphy"] = self.vision_r
    self.chatting_with_buffer = dict()
    self.chatting_end_time = None

    # <path_set> is True if we've already calculated the path the persona will
    # take to execute this action. That path is stored in the persona's 
    # scratch.planned_path.
    self.act_path_set = False
    # <planned_path> is a list of x y coordinate tuples (tiles) that describe
    # the path the persona is to take to execute the <curr_action>. 
    # The list does not include the persona's current tile, and includes the 
    # destination tile. 
    # e.g., [(50, 10), (49, 10), (48, 10), ...]
    self.planned_path = []

    if check_if_file_exists(f_saved): 
      # If we have a bootstrap file, load that here. 
      scratch_load = json.load(open(f_saved))

      self.vision_r = scratch_load["vision_r"]
      self.att_bandwidth = scratch_load["att_bandwidth"]
      self.retention = scratch_load["retention"]

      if scratch_load["curr_time"]: 
        self.curr_time = datetime.datetime.strptime(scratch_load["curr_time"],
                                                  "%B %d, %Y, %H:%M:%S")
      else: 
        self.curr_time = None
      self.curr_tile = scratch_load["curr_tile"]
      self.daily_plan_req = scratch_load["daily_plan_req"]

      self.name = scratch_load["name"]
      self.first_name = scratch_load["first_name"]
      self.last_name = scratch_load["last_name"]
      self.age = scratch_load["age"]
      self.innate = scratch_load["innate"]
      self.learned = scratch_load["learned"]
      self.currently = scratch_load["currently"]
      self.lifestyle = scratch_load["lifestyle"]
      self.living_area = scratch_load["living_area"]

      self.concept_forget = scratch_load["concept_forget"]
      self.daily_reflection_time = scratch_load["daily_reflection_time"]
      self.daily_reflection_size = scratch_load["daily_reflection_size"]
      self.overlap_reflect_th = scratch_load["overlap_reflect_th"]
      self.kw_strg_event_reflect_th = scratch_load["kw_strg_event_reflect_th"]
      self.kw_strg_thought_reflect_th = scratch_load["kw_strg_thought_reflect_th"]

      self.recency_w = scratch_load["recency_w"]
      self.relevance_w = scratch_load["relevance_w"]
      self.importance_w = scratch_load["importance_w"]
      self.recency_decay = scratch_load["recency_decay"]
      self.importance_trigger_max = scratch_load["importance_trigger_max"]
      self.importance_trigger_curr = scratch_load["importance_trigger_curr"]
      self.importance_ele_n = scratch_load["importance_ele_n"]
      self.thought_count = scratch_load["thought_count"]

      self.daily_req = scratch_load["daily_req"]
      self.f_daily_schedule = scratch_load["f_daily_schedule"]
      self.f_daily_schedule_hourly_org = scratch_load["f_daily_schedule_hourly_org"]

      self.act_address = scratch_load["act_address"]
      if scratch_load["act_start_time"]: 
        self.act_start_time = datetime.datetime.strptime(
                                              scratch_load["act_start_time"],
                                              "%B %d, %Y, %H:%M:%S")
      else: 
        self.curr_time = None
      self.act_duration = scratch_load["act_duration"]
      self.act_description = scratch_load["act_description"]
      self.act_pronunciatio = scratch_load["act_pronunciatio"]
      self.act_event = tuple(scratch_load["act_event"])

      self.act_obj_description = scratch_load["act_obj_description"]
      self.act_obj_pronunciatio = scratch_load["act_obj_pronunciatio"]
      self.act_obj_event = tuple(scratch_load["act_obj_event"])

      self.chatting_with = scratch_load["chatting_with"]
      self.chat = scratch_load["chat"]
      self.chatting_with_buffer = scratch_load["chatting_with_buffer"]
      if scratch_load["chatting_end_time"]: 
        self.chatting_end_time = datetime.datetime.strptime(
                                            scratch_load["chatting_end_time"],
                                            "%B %d, %Y, %H:%M:%S")
      else:
        self.chatting_end_time = None

      self.act_path_set = scratch_load["act_path_set"]
      self.planned_path = scratch_load["planned_path"]


  def save(self, out_json):
    """
    Save persona's scratch. 

    INPUT: 
      out_json: The file where we wil be saving our persona's state. 
    OUTPUT: 
      None
    """
    scratch = dict() 
    scratch["vision_r"] = self.vision_r
    scratch["att_bandwidth"] = self.att_bandwidth
    scratch["retention"] = self.retention

    scratch["curr_time"] = self.curr_time.strftime("%B %d, %Y, %H:%M:%S")
    scratch["curr_tile"] = self.curr_tile
    scratch["daily_plan_req"] = self.daily_plan_req

    scratch["name"] = self.name
    scratch["first_name"] = self.first_name
    scratch["last_name"] = self.last_name
    scratch["age"] = self.age
    scratch["innate"] = self.innate
    scratch["learned"] = self.learned
    scratch["currently"] = self.currently
    scratch["lifestyle"] = self.lifestyle
    scratch["living_area"] = self.living_area

    scratch["concept_forget"] = self.concept_forget
    scratch["daily_reflection_time"] = self.daily_reflection_time
    scratch["daily_reflection_size"] = self.daily_reflection_size
    scratch["overlap_reflect_th"] = self.overlap_reflect_th
    scratch["kw_strg_event_reflect_th"] = self.kw_strg_event_reflect_th
    scratch["kw_strg_thought_reflect_th"] = self.kw_strg_thought_reflect_th

    scratch["recency_w"] = self.recency_w
    scratch["relevance_w"] = self.relevance_w
    scratch["importance_w"] = self.importance_w
    scratch["recency_decay"] = self.recency_decay
    scratch["importance_trigger_max"] = self.importance_trigger_max
    scratch["importance_trigger_curr"] = self.importance_trigger_curr
    scratch["importance_ele_n"] = self.importance_ele_n
    scratch["thought_count"] = self.thought_count

    scratch["daily_req"] = self.daily_req
    scratch["f_daily_schedule"] = self.f_daily_schedule
    scratch["f_daily_schedule_hourly_org"] = self.f_daily_schedule_hourly_org

    scratch["act_address"] = self.act_address
    scratch["act_start_time"] = (self.act_start_time
                                     .strftime("%B %d, %Y, %H:%M:%S"))
    scratch["act_duration"] = self.act_duration
    scratch["act_description"] = self.act_description
    scratch["act_pronunciatio"] = self.act_pronunciatio
    scratch["act_event"] = self.act_event

    scratch["act_obj_description"] = self.act_obj_description
    scratch["act_obj_pronunciatio"] = self.act_obj_pronunciatio
    scratch["act_obj_event"] = self.act_obj_event

    scratch["chatting_with"] = self.chatting_with
    scratch["chat"] = self.chat
    scratch["chatting_with_buffer"] = self.chatting_with_buffer
    if self.chatting_end_time: 
      scratch["chatting_end_time"] = (self.chatting_end_time
                                        .strftime("%B %d, %Y, %H:%M:%S"))
    else: 
      scratch["chatting_end_time"] = None

    scratch["act_path_set"] = self.act_path_set
    scratch["planned_path"] = self.planned_path

    with open(out_json, "w") as outfile:
      json.dump(scratch, outfile, indent=2) 


  def get_f_daily_schedule_index(self, advance=0):
    """
    We get the current index of self.f_daily_schedule. 

    Recall that self.f_daily_schedule stores the decomposed action sequences 
    up until now, and the hourly sequences of the future action for the rest
    of today. Given that self.f_daily_schedule is a list of list where the 
    inner list is composed of [task, duration], we continue to add up the 
    duration until we reach "if elapsed > today_min_elapsed" condition. The
    index where we stop is the index we will return. 

    INPUT
      advance: Integer value of the number minutes we want to look into the 
               future. This allows us to get the index of a future timeframe.
    OUTPUT 
      an integer value for the current index of f_daily_schedule.
    """
    # We first calculate teh number of minutes elapsed today. 
    today_min_elapsed = 0
    today_min_elapsed += self.curr_time.hour * 60
    today_min_elapsed += self.curr_time.minute
    today_min_elapsed += advance

    x = 0
    for task, duration in self.f_daily_schedule: 
      x += duration
    x = 0
    for task, duration in self.f_daily_schedule_hourly_org: 
      x += duration

    # We then calculate the current index based on that. 
    curr_index = 0
    elapsed = 0
    for task, duration in self.f_daily_schedule: 
      elapsed += duration
      if elapsed > today_min_elapsed: 
        return curr_index
      curr_index += 1

    return curr_index


  def get_f_daily_schedule_hourly_org_index(self, advance=0):
    """
    We get the current index of self.f_daily_schedule_hourly_org. 
    It is otherwise the same as get_f_daily_schedule_index. 

    INPUT
      advance: Integer value of the number minutes we want to look into the 
               future. This allows us to get the index of a future timeframe.
    OUTPUT 
      an integer value for the current index of f_daily_schedule.
    """
    # We first calculate teh number of minutes elapsed today. 
    today_min_elapsed = 0
    today_min_elapsed += self.curr_time.hour * 60
    today_min_elapsed += self.curr_time.minute
    today_min_elapsed += advance
    # We then calculate the current index based on that. 
    curr_index = 0
    elapsed = 0
    for task, duration in self.f_daily_schedule_hourly_org: 
      elapsed += duration
      if elapsed > today_min_elapsed: 
        return curr_index
      curr_index += 1
    return curr_index


  def get_str_iss(self): 
    """
    ISS stands for "identity stable set." This describes the commonset summary
    of this persona -- basically, the bare minimum description of the persona
    that gets used in almost all prompts that need to call on the persona. 

    INPUT
      None
    OUTPUT
      the identity stable set summary of the persona in a string form.
    EXAMPLE STR OUTPUT
      "Name: Dolores Heitmiller
       Age: 28
       Innate traits: hard-edged, independent, loyal
       Learned traits: Dolores is a painter who wants live quietly and paint 
         while enjoying her everyday life.
       Currently: Dolores is preparing for her first solo show. She mostly 
         works from home.
       Lifestyle: Dolores goes to bed around 11pm, sleeps for 7 hours, eats 
         dinner around 6pm.
       Daily plan requirement: Dolores is planning to stay at home all day and 
         never go out."
    """
    commonset = ""
    commonset += f"Name: {self.name}\n"
    commonset += f"Age: {self.age}\n"
    commonset += f"Innate traits: {self.innate}\n"
    commonset += f"Learned traits: {self.learned}\n"
    commonset += f"Currently: {self.currently}\n"
    commonset += f"Lifestyle: {self.lifestyle}\n"
    commonset += f"Daily plan requirement: {self.daily_plan_req}\n"
    commonset += f"Current Date: {self.curr_time.strftime('%A %B %d')}\n"
    return commonset


  def get_str_name(self): 
    return self.name


  def get_str_firstname(self): 
    return self.first_name


  def get_str_lastname(self): 
    return self.last_name


  def get_str_age(self): 
    return str(self.age)


  def get_str_innate(self): 
    return self.innate


  def get_str_learned(self): 
    return self.learned


  def get_str_currently(self): 
    return self.currently


  def get_str_lifestyle(self): 
    return self.lifestyle


  def get_str_daily_plan_req(self): 
    return self.daily_plan_req


  def get_str_curr_date_str(self): 
    return self.curr_time.strftime("%A %B %d")


  def get_curr_event(self):
    if not self.act_address: 
      return (self.name, None, None)
    else: 
      return self.act_event


  def get_curr_event_and_desc(self): 
    if not self.act_address: 
      return (self.name, None, None, None)
    else: 
      return (self.act_event[0], 
              self.act_event[1], 
              self.act_event[2],
              self.act_description)


  def get_curr_obj_event_and_desc(self): 
    if not self.act_address: 
      return ("", None, None, None)
    else: 
      return (self.act_address, 
              self.act_obj_event[1], 
              self.act_obj_event[2],
              self.act_obj_description)


  def add_new_action(self, 
                     action_address, 
                     action_duration,
                     action_description,
                     action_pronunciatio, 
                     action_event,
                     chatting_with, 
                     chat, 
                     chatting_with_buffer,
                     chatting_end_time,
                     act_obj_description, 
                     act_obj_pronunciatio, 
                     act_obj_event, 
                     act_start_time=None): 
    self.act_address = action_address
    self.act_duration = action_duration
    self.act_description = action_description
    self.act_pronunciatio = action_pronunciatio
    self.act_event = action_event

    self.chatting_with = chatting_with
    self.chat = chat 
    if chatting_with_buffer: 
      self.chatting_with_buffer.update(chatting_with_buffer)
    self.chatting_end_time = chatting_end_time

    self.act_obj_description = act_obj_description
    self.act_obj_pronunciatio = act_obj_pronunciatio
    self.act_obj_event = act_obj_event
    
    self.act_start_time = self.curr_time
    
    self.act_path_set = False


  def act_time_str(self): 
    """
    Returns a string output of the current time. 

    INPUT
      None
    OUTPUT 
      A string output of the current time.
    EXAMPLE STR OUTPUT
      "14:05 P.M."
    """
    return self.act_start_time.strftime("%H:%M %p")


  def act_check_finished(self): 
    """
    Checks whether the self.Action instance has finished.  

    INPUT
      curr_datetime: Current time. If current time is later than the action's
                     start time + its duration, then the action has finished. 
    OUTPUT 
      Boolean [True]: Action has finished.
      Boolean [False]: Action has not finished and is still ongoing.
    """
    if not self.act_address: 
      return True
      
    if self.chatting_with: 
      end_time = self.chatting_end_time
    else: 
      x = self.act_start_time
      if x.second != 0: 
        x = x.replace(second=0)
        x = (x + datetime.timedelta(minutes=1))
      end_time = (x + datetime.timedelta(minutes=self.act_duration))

    if end_time.strftime("%H:%M:%S") == self.curr_time.strftime("%H:%M:%S"): 
      return True
    return False


  def act_summarize(self):
    """
    Summarize the current action as a dictionary. 

    INPUT
      None
    OUTPUT 
      ret: A human readable summary of the action.
    """
    exp = dict()
    exp["persona"] = self.name
    exp["address"] = self.act_address
    exp["start_datetime"] = self.act_start_time
    exp["duration"] = self.act_duration
    exp["description"] = self.act_description
    exp["pronunciatio"] = self.act_pronunciatio
    return exp


  def act_summary_str(self):
    """
    Returns a string summary of the current action. Meant to be 
    human-readable.

    INPUT
      None
    OUTPUT 
      ret: A human readable summary of the action.
    """
    start_datetime_str = self.act_start_time.strftime("%A %B %d -- %H:%M %p")
    ret = f"[{start_datetime_str}]\n"
    ret += f"Activity: {self.name} is {self.act_description}\n"
    ret += f"Address: {self.act_address}\n"
    ret += f"Duration in minutes (e.g., x min): {str(self.act_duration)} min\n"
    return ret


  def get_str_daily_schedule_summary(self): 
    ret = ""
    curr_min_sum = 0
    for row in self.f_daily_schedule: 
      curr_min_sum += row[1]
      hour = int(curr_min_sum/60)
      minute = curr_min_sum%60
      ret += f"{hour:02}:{minute:02} || {row[0]}\n"
    return ret


  def get_str_daily_schedule_hourly_org_summary(self): 
    ret = ""
    curr_min_sum = 0
    for row in self.f_daily_schedule_hourly_org: 
      curr_min_sum += row[1]
      hour = int(curr_min_sum/60)
      minute = curr_min_sum%60
      ret += f"{hour:02}:{minute:02} || {row[0]}\n"
    return ret




















