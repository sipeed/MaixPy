let currentPath = '/root';
let showHidden = false;
let currentZoom = 1; // 初始缩放比例
// 支持的文件类型字典
const fileTypes = {
    image: ['jpg', 'jpeg', 'png', 'gif'],
    text: ['txt', 'md', 'py', 'mud', 'json', 'yaml', 'yml', 'conf'],
    video: ['mp4', 'webm', 'ogg', 'avi', 'flv']
};


document.addEventListener("DOMContentLoaded", () => {
    loadDirectory(currentPath);
});

function selectDirectory(path) {
    currentPath = path;
    loadDirectory(currentPath);
}

function showMessage(message) {
    const messageBox = document.getElementById("messageBox");
    messageBox.textContent = message;
    messageBox.classList.add("show");

    // 3 秒后自动隐藏
    setTimeout(() => {
        messageBox.classList.remove("show");
    }, 3000);
}

function goBack() {
    // 移除当前路径的最后一级
    if (currentPath !== "/") {
        currentPath = currentPath.split("/").slice(0, -1).join("/") || "/";
        loadDirectory(currentPath);
    }
}

function toggleHidden() {
    showHidden = document.getElementById("showHidden").checked;
    loadDirectory(currentPath);
}

function loadDirectory(path) {
    document.getElementById("pathDisplay").textContent = "当前路径：" + path;

    // 如果路径不是根路径，则显示“返回上一层”按钮，否则隐藏它
    const backButton = document.getElementById("backButton");
    backButton.style.display = path !== "/" ? "inline-block" : "none";

    fetch(`/list?path=${encodeURIComponent(path)}&showHidden=${showHidden}`)
        .then(response => response.json())
        .then(data => displayFiles(data));
}


function displayFiles(files) {
    const fileList = document.getElementById("fileList");
    fileList.innerHTML = '';

    // 对文件夹、文件、隐藏文件排序
    files.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        if (a.name.startsWith('.') && !b.name.startsWith('.')) return 1;
        if (!a.name.startsWith('.') && b.name.startsWith('.')) return -1;
        return a.name.localeCompare(b.name);
    });

    files.forEach(file => {
        const fileDiv = document.createElement("div");
        fileDiv.classList.add("file-item");
        fileDiv.classList.add(file.isDirectory ? "folder" : "file");

        // 判断文件格式是否支持
        const fileExtension = file.name.split('.').pop().toLowerCase();
        const isSupported = Object.values(fileTypes).some(types => types.includes(fileExtension));
        if (isSupported) {
            fileDiv.classList.add("supported"); // 加粗样式
        }

        // 左侧：图标和文件名
        const fileNameContainer = document.createElement("div");
        fileNameContainer.classList.add("file-name");

        const fileIcon = document.createElement("span");
        fileIcon.classList.add("file-icon");
        if(fileTypes.video.includes(fileExtension)) {
            fileIcon.classList.add("fmt_video");
        } else if(fileTypes.text.includes(fileExtension)) {
            fileIcon.classList.add("fmt_txt");
        } else if(fileTypes.image.includes(fileExtension)) {
            fileIcon.classList.add("fmt_image");
        }

        const fileName = document.createElement("span");
        fileName.textContent = file.name;
        fileName.onclick = () => {
            if (file.isDirectory) selectDirectory(file.path);
            else previewFile(file.path);
        };

        fileNameContainer.appendChild(fileIcon); // 添加图标
        fileNameContainer.appendChild(fileName); // 添加文件名

        // 右侧：日期和按钮容器
        const fileDetailsContainer = document.createElement("div");
        fileDetailsContainer.classList.add("file-details");

        // 日期元素
        const fileTime = document.createElement("span");
        fileTime.classList.add("file-date");
        fileTime.textContent = file.time;

        // 按钮：SHA256 和 下载
        if (!file.isDirectory) {
            const shaButton = document.createElement("button");
            shaButton.textContent = "SHA256";
            shaButton.onclick = () => calculateSHA(file.path);

            const downloadButton = document.createElement("button");
            downloadButton.textContent = "下载";
            downloadButton.onclick = () => downloadFile(file.path);

            fileDetailsContainer.appendChild(fileTime);
            fileDetailsContainer.appendChild(shaButton);
            fileDetailsContainer.appendChild(downloadButton);
        } else {
            // 文件夹只显示日期和下载按钮
            const downloadButton = document.createElement("button");
            downloadButton.textContent = "下载";
            downloadButton.onclick = () => downloadFile(file.path);

            fileDetailsContainer.appendChild(fileTime);
            fileDetailsContainer.appendChild(downloadButton);
        }

        // 组合左侧和右侧内容
        fileDiv.appendChild(fileNameContainer); // 左侧内容：图标+文件名
        fileDiv.appendChild(fileDetailsContainer); // 右侧内容：日期+按钮

        fileList.appendChild(fileDiv);
    });
}


function calculateSHA(path) {
    // 找到当前路径对应的 SHA256 按钮
    const shaButton = event.target;
    
    // 禁用按钮，设置为“计算中...”
    shaButton.disabled = true;
    const originalText = shaButton.textContent; // 保存原始文本
    shaButton.textContent = "计算中...";

    fetch(`/sha256?path=${encodeURIComponent(path)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("计算失败");
            }
            return response.text();
        })
        .then(sha256Result => {
            // 计算成功，显示结果并恢复按钮
            alert(`SHA256: ${sha256Result}`);
            shaButton.textContent = originalText;
        })
        .catch(error => {
            // 计算失败，显示错误信息并恢复按钮
            alert(error.message);
            shaButton.textContent = "计算失败";
            setTimeout(() => {
                shaButton.textContent = originalText;
            }, 2000); // 2 秒后恢复原始文本
        })
        .finally(() => {
            // 最终恢复按钮的可点击状态
            shaButton.disabled = false;
        });
}


function downloadFile(path) {
    window.open(`/download?path=${encodeURIComponent(path)}`);
}

function previewFile(path) {
    const previewOverlay = document.getElementById("previewOverlay");
    const previewImage = document.getElementById("previewImage");
    const previewText = document.getElementById("previewText");
    const previewVideo = document.getElementById("previewVideo");
    const zoomControls = document.getElementById("zoomControls");

    // 清空上次的预览内容
    previewImage.style.display = "none";
    previewText.style.display = "none";
    previewVideo.style.display = "none";
    zoomControls.style.display = "none";
    previewVideo.src = ""; // 清空视频源以确保每次重新加载

    // 判断文件类型
    const fileExtension = path.split('.').pop().toLowerCase();

    if (fileTypes.image.includes(fileExtension)) {
        // 图片文件
        previewImage.src = `/preview?path=${encodeURIComponent(path)}`;
        previewImage.style.display = "block";
        zoomControls.style.display = "flex"; // 显示缩放按钮
        resetZoom(); // 重置缩放比例
    } else if (fileTypes.text.includes(fileExtension)) {
        // 文本文件
        fetch(`/preview?path=${encodeURIComponent(path)}`)
            .then(response => response.text())
            .then(content => {
                previewText.textContent = content;
                previewText.style.display = "block";
            });
    } else if (fileTypes.video.includes(fileExtension)) {
        // 视频文件
        previewVideo.src = `/preview?path=${encodeURIComponent(path)}`;
        previewVideo.style.display = "block";
    } else {
        // 不支持的文件类型，显示自定义消息框
        showMessage("不支持预览该文件类型。");
        return;
    }

    // 显示遮罩层
    previewOverlay.style.display = "flex";
}

// 放大功能
function zoomIn() {
    const previewImage = document.getElementById("previewImage");
    currentZoom += 0.1;
    previewImage.style.width = `${currentZoom * 100}%`;
    previewImage.style.height = "auto";
}

// 缩小功能
function zoomOut() {
    const previewImage = document.getElementById("previewImage");
    if (currentZoom > 0.2) { // 限制最小缩放比例
        currentZoom -= 0.1;
        previewImage.style.width = `${currentZoom * 100}%`;
        previewImage.style.height = "auto";
    }
}

// 复原功能
function resetZoom() {
    const previewImage = document.getElementById("previewImage");
    currentZoom = 1; // 重置缩放比例
    previewImage.style.width = "auto";
    previewImage.style.height = "auto";
}

// 关闭预览功能
function closePreview() {
    const previewOverlay = document.getElementById("previewOverlay");
    const previewVideo = document.getElementById("previewVideo");

    previewOverlay.style.display = "none";
    previewVideo.pause(); // 关闭时暂停视频
    previewVideo.src = ""; // 清空视频源
}
