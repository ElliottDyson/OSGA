# OSGA (Open-Source Generative Agents)

Welcome to Open-Source Generative Agents (OSGA), a community-driven initiative that builds upon the foundation of 'Generative Agents'. Our ethos revolves around the following pillars:

- **Compatibility**: Ensuring seamless integration with open-source Large Language Models.
- **Innovation**: Continuously enhancing performance, methodologies, and adaptability.
- **Expansion**: Rolling out novel, optional features to enrich user experience.
- **Centralisation**: Offering a consolidated repository for all OSGA-associated endeavours.

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

- **Compatibility**: The system has been rigorously tested on Python 3.11. However, if you're using an older version, do ensure backward compatibility.

## Configuration

To start, you need to configure `utils.py` inside the `reverie` directory:

```python
base_api_url = "your_http_call_here"  # Replace with your specific HTTP call
# For instance:
base_api_url = "http://localhost:8000/v1"  # If the model resides on the same system initiating the communication.
```

## Usage Guide

1. **Setup**: Execute the `install requirements.bat` file. This will handle all necessary Python dependencies.
2. **Launching**: Activate the servers (both frontend and backend) by running `start.bat`.
3. **Simulation Selection**: When prompted, input the name of a pre-existing simulation (corresponding to a folder name) located at `OSGA\main\environment\frontend_server\storage`. This becomes the genesis point for your simulation.
4. **Fork Naming**: Specify a unique name for your fork. This name will represent your simulation in the storage directory.
5. **Simulation Duration**: To dictate the duration of your simulation, use commands like `run 6000`. Here, the integer represents steps, where 1 in-game hour equates to 360 steps.
6. **Continuation**: If you wish to extend a paused simulation, initiate a new fork from your previous state. This requires terminating the prior frontend and backend processes and then launching fresh ones.

**Important Notes**:
- Upon executing, grant the frontend sufficient time to load. Initial actions by the personas might cause minor delays.
- Refrain from refreshing the frontend page as it could potentially halt the backend simulation. The root cause of this issue is under investigation.
- Navigate the simulator GUI using your keyboard's arrow keys.
- **Access Points**:
  - Simulator Home: [http://127.0.0.1:8000/simulator_home](http://127.0.0.1:8000/simulator_home)
  - Past Simulations (ensure frontend is active): [http://localhost:8000/replay/simulation-name/starting-time-step](http://localhost:8000/replay/simulation-name/starting-time-step)

Facing issues? Raise them on our GitHub, ensuring you tag them appropriately. We endeavour to address them promptly. Please bear with us during peak times as our response rate might be slightly delayed.

## Engage with our Community

We believe in the power of collaboration. Engage in vibrant discussions, share ideas, and explore potential partnerships on our [Discord platform](https://discord.gg/GefGyX4qT6).

## Contribute to OSGA

Your insights are invaluable. Here's why you should consider contributing:

- **Collective Growth**: Hosting projects within our ecosystem fosters shared learning and collective enhancement.
- **Knowledge Hub**: Our vision is to establish a nexus of derivative projects, propelling innovation in generative agent systems.

If our mission resonates with you, and you're keen to contribute or host your project, please connect with us on Discord, sharing your GitHub username. Post a review, we'll onboard you as a contributor and showcase your work on a test branch, ensuring it aligns with our standards.

## Potential Applications

Embarking on a project and seeking inspiration? Here are some avenues to explore:

- **Benchmarking Large Language Models (LLMs)**
  - **Character Representation**: Gauge the proficiency of LLMs in crafting character portrayals based on detailed character sheets.
  - **Social Dynamics**: Analyse the prowess of LLMs in orchestrating authentic and profound social dialogues.
  - **World Engagement**: Investigate the logical reasoning abilities of LLMs when they interface with diverse world constituents.

- **Role-Playing Games (RPGs)**
  - **Bespoke Engines**: Integrate generative agents within proprietary game engines, infusing characters with dynamism and reactivity.
  - **Popular Engines**: Craft plugins for renowned game engines, integrating the capabilities of generative agents.

- **The Horizon is Limitless**: Our platform is a canvas, and we eagerly anticipate the masterpieces you'll conceive.

Authored By: Elliott Dyson
