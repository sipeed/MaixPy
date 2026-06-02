---
title: MaixCAM MaixPy 开发源代码指南
---
## 准备源码
### 获取 MaixCDK 源码

MaixPy 项目依赖于 MaixCDK，需要先克隆它，放到电脑的某个目录（勿放在 MaixPy 目录下）

```shell
mkdir -p ~/maix
cd ~/maix
git clone https://github.com/sipeed/MaixCDK
```

然后需要设置环境变量 `MAIXCDK_PATH` 指定 MaixCDK 的路径，可以在 `~/.bashrc` 或者`~/.zshrc`（根据你使用的shell决定）添加：

```shell
export MAIXCDK_PATH=~/maix/MaixCDK
```

只有在成功设置环境变量后， MaixPy 才能找到 MaixCDK 源码。

### 获取 MaixPy 源代码

```shell
cd ~/maix
git clone https://github.com/sipeed/MaixPy
```

## 准备环境

### 准备本地环境

#### maixcam和maixcam2需要的依赖
- 编译wheel所需要的包如下
```
PyYAML       
tqdm         
progress     
requests     
cmake==3.15.3
maixtool     
```

#### 安装conda（miniconda/anaconda）
maixcam需要python3.11, maixcam2需要python3.13
- 首先使用`conda create -n maixcam2 python=3.13 -y`创造环境
- 然后请`conda run -n maixcam2 pip install -r /tmp/requirements.txt`安装依赖,新建一个txt文件/tmp/requirements.txt放上面的依赖库
- 同理maixcam使用`conda create -n maixcam python=3.13 -y`创造环境
- 然后请`conda run -n maixcam pip install -r /tmp/requirements.txt`安装依赖


### 准备docker环境（推荐）


```Dockerfile
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND noninteractive

EXPOSE 8888

EXPOSE 2333

RUN dpkg --add-architecture i386 \
    && apt-get -o APT::Retries=3 update -y

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa\
    # 安装编译工具、系统工具、Python、OpenCV、SDL 等依赖。
    # Install build tools, system tools, Python, OpenCV, SDL, and other dependencies.
    && apt-get install build-essential vim \
        git libncurses5-dev zlib1g-dev gawk \
        libfuse2 libssl-dev unzip lib32z1 lib32z1-dev lib32stdc++6 libstdc++6 \
        ca-certificates file g++-multilib libc6:i386 locales autoconf automake libtool mtools \
        android-sdk-libsparse-utils zip libpcre3-dev \
        python3 python3-pip rsync shellcheck \
        libopencv-dev libopencv-contrib-dev \
        libsdl2-dev wget sudo -y \
        # 下载 Miniconda 安装脚本。
        # Download the Miniconda installer script.
        && wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
        && bash miniconda.sh -b -p /opt/miniconda \
        && rm miniconda.sh \
        && /opt/miniconda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
        && /opt/miniconda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
        && apt-get purge -yq software-properties-common \
        && apt-get autoremove -yq --purge \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* \
        && rm -rf /tmp/* 

# 创建 teedoc 插件依赖文件 和 maixtool工具链。
# Create the teedoc requirements and maixtool toolchain
RUN echo 'PyYAML       ' > /tmp/requirements.txt && \
    echo 'tqdm         ' >> /tmp/requirements.txt && \
    echo 'progress     ' >> /tmp/requirements.txt && \
    echo 'requests     ' >> /tmp/requirements.txt && \
    echo 'cmake==3.15.3' >> /tmp/requirements.txt && \
    echo 'maixtool     ' >> /tmp/requirements.txt && \
    echo 'pybind11-stubgen' >> /tmp/requirements.txt && \
    echo 'teedoc-plugin-ad-hint                 ' > /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-assets                  ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-baidu-tongji            ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-blog                    ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-comments-gitalk         ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-google-analytics        ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-google-translate        ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-jupyter-notebook-parser ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-markdown-parser         ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-search                  ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-theme-default           ' >> /tmp/teedoc_requirements.txt && \
    echo 'teedoc-plugin-thumbs-up               ' >> /tmp/teedoc_requirements.txt 

# 将 Miniconda 的 bin 目录加入 PATH 环境变量。
# Add Miniconda's bin directory to the PATH environment variable.
ENV PATH="/opt/miniconda/bin:$PATH"

RUN conda init bash \
    && conda init zsh

# 创建名为 maixcam2 的 conda 环境，并安装 Python 3.13。
# Create a conda environment named maixcam2 with Python 3.13.
RUN conda create -n maixcam2 python=3.13 -y

# 在 maixcam2 环境中安装 requirements.txt 里的依赖。
# Install dependencies from requirements.txt into the maixcam2 environment.
RUN conda run -n maixcam2 pip install -r /tmp/requirements.txt && \
    conda run -n maixcam2 pip install -r /tmp/teedoc_requirements.txt

# 创建名为 maixcam 的 conda 环境，并安装 Python 3.11。
# Create a conda environment named maixcam with Python 3.11.
RUN conda create -n maixcam python=3.11 -y

# 在 maixcam 环境中安装 requirements.txt 里的依赖。
# Install dependencies from requirements.txt into the maixcam environment.
RUN conda run -n maixcam pip install -r /tmp/requirements.txt && \
    conda run -n maixcam pip install -r /tmp/teedoc_requirements.txt

# 在 bash 启动时自动激活 maixcam2 环境。
# Automatically activate the maixcam2 environment when bash starts.
RUN echo "conda activate maixcam2" >> ~/.bashrc

# 设置默认工作目录为 /maix。
# Set the default working directory to /maix.
WORKDIR /maix

```
使用`docker build --network=host -t maixcdk-builder . ` 编译maixcdk编译环境。

```bash
cd ~/maix

docker run -it \
--network=host --hostname maixcdk-env \
-p 9002:2333 --rm --env MAIXCDK_PATH=/maix/MaixCDK  \
-v ./:/maix \
maixcdk-builder:latest
```
> 启动环境后，使用`conda activate maixcam2`激活maixcam2编译环境 和 `conda activate maixcam`激活maixcam编译环境
> 默认启动maixcam2编译环境
> maix里需要存放最新的MaixCDK源码和MaixPy源码

## 构建MaixPy python wheel包

### 构建并打包成 wheel 文件

```shell
cd ~/maix/MaixPy
#需要确保使用conda activate maixcam进入maixcam环境
python setup.py bdist_wheel maixcam
#需要确保使用conda activate maixcam2进入maixcam2环境
python setup.py bdist_wheel maixcam2
```

`maixcam` 可以被替换为其他板卡配置, 请查看 `MaixCDK/platforms` 目录。

构建成功后, 你会在 `dist` 目录中找到 wheel 文件, 传输到设备（开发板），在设备终端中使用 `pip install -U MaixPy****.whl` 在你的设备上安装或升级。

> `python setup.py bdist_wheel maixcam --skip-build` 不会执行构建命令, 只会打包 wheel 文件, 因此你可以先使用 `maixcdk menuconfig` 和 `maixcdk build` 来自定义构建。

> 另外如果你是在调试 API，需要频繁安装，使用 pip 安装会比较慢，可以直接编译后拷贝 `maix` 目录到设备的 `/usr/lib/python3.11/site-packages`目录下覆盖旧的文件即可。


### 手动构建

```shell
maixcdk build
```

### 修改源代码后运行测试

* 首先, 构建源代码
```shell
maixcdk build
```

* 如果为 PC 自身构建(平台 `linux`):
然后执行 `./run.sh your_test_file_name.py` 来运行 Python 脚本。
```shell
cd test
./run.sh examples/hello_maix.py
```

* 如果为板卡交叉编译:
  * 最快的方式是将 `maix` 目录复制到设备的 `/usr/lib/python3.11/site-packages/` 目录, 然后在设备上运行脚本。
  * 或者打包 wheel 文件并在设备上使用 `pip install -U MaixPy****.whl` 安装, 然后在设备上运行脚本。

## 本地预览文档

文档位于 [docs](https://github.com/sipeed/MaixPy/tree/main/docs) 目录, 使用 `Markdown` 格式, 你可以使用 [teedoc](https://github.com/teedoc/teedoc) 来生成网页版本的文档。

API 文档会在构建 MaixPy 固件时生成, **如果你没有构建 MaixPy, API 文档将会是空的**。
在这之前请确保你的依赖是否安装完全
```
teedoc-plugin-ad-hint                 
teedoc-plugin-assets                  
teedoc-plugin-baidu-tongji            
teedoc-plugin-blog                    
teedoc-plugin-comments-gitalk         
teedoc-plugin-google-analytics        
teedoc-plugin-google-translate        
teedoc-plugin-jupyter-notebook-parser 
teedoc-plugin-markdown-parser         
teedoc-plugin-search                  
teedoc-plugin-theme-default           
teedoc-plugin-thumbs-up               
```

```shell
cd ~/maix/MaixPy
teedoc serve
```

然后访问 `http://127.0.0.1:2333` 在网页浏览器中预览文档。

## 对于想要贡献的开发者

请查看 [MaixPy 开发源代码指南](./contribute.md)

如果在使用源代码时遇到任何问题, 请先参考 [FAQ](./faq.md)。
