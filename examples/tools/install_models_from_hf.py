# This scripy is used to install models from huggingface
# Only support MaixCAM2 platform

import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com' # or 'https://huggingface.co'

from huggingface_hub import snapshot_download
from huggingface_hub.utils import tqdm

CAPTURE_PROGRESS=False
class Tqdm(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if CAPTURE_PROGRESS:
            print(f"[INIT] {self.desc} | {self.n}/{self.total} ({self.n/self.total*100:.2f}%)")
        else:
            print('')
            
    def update(self, n=1):
        super().update(n)
        if CAPTURE_PROGRESS:
            print(f"[UPDATE] {self.desc} | {self.n}/{self.total} ({self.n/self.total*100:.2f}%)")
        else:
            print('')
    
    def close(self):
        super().close()
        if CAPTURE_PROGRESS:
            print(f"[CLOSE] {self.desc} | {self.n}/{self.total} ({self.n/self.total*100:.2f}%)")
        else:
            print('')

model_name = 'lcm-lora-sdv1-5-maixcam2'
repo_id = f'sipeed/{model_name}'
local_dir = f'/root/models/{model_name}'
snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    # allow_patterns="*.py",
    tqdm_class=Tqdm,
)
