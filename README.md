# OSGA (Open-Source Generative Agents)

Open-Source Generative Agents (OSGA) is a community-driven fork of 'Generative Agents.' Our mission is to:

- Enable compatibility with open-source Large Language Models.
- Enhance performance and adaptability.
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

\```python
# Update this line with your HTTP call
base_api_url = "your_http_call_here"
\```

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
