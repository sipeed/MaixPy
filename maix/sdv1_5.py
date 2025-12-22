from maix import sys
if sys.device_id().lower() != "maixcam2":
    raise ValueError("Only maixcam2 platform support this module")

from typing import List, Optional, Tuple, Union
import os
import time

import warnings
import numpy as np
import onnxruntime
import torch
from PIL import Image
from transformers import CLIPTokenizer, PreTrainedTokenizer
from diffusers.models.autoencoders.vae import DiagonalGaussianDistribution
from diffusers.models.modeling_outputs import AutoencoderKLOutput
from diffusers.utils import load_image, make_image_grid
from diffusers.utils.torch_utils import randn_tensor

############ Img2Img
PipelineImageInput = Union[
    Image.Image,
    np.ndarray,
    torch.Tensor,
    List[Image.Image],
    List[np.ndarray],
    List[torch.Tensor],
]

PipelineDepthInput = PipelineImageInput

TIME_EMBED_KEY = "/down_blocks.0/resnets.0/act_1/Mul_output_0"
TXT2IMG_TIMESTEPS = np.array([999, 759, 499, 259], dtype=np.int64)
IMG2IMG_TIMESTEPS = np.array([499, 259], dtype=np.int64)
IMG2IMG_SELF_TIMESTEPS = np.array([999, 759, 499, 259], dtype=np.int64)
IMG2IMG_STEP_INDEX = [2, 3]

# Copied from diffusers.schedulers.scheduling_ddpm.DDPMScheduler.add_noise
def add_noise(
    original_samples: torch.Tensor,
    noise: torch.Tensor,
    timesteps: torch.IntTensor,
) -> torch.Tensor:
    # Make sure alphas_cumprod and timestep have same device and dtype as original_samples
    # Move the self.alphas_cumprod to device to avoid redundant CPU to GPU data movement
    # for the subsequent add_noise calls
    # self.alphas_cumprod = self.alphas_cumprod.to(device=original_samples.device)
    # Convert betas to alphas_bar_sqrt
    beta_start = 0.00085
    beta_end = 0.012
    num_train_timesteps = 1000
    betas = torch.linspace(beta_start**0.5, beta_end**0.5, num_train_timesteps, dtype=torch.float32) ** 2
    alphas = 1.0 - betas
    alphas_cumprod = torch.cumprod(alphas, dim=0)
    alphas_cumprod = alphas_cumprod.to(device=original_samples.device)
    alphas_cumprod = alphas_cumprod.to(dtype=original_samples.dtype)
    timesteps = timesteps.to(original_samples.device)

    sqrt_alpha_prod = alphas_cumprod[timesteps] ** 0.5
    sqrt_alpha_prod = sqrt_alpha_prod.flatten()
    while len(sqrt_alpha_prod.shape) < len(original_samples.shape):
        sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)

    sqrt_one_minus_alpha_prod = (1 - alphas_cumprod[timesteps]) ** 0.5
    sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.flatten()
    while len(sqrt_one_minus_alpha_prod.shape) < len(original_samples.shape):
        sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)

    noisy_samples = sqrt_alpha_prod * original_samples + sqrt_one_minus_alpha_prod * noise
    return noisy_samples

def retrieve_latents(
    encoder_output: torch.Tensor, generator: Optional[torch.Generator] = None, sample_mode: str = "sample"
):
    if hasattr(encoder_output, "latent_dist") and sample_mode == "sample":
        return encoder_output.latent_dist.sample(generator)
    elif hasattr(encoder_output, "latent_dist") and sample_mode == "argmax":
        return encoder_output.latent_dist.mode()
    elif hasattr(encoder_output, "latents"):
        return encoder_output.latents
    else:
        raise AttributeError("Could not access latents of provided encoder_output")

def numpy_to_pt(images: np.ndarray) -> torch.Tensor:
    r"""
    Convert a NumPy image to a PyTorch tensor.

    Args:
        images (`np.ndarray`):
            The NumPy image array to convert to PyTorch format.

    Returns:
        `torch.Tensor`:
            A PyTorch tensor representation of the images.
    """
    if images.ndim == 3:
        images = images[..., None]

    images = torch.from_numpy(images.transpose(0, 3, 1, 2))
    return images

def pil_to_numpy(images: Union[List[Image.Image], Image.Image]) -> np.ndarray:
    r"""
    Convert a PIL image or a list of PIL images to NumPy arrays.

    Args:
        images (`PIL.Image.Image` or `List[PIL.Image.Image]`):
            The PIL image or list of images to convert to NumPy format.

    Returns:
        `np.ndarray`:
            A NumPy array representation of the images.
    """
    if not isinstance(images, list):
        images = [images]
    images = [np.array(image).astype(np.float32) / 255.0 for image in images]
    images = np.stack(images, axis=0)

    return images

def is_valid_image(image) -> bool:
    r"""
    Checks if the input is a valid image.

    A valid image can be:
    - A `PIL.Image.Image`.
    - A 2D or 3D `np.ndarray` or `torch.Tensor` (grayscale or color image).

    Args:
        image (`Union[PIL.Image.Image, np.ndarray, torch.Tensor]`):
            The image to validate. It can be a PIL image, a NumPy array, or a torch tensor.

    Returns:
        `bool`:
            `True` if the input is a valid image, `False` otherwise.
    """
    return isinstance(image, Image.Image) or isinstance(image, (np.ndarray, torch.Tensor)) and image.ndim in (2, 3)

def is_valid_image_imagelist(images):
    r"""
    Checks if the input is a valid image or list of images.

    The input can be one of the following formats:
    - A 4D tensor or numpy array (batch of images).
    - A valid single image: `PIL.Image.Image`, 2D `np.ndarray` or `torch.Tensor` (grayscale image), 3D `np.ndarray` or
      `torch.Tensor`.
    - A list of valid images.

    Args:
        images (`Union[np.ndarray, torch.Tensor, PIL.Image.Image, List]`):
            The image(s) to check. Can be a batch of images (4D tensor/array), a single image, or a list of valid
            images.

    Returns:
        `bool`:
            `True` if the input is valid, `False` otherwise.
    """
    if isinstance(images, (np.ndarray, torch.Tensor)) and images.ndim == 4:
        return True
    elif is_valid_image(images):
        return True
    elif isinstance(images, list):
        return all(is_valid_image(image) for image in images)
    return False


def normalize(images: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
    r"""
    Normalize an image array to [-1,1].

    Args:
        images (`np.ndarray` or `torch.Tensor`):
            The image array to normalize.

    Returns:
        `np.ndarray` or `torch.Tensor`:
            The normalized image array.
    """
    return 2.0 * images - 1.0

# Copy from: /home/baiyongqiang/miniforge-pypy3/envs/hf/lib/python3.9/site-packages/diffusers/image_processor.py#607
def preprocess(
    image: PipelineImageInput,
    height: Optional[int] = None,
    width: Optional[int] = None,
    resize_mode: str = "default",  # "default", "fill", "crop"
    crops_coords: Optional[Tuple[int, int, int, int]] = None,
) -> torch.Tensor:
    """
    Preprocess the image input.

    Args:
        image (`PipelineImageInput`):
            The image input, accepted formats are PIL images, NumPy arrays, PyTorch tensors; Also accept list of
            supported formats.
        height (`int`, *optional*):
            The height in preprocessed image. If `None`, will use the `get_default_height_width()` to get default
            height.
        width (`int`, *optional*):
            The width in preprocessed. If `None`, will use get_default_height_width()` to get the default width.
        resize_mode (`str`, *optional*, defaults to `default`):
            The resize mode, can be one of `default` or `fill`. If `default`, will resize the image to fit within
            the specified width and height, and it may not maintaining the original aspect ratio. If `fill`, will
            resize the image to fit within the specified width and height, maintaining the aspect ratio, and then
            center the image within the dimensions, filling empty with data from image. If `crop`, will resize the
            image to fit within the specified width and height, maintaining the aspect ratio, and then center the
            image within the dimensions, cropping the excess. Note that resize_mode `fill` and `crop` are only
            supported for PIL image input.
        crops_coords (`List[Tuple[int, int, int, int]]`, *optional*, defaults to `None`):
            The crop coordinates for each image in the batch. If `None`, will not crop the image.

    Returns:
        `torch.Tensor`:
            The preprocessed image.
    """
    supported_formats = (Image.Image, np.ndarray, torch.Tensor)

    # # Expand the missing dimension for 3-dimensional pytorch tensor or numpy array that represents grayscale image
    # if self.config.do_convert_grayscale and isinstance(image, (torch.Tensor, np.ndarray)) and image.ndim == 3:
    #     if isinstance(image, torch.Tensor):
    #         # if image is a pytorch tensor could have 2 possible shapes:
    #         #    1. batch x height x width: we should insert the channel dimension at position 1
    #         #    2. channel x height x width: we should insert batch dimension at position 0,
    #         #       however, since both channel and batch dimension has same size 1, it is same to insert at position 1
    #         #    for simplicity, we insert a dimension of size 1 at position 1 for both cases
    #         image = image.unsqueeze(1)
    #     else:
    #         # if it is a numpy array, it could have 2 possible shapes:
    #         #   1. batch x height x width: insert channel dimension on last position
    #         #   2. height x width x channel: insert batch dimension on first position
    #         if image.shape[-1] == 1:
    #             image = np.expand_dims(image, axis=0)
    #         else:
    #             image = np.expand_dims(image, axis=-1)

    if isinstance(image, list) and isinstance(image[0], np.ndarray) and image[0].ndim == 4:
        warnings.warn(
            "Passing `image` as a list of 4d np.ndarray is deprecated."
            "Please concatenate the list along the batch dimension and pass it as a single 4d np.ndarray",
            FutureWarning,
        )
        image = np.concatenate(image, axis=0)
    if isinstance(image, list) and isinstance(image[0], torch.Tensor) and image[0].ndim == 4:
        warnings.warn(
            "Passing `image` as a list of 4d torch.Tensor is deprecated."
            "Please concatenate the list along the batch dimension and pass it as a single 4d torch.Tensor",
            FutureWarning,
        )
        image = torch.cat(image, axis=0)

    if not is_valid_image_imagelist(image):
        raise ValueError(
            f"Input is in incorrect format. Currently, we only support {', '.join(str(x) for x in supported_formats)}"
        )
    if not isinstance(image, list):
        image = [image]

    if isinstance(image[0], Image.Image):
        if crops_coords is not None:
            image = [i.crop(crops_coords) for i in image]
        # if self.config.do_resize:
        #     height, width = self.get_default_height_width(image[0], height, width)
        #     image = [self.resize(i, height, width, resize_mode=resize_mode) for i in image]
        # if self.config.do_convert_rgb:
        #     image = [self.convert_to_rgb(i) for i in image]
        # elif self.config.do_convert_grayscale:
        #     image = [self.convert_to_grayscale(i) for i in image]
        image = pil_to_numpy(image)  # to np
        image = numpy_to_pt(image)  # to pt

    elif isinstance(image[0], np.ndarray):
        image = np.concatenate(image, axis=0) if image[0].ndim == 4 else np.stack(image, axis=0)

        # image = self.numpy_to_pt(image)

        # height, width = self.get_default_height_width(image, height, width)
        # if self.config.do_resize:
        #     image = self.resize(image, height, width)

    elif isinstance(image[0], torch.Tensor):
        image = torch.cat(image, axis=0) if image[0].ndim == 4 else torch.stack(image, axis=0)

        # if self.config.do_convert_grayscale and image.ndim == 3:
        #     image = image.unsqueeze(1)

        channel = image.shape[1]
        # don't need any preprocess if the image is latents
        # if channel == self.config.vae_latent_channels:
        #     return image

        # height, width = self.get_default_height_width(image, height, width)
        # if self.config.do_resize:
        #     image = self.resize(image, height, width)

    # expected range [0,1], normalize to [-1,1]
    do_normalize = True # self.config.do_normalize
    if do_normalize and image.min() < 0:
        warnings.warn(
            "Passing `image` as torch tensor with value range in [-1,1] is deprecated. The expected value range for image tensor is [0,1] "
            f"when passing as pytorch tensor or numpy Array. You passed `image` with value range [{image.min()},{image.max()}]",
            FutureWarning,
        )
        do_normalize = False
    if do_normalize:
        image = normalize(image)

    # if self.config.do_binarize:
    #     image = self.binarize(image)

    return image
##########


def maybe_convert_prompt(prompt: Union[str, List[str]], tokenizer: "PreTrainedTokenizer"):  # noqa: F821
    if not isinstance(prompt, List):
        prompts = [prompt]
    else:
        prompts = prompt

    prompts = [_maybe_convert_prompt(p, tokenizer) for p in prompts]

    if not isinstance(prompt, List):
        return prompts[0]

    return prompts


def _maybe_convert_prompt(prompt: str, tokenizer: "PreTrainedTokenizer"):  # noqa: F821
    tokens = tokenizer.tokenize(prompt)
    unique_tokens = set(tokens)
    for token in unique_tokens:
        if token in tokenizer.added_tokens_encoder:
            replacement = token
            i = 1
            while f"{token}_{i}" in tokenizer.added_tokens_encoder:
                replacement += f" {token}_{i}"
                i += 1

            prompt = prompt.replace(token, replacement)

    return prompt


def create_session(model_path: str, backend: str):
    if backend == "onnx":
        return onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    return axengine.InferenceSession(model_path)


def ensure_multiple_of_eight(size: int) -> int:
    if size % 8 != 0:
        raise ValueError("Image size must be a multiple of 8")
    return size


def compute_latent_shape(size: int, batch_size: int = 1) -> Tuple[int, int, int, int]:
    size = ensure_multiple_of_eight(size)
    return batch_size, 4, size // 8, size // 8


def prepare_init_image(image_path: str, size: int) -> Tuple[Image.Image, np.ndarray]:
    def convert(img: Image.Image) -> Image.Image:
        return img.resize((size, size)).convert("RGB")

    image = load_image(image_path, convert_method=convert)
    image_show = image.copy()
    processed = preprocess(image)
    if isinstance(processed, torch.Tensor):
        processed = processed.detach().cpu().numpy()
    return image_show, processed


def ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def resolve_with_base(path: str, base_dir: str) -> str:
    if os.path.isabs(path) and os.path.exists(path):
        return path
    candidate = os.path.join(base_dir, path)
    if os.path.exists(candidate):
        return candidate
    return path


def get_prev_timestep(
    index: int,
    timestep: int,
    timesteps: np.ndarray,
    self_timesteps: Optional[np.ndarray] = None,
    step_index: Optional[List[int]] = None,
) -> int:
    if self_timesteps is not None and step_index is not None:
        prev_idx = step_index[index] + 1
        if prev_idx < len(self_timesteps):
            return int(self_timesteps[prev_idx])
        return int(timestep)
    if index + 1 < len(timesteps):
        return int(timesteps[index + 1])
    return int(timestep)


def denoise_loop(
    latent: np.ndarray,
    prompt_embeds: np.ndarray,
    time_inputs: np.ndarray,
    timesteps: np.ndarray,
    unet_session,
    alphas_cumprod: np.ndarray,
    final_alphas_cumprod: float,
    generator: Optional[torch.Generator],
    noise_dtype: torch.dtype,
    self_timesteps: Optional[np.ndarray] = None,
    step_index: Optional[List[int]] = None,
) -> np.ndarray:
    if time_inputs.shape[0] < len(timesteps):
        raise ValueError("time_input 的步数少于推理步数")

    device = torch.device("cpu")
    for i, timestep in enumerate(timesteps):
        unet_start = time.time()
        latent = latent.astype(np.float32)
        feeds = {
            "sample": latent,
            TIME_EMBED_KEY: np.expand_dims(time_inputs[i], axis=0),
            "encoder_hidden_states": prompt_embeds,
        }
        noise_pred = unet_session.run(None, feeds)[0]
        print(f"unet once take {(1000 * (time.time() - unet_start)):.1f}ms")

        sample = latent
        model_output = noise_pred
        prev_timestep = get_prev_timestep(i, int(timestep), timesteps, self_timesteps, step_index)

        alpha_prod_t = alphas_cumprod[int(timestep)]
        alpha_prod_t_prev = alphas_cumprod[prev_timestep] if prev_timestep >= 0 else final_alphas_cumprod
        beta_prod_t = 1 - alpha_prod_t
        beta_prod_t_prev = 1 - alpha_prod_t_prev

        scaled_timestep = int(timestep) * 10
        c_skip = 0.5 ** 2 / (scaled_timestep ** 2 + 0.5 ** 2)
        c_out = scaled_timestep / (scaled_timestep ** 2 + 0.5 ** 2) ** 0.5
        predicted_original_sample = (sample - (beta_prod_t ** 0.5) * model_output) / (alpha_prod_t ** 0.5)

        denoised = c_out * predicted_original_sample + c_skip * sample
        if i != len(timesteps) - 1:
            if noise_dtype == torch.float32 and generator is None:
                noise = torch.randn(model_output.shape, device=device, dtype=noise_dtype).cpu().numpy()
            else:
                noise_tensor = randn_tensor(model_output.shape, generator=generator, device=device, dtype=noise_dtype)
                noise = noise_tensor.cpu().numpy()
            prev_sample = (alpha_prod_t_prev ** 0.5) * denoised + (beta_prod_t_prev ** 0.5) * noise
        else:
            prev_sample = denoised

        latent = prev_sample.astype(np.float32)

    return latent


def get_embeds(
    prompt: Union[str, List[str]] = "Portrait of a pretty girl",
    tokenizer_dir: str = "./models/tokenizer",
    text_encoder_path: str = "./models/text_encoder/sd15_text_encoder_sim.axmodel",
    backend: str = "axe",
):
    tokenizer = CLIPTokenizer.from_pretrained(tokenizer_dir)

    text_inputs = tokenizer(
        prompt,
        padding="max_length",
        max_length=77,
        truncation=True,
        return_tensors="pt",
    )
    input_ids = text_inputs.input_ids.to("cpu").numpy()
    if backend == "axe":
        input_ids = input_ids.astype(np.int32)

    text_encoder = create_session(text_encoder_path, backend)
    running_start = time.time()
    prompt_embeds_npy = text_encoder.run(None, {"input_ids": input_ids})[0]
    print(f"text encoder running take {(1000 * (time.time() - running_start)):.1f}ms")
    return prompt_embeds_npy


def get_alphas_cumprod():
    betas = torch.linspace(0.00085 ** 0.5, 0.012 ** 0.5, 1000, dtype=torch.float32) ** 2
    alphas = 1.0 - betas
    alphas_cumprod = torch.cumprod(alphas, dim=0).detach().numpy()
    final_alphas_cumprod = alphas_cumprod[0]
    self_timesteps = np.arange(0, 1000)[::-1].copy().astype(np.int64)
    return alphas_cumprod, final_alphas_cumprod, self_timesteps

class SDV1_5:
    def __init__(self, model_dir, backend="axe"):
        if backend != "axe":
            raise ValueError("Only support axmodel, please set backend='axe'")
        self.model_suffix = ".axmodel" if backend == "axe" else ".onnx"
        self.model_dir = model_dir
        if not os.path.exists(model_dir):
            raise ValueError(f"Model dir {model_dir} not exists")
        self.backend = backend
        self.is_inited = False

    def __del__(self):
        if self.is_inited:
            self.deinit()

    def create_session(self, model_path: str, backend: str):
        if backend == "onnx":
            return onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        return self.axengine.InferenceSession(model_path)

    def init(self, txt2img=True, img2img=False, time_input=None):
        if self.is_inited:
            print('Already inited')
            return
        import axengine
        self.axengine = axengine

        backend = self.backend.lower()
        model_dir = self.model_dir
        tokenizer_dir = os.path.join(model_dir, "tokenizer")
        text_encoder_dir = os.path.join(model_dir, "text_encoder")
        model_suffix = ".axmodel" if backend == "axe" else ".onnx"
        text_encoder_path = os.path.join(text_encoder_dir, f"sd15_text_encoder_sim{model_suffix}")
        unet_model = os.path.join(model_dir, f"unet{model_suffix}")
        vae_decoder_model = os.path.join(model_dir, f"vae_decoder{model_suffix}")
        vae_encoder_model = os.path.join(model_dir, f"vae_encoder{model_suffix}")

        if txt2img:
            time_input_default = "time_input_txt2img.npy"
            time_input_path = time_input or os.path.join(self.model_dir, time_input_default)
            if time_input:
                time_input_path = resolve_with_base(time_input, model_dir)
            self.txt2img_time_input = np.load(time_input_path)

        if img2img:
            time_input_default = "time_input_img2img.npy"
            time_input_path = time_input or os.path.join(self.model_dir, time_input_default)
            if time_input:
                time_input_path = resolve_with_base(time_input, model_dir)
            self.img2img_time_input = np.load(time_input_path)

        self.alphas_cumprod, self.final_alphas_cumprod, _ = get_alphas_cumprod()

        self.vae_encoder_session = None
        if img2img:
            self.vae_encoder_session = self.create_session(vae_encoder_model, backend)
        self.unet_session = self.create_session(unet_model, backend)
        self.vae_decoder_session = self.create_session(vae_decoder_model, backend)
        self.tokenizer = CLIPTokenizer.from_pretrained(tokenizer_dir)
        self.text_encoder = self.create_session(text_encoder_path, backend)

        self.img2img = img2img
        self.txt2img = txt2img
        self.is_inited = True

    def deinit(self):
        if not self.is_inited:
            return

        try:
            if self.vae_encoder_session:
                del self.vae_encoder_session
                self.vae_encoder_session = None
            
            if self.unet_session:
                del self.unet_session
                self.unet_session = None

            if self.vae_decoder_session:
                del self.vae_decoder_session
                self.vae_decoder_session = None

            if self.text_encoder:
                del self.text_encoder
                self.text_encoder = None

            if self.axengine:
                del self.axengine
                self.axengine = None
        except:
            print("We encountered some issues when releasing ax_engine, but we ignored them.")

        self.is_inited = False

    def get_embeds(self,
        prompt: Union[str, List[str]] = "Portrait of a pretty girl",
    ):
        text_inputs = self.tokenizer(
            prompt,
            padding="max_length",
            max_length=77,
            truncation=True,
            return_tensors="pt",
        )
        input_ids = text_inputs.input_ids.to("cpu").numpy()
        if self.backend == "axe":
            input_ids = input_ids.astype(np.int32)

        running_start = time.time()
        prompt_embeds_npy = self.text_encoder.run(None, {"input_ids": input_ids})[0]
        print(f"text encoder running take {(1000 * (time.time() - running_start)):.1f}ms")
        return prompt_embeds_npy

    def refer(self, prompt, isize=256, init_image_path=None, seed=None, save_path=None):
        if not self.is_inited:
            raise ValueError('Model is not inited')

        if not self.img2img and init_image_path:
            raise ValueError('You need enable img2img mode, try: init(img2img=True)')
        is_img2img = init_image_path is not None

        if not self.txt2img and not is_img2img:
            raise ValueError('You need enable img2img mode, try: init(txt2img=True)')

        if isize != 256:
            raise ValueError("isize only supports 256")

        device = torch.device("cpu")
        generator: Optional[torch.Generator] = None
        if seed is not None:
            generator = torch.manual_seed(seed)
        noise_dtype = torch.float16 if is_img2img else torch.float32

        prompt_embeds_npy = self.get_embeds(prompt)
        size = ensure_multiple_of_eight(isize)
        if is_img2img:
            init_image_show, init_image_np = prepare_init_image(init_image_path, size)

            vae_start = time.time()
            if self.vae_encoder_session is None:
                raise ValueError("vae encoder is not created.")
            vae_encoder_inp_name = self.vae_encoder_session.get_inputs()[0].name
            vae_encoder_out = self.vae_encoder_session.run(None, {vae_encoder_inp_name: init_image_np})[0]
            print(f"vae encoder inference take {(1000 * (time.time() - vae_start)):.1f}ms")

            posterior = DiagonalGaussianDistribution(torch.from_numpy(vae_encoder_out).to(torch.float32))
            vae_encode_info = AutoencoderKLOutput(latent_dist=posterior)
            if generator is None:
                generator = torch.manual_seed(0)
            init_latents = retrieve_latents(vae_encode_info, generator=generator)
            init_latents = init_latents * 0.18215
            init_latents = torch.cat([init_latents], dim=0)
            noise = randn_tensor(init_latents.shape, generator=generator, device=device, dtype=noise_dtype)
            timestep_tensor = torch.tensor([int(IMG2IMG_TIMESTEPS[0])], device=device)
            init_latents = add_noise(init_latents.to(device), noise, timestep_tensor)
            latent = init_latents.detach().cpu().numpy()

            timesteps = IMG2IMG_TIMESTEPS
            self_timesteps = IMG2IMG_SELF_TIMESTEPS
            step_index = IMG2IMG_STEP_INDEX
        else:
            batch, channels, latent_h, latent_w = compute_latent_shape(size)
            if generator is None:
                latents = torch.randn((batch, channels, latent_h, latent_w), device=device, dtype=torch.float32)
            else:
                latents = randn_tensor((batch, channels, latent_h, latent_w), generator=generator, device=device, dtype=torch.float32)
            latent = latents.cpu().numpy()
            init_image_show = None
            timesteps = TXT2IMG_TIMESTEPS
            self_timesteps = None
            step_index = None

        unet_loop_start = time.time()
        latent = denoise_loop(
            latent=latent,
            prompt_embeds=prompt_embeds_npy,
            time_inputs=self.img2img_time_input if is_img2img else self.txt2img_time_input,
            timesteps=timesteps,
            unet_session=self.unet_session,
            alphas_cumprod=self.alphas_cumprod,
            final_alphas_cumprod=self.final_alphas_cumprod,
            generator=generator,
            noise_dtype=noise_dtype,
            self_timesteps=self_timesteps,
            step_index=step_index,
        )
        print(f"unet loop take {(1000 * (time.time() - unet_loop_start)):.1f}ms")

        vae_start = time.time()
        latent = latent / 0.18215
        vae_decoder_inp_name = self.vae_decoder_session.get_inputs()[0].name
        image = self.vae_decoder_session.run(None, {vae_decoder_inp_name: latent.astype(np.float32)})[0]
        print(f"vae decoder inference take {(1000 * (time.time() - vae_start)):.1f}ms")

        if save_path:
            save_start = time.time()
            image = np.transpose(image, (0, 2, 3, 1)).squeeze(axis=0)
            image_denorm = np.clip(image / 2 + 0.5, 0, 1)
            image_uint8 = (image_denorm * 255).round().astype("uint8")

            pil_image = Image.fromarray(image_uint8[:, :, :3])
            ensure_parent(save_path)
            pil_image.save(save_path)

            if is_img2img:
                grid_path = os.path.splitext(save_path)[0] + "_grid.png"
                grid_img = make_image_grid([init_image_show, pil_image], rows=1, cols=2)
                ensure_parent(grid_path)
                grid_img.save(grid_path)
                print(f"grid image saved in {grid_path}")
            print(f"save image take {(1000 * (time.time() - save_start)):.1f}ms")


# model = SDV1_5("/root/models/lcm-lora-sdv1-5-maixcam2/ax620e_models")
# model.init(img2img=True)
# model.refer(prompt="A white dog", save_path="/root/text2img.jpg")
# model.refer(prompt="Replace the dog with a cat.", init_image_path="/root/text2img.jpg", seed=0.5, save_path="/root/img2img.jpg")

# model.deinit()