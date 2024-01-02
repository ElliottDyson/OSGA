conda create -n gptq python=3.10
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install flash-attn --no-build-isolation
pip install transformers==4.36 bitsandbytes==0.41.3 accelerate==0.25.0 scipy==1.11.4 sentencepiece==0.1.99 gradio==4.9.0
