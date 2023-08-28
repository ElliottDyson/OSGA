# Copy and paste your OpenAI API Key
openai_api_key = "something"
"""ngrok for public IP addresses of externally hosted notebook instances - localhost:8000 for locally hosted instances"""
base_api_url = "http://e3c2-35-203-140-86.ngrok-free.app/v1"   #   "https://YOUR_NEW_API_ENDPOINT/v1" must end in /v1 due to the nature of llama-cpp-python

model_name = "model"

maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose 
debug = True