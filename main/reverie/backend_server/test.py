"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: gpt_structure.py
Description: Wrapper functions for calling OpenAI APIs.
"""
import json
import random
import time

from utils import *
# openai.api_base = base_api_url
from openai import OpenAI
client = OpenAI(base_url=base_api_url,)


def ChatGPT_request(prompt):
    """
    Given a prompt and a dictionary of GPT parameters, make a request to OpenAI
    server and returns the response. 
    ARGS:
      prompt: a str prompt
      gpt_parameter: a python dictionary with the keys indicating the names of  
                     the parameter and the values indicating the parameter 
                     values.   
    RETURNS: 
      a str of GPT-3's response. 
    """
    # temp_sleep()
    response = client.completions.create(
        model="gpt-3.5-turbo-1106",
        prompt=prompt,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response, response.choices[0].text)


prompt = """
Context for the task:

PART 1.
Here is Here is a brief description of Klaus Mueller.
Name: Klaus Mueller
Age: 20
Innate traits: kind, inquisitive, passionate
Learned traits: Klaus Mueller is a student at Oak Hill College studying sociology. He is passionate about social justice and loves to explore different perspectives.
Currently: Klaus Mueller is writing a research paper on the effects of gentrification in low-income communities.
Lifestyle: Klaus Mueller goes to bed around 11pm, awakes up around 7am, eats dinner around 5pm.
Daily plan requirement: Klaus Mueller goes to the library at Oak Hill College early in the morning, spends his days writing, and eats at Hobbs Cafe.
Current Date: Sunday August 27


Here is the memory that is in Klaus Mueller's head:
- This is Klaus Mueller's plan for Sunday August 27: wake up and complete the morning routine at 7:00 am, go to the library at Oak Hill College around 8:00 am, , have lunch at Hobbs Cafe at 12:00 pm, continue writing his research paper until 6:00 pm, take a break from 6:00 to 7:00 pm.
- Maria Lopez is getting a drink of water
- kitchen sink is being used for washing dishes
- toaster is plugged in and ready for use
- Klaus Mueller is cleaning up the kitchen
- Klaus Mueller is preparing his breakfast
- Klaus Mueller is taking a shower
- kitchen sink is running with water
- toaster is heating bread for breakfast
- bed is being slept on
- Klaus Mueller is brushing his teeth
- closet is being used for storage of clothes
- Klaus Mueller is getting dressed
- refrigerator is being used to store food
- Klaus Mueller is eating breakfast
- Maria Lopez is getting a drink of water
- kitchen sink is being used for washing dishes
- Klaus Mueller is taking a shower
- Klaus Mueller is preparing his breakfast
- Klaus Mueller is cleaning up the kitchen
- This is Klaus Mueller's plan for Sunday August 27: wake up and complete the morning routine at 7:00 am, go to the library at Oak Hill College around 8:00 am, , have lunch at Hobbs Cafe at 12:00 pm, continue writing his research paper until 6:00 pm, take a break from 6:00 to 7:00 pm.
- toaster is plugged in and ready for use
- toaster is heating bread for breakfast
- kitchen sink is running with water
- Klaus Mueller is brushing his teeth
- Klaus Mueller is getting dressed
- bed is being slept on
- Klaus Mueller is eating breakfast
- closet is being used for storage of clothes
- refrigerator is being used to store food


PART 2.
Past Context:


Current Location: kitchen in Dorm for Oak Hill College

Current Context:
Klaus Mueller was eating breakfast at home (setting the table) when Klaus Mueller saw Maria Lopez in the middle of waking up and getting ready for the day. She brushes her teeth, washes her face, puts on some clothes, and gets a drink of water before starting her day (getting a drink of water).
Klaus Mueller is initiating a conversation with Maria Lopez.

Klaus Mueller and Maria Lopez are chatting. Here is their conversation so far:
[This feels awkward, they're just staring at each other, start talking!]

---
Task: Given the above, what should Klaus Mueller say to Maria Lopez next in the conversation? And did it end the conversation?

Output format: Output a json of the following format:
{
"Klaus Mueller": "<Klaus Mueller's utterance>",
"Did the conversation end with Klaus Mueller's utterance?": "<json Boolean>"
}
"""

print(ChatGPT_request(prompt))
