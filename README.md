# OSGA (Open-Source Generative Agents)

Open-Source Generative Agents (OSGA) is a community-driven derivative of 'Generative Agents.' Our mission is to:

- Enable compatibility with open-source Large Language Models.
- Enhance performance, methods, and adaptability.
- Introduce new, optional features.
- Provide a centralised repository for OSGA-related projects.

## Citation

If you're leveraging this code or data, please cite the original paper:
```
@inproceedings{Park2023GenerativeAgents,
author = {Park, Joon Sung and O'Brien, Joseph C. and Cai, Carrie J. and Morris, Meredith Ringel and Liang, Percy and Bernstein, Michael S.},
title = {Generative Agents: Interactive Simulacra of Human Behavior},
year = {2023},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
booktitle = {In the 36th Annual ACM Symposium on User Interface Software and Technology (UIST '23)},
keywords = {Human-AI interaction, agents, generative AI, large language models},
location = {San Francisco, CA, USA},
series = {UIST '23}
}
```

## Environment

Tested on Python 3.11. (Note: Please check for backward compatibility.)

## Configuration

Update `utils.py` within reverie with the appropriate HTTP call. For example:

Update this line with your HTTP call:
base_api_url = "your_http_call_here"
e.g.
base_api_url = HTTP://localhost:8000/v1 #For hosting the model on the same system that is communicating with the model.

## How to use

Run the "install requirements.bat" file to install the required Python dependencies for running the server.


Run "start.bat" to start the servers up (frontend and backend). 

  When it asks for you to enter the name of a forked simulation to continue from, enter the name of one of the simulations (name of one of the folders) from OSGA\main\environment\frontend_server\storage. 
  This will give you a starting point to run your simulation.

  Follow this up with whatever you want your fork to be called (and saved as in the storage directory)

  You can then use run 6000 (or any other integer, multiply this value by 10 and you get the number of in-game seconds that the simulation is running for). For instance, 1hr in game = 360 steps
  
  If it pauses and you want to run it further, you can simply continue the simulation with a new fork of your old version (by closing the old frontend and backend, then loading new ones).


Be patient! It might take a while until the front_end loads up properly, this is because the first actions have to be completed by the personas first!


Access the current frontend in your browser here: http://127.0.0.1:8000/simulator_home
Access previous simulations in your browser here (frontend still needs to be running): http://localhost:8000/replay/<simulation-name>/<starting-time-step>


Have you had any issues? Post them here on GitHub with the appropriate 'tag'. We'll try and get around to fixing them as quickly as we can! (This may not be particularly quick until we have more people helping us)

## Community

Join our community to discuss projects, ideas, and collaboration: [Discord Link](https://discord.gg/GefGyX4qT6)

## Contribution

We encourage contributions that can help expand the capabilities of generative agents. To foster a collaborative environment, we also invite you to host your OSGA-related projects right here on our GitHub repository.
If you're interested in contributing or hosting your project, reach out on our Discord server with your GitHub username. We'll add you as a contributor and host your work on a test branch until everyone is satisfied with its stability.

### Why Contribute?

- **Collaborative Enhancement**: Hosting your project here allows everyone to learn from and improve upon each other's work.
- **Centralised Knowledge**: We aim to create a hub of derivative projects to accelerate innovation in generative agent systems.

## Ideas of Possible Usage

Here are some potential applications to get you started:

- **Benchmarking of Large Language Models (LLMs)**
  - **Character Representation**: Test how well LLMs can portray characters based on written character sheets.
  - **Socialising**: Evaluate the LLM's ability to engage in realistic and meaningful social interactions.
  - **World Interaction**: Assess logical decision-making by LLMs when interacting with various world elements.

- **Role-Playing Games (RPGs)**
  - **Custom Engines**: Integrate generative agents into your own game engine to create more dynamic and responsive characters.
  - **Existing Engines**: Develop extensions for popular game engines to include generative agents.

- **And More!**: The possibilities are endless. We're excited to see what you'll bring to this collaborative platform.
