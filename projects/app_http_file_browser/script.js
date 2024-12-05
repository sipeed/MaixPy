let currentPath = '/root';
let showHidden = false;
let currentZoom = 0.8; // 初始缩放比例

// 支持的文件类型字典
const fileTypes = {
    image: ['jpg', 'jpeg', 'png', 'gif'],
    text: ['txt', 'md', 'py', 'mud', 'json', 'yaml', 'yml', 'conf', 'ini', 'version', 'log'],
    video: ['mp4', 'webm', 'ogg', 'avi', 'flv']
};

let translations = {}; // 存储翻译内容

// 加载语言文件，根据用户的语言设置选择合适的语言文件
function loadLanguage() {
    const userLang = navigator.language || 'zh';
    const lang = userLang.startsWith('en') ? 'en' : 'zh';
    fetch(`locales/${lang}.json`)
        .then(response => response.json())
        .then(data => {
            translations = data;
            updateTexts();
        });
}

// 更新界面中的所有文本内容
function updateTexts() {
    document.getElementById("pageTitle").textContent = translations.title;
    document.getElementById("pathDisplay").textContent = translations.currentPath + currentPath;
    document.getElementById("labelShowHidden").textContent = translations.showHidden;
    document.getElementById("backButton").textContent = translations.backButton;
    document.getElementById("closeButton").textContent = translations.closePreview;
    document.getElementById("zoomInButton").textContent = translations.zoomIn;
    document.getElementById("zoomOutButton").textContent = translations.zoomOut;
    document.getElementById("resetZoomButton").textContent = translations.resetZoom;

    // 更新动态生成的按钮文本
    document.querySelectorAll(".sha256-button").forEach(btn => {
        btn.textContent = translations.sha256;
    });
    document.querySelectorAll(".download-button").forEach(btn => {
        btn.textContent = translations.download;
    });
}

// 页面加载完成后加载语言和初始化目录
document.addEventListener("DOMContentLoaded", () => {
    loadLanguage();
    loadDirectory(currentPath);
});

// 选择目录，更新当前路径
function selectDirectory(path) {
    currentPath = path;
    loadDirectory(currentPath);
}

// 显示自定义消息框
function showMessage(messageKey) {
    const messageBox = document.getElementById("messageBox");
    messageBox.textContent = translations[messageKey] || messageKey;
    messageBox.classList.add("show");

    // 3 秒后自动隐藏
    setTimeout(() => {
        messageBox.classList.remove("show");
    }, 3000);
}

// 返回上一层目录
function goBack() {
    if (currentPath !== "/") {
        currentPath = currentPath.split("/").slice(0, -1).join("/") || "/";
        loadDirectory(currentPath);
    }
}

// 切换是否显示隐藏文件
function toggleHidden() {
    showHidden = document.getElementById("showHidden").checked;
    loadDirectory(currentPath);
}

// 加载指定目录内容
function loadDirectory(path) {
    document.getElementById("pathDisplay").textContent = translations.currentPath + path;
    const backButton = document.getElementById("backButton");
    backButton.style.display = path !== "/" ? "inline-block" : "none";

    fetch(`/list?path=${encodeURIComponent(path)}&showHidden=${showHidden}`)
        .then(response => response.json())
        .then(data => displayFiles(data));
}

// 显示文件列表
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
        fileDiv.classList.add("file-item", file.isDirectory ? "folder" : "file");

        const fileExtension = file.name.split('.').pop().toLowerCase();
        const isSupported = Object.values(fileTypes).some(types => types.includes(fileExtension));
        if (isSupported) fileDiv.classList.add("supported");

        const fileNameContainer = document.createElement("div");
        fileNameContainer.classList.add("file-name");

        const fileIcon = document.createElement("span");
        fileIcon.classList.add("file-icon", `fmt_${fileTypes.video.includes(fileExtension) ? "video" : fileTypes.text.includes(fileExtension) ? "txt" : "image"}`);
        const fileName = document.createElement("span");
        fileName.textContent = file.name;
        fileName.onclick = () => {
            if (file.isDirectory) selectDirectory(file.path);
            else previewFile(file.path);
        };

        fileNameContainer.append(fileIcon, fileName);

        const fileDetailsContainer = document.createElement("div");
        fileDetailsContainer.classList.add("file-details");
        const fileTime = document.createElement("span");
        fileTime.classList.add("file-date");
        fileTime.textContent = file.time;

        if (!file.isDirectory) {
            const shaButton = document.createElement("button");
            shaButton.classList.add("sha256-button");
            shaButton.textContent = translations.sha256;
            shaButton.onclick = () => calculateSHA(file.path);

            const downloadButton = document.createElement("button");
            downloadButton.classList.add("download-button");
            downloadButton.textContent = translations.download;
            downloadButton.onclick = () => downloadFile(file.path);

            fileDetailsContainer.append(fileTime, shaButton, downloadButton);
        } else {
            const downloadButton = document.createElement("button");
            downloadButton.classList.add("download-button");
            downloadButton.textContent = translations.download;
            downloadButton.onclick = () => downloadFile(file.path);

            fileDetailsContainer.append(fileTime, downloadButton);
        }

        fileDiv.append(fileNameContainer, fileDetailsContainer);
        fileList.appendChild(fileDiv);
    });
}

// 计算文件的 SHA256 值
function calculateSHA(path) {
    const shaButton = event.target;
    shaButton.disabled = true;
    const originalText = shaButton.textContent;
    shaButton.textContent = translations.calculate;

    fetch(`/sha256?path=${encodeURIComponent(path)}`)
        .then(response => response.ok ? response.text() : Promise.reject("计算失败"))
        .then(sha256Result => alert(`SHA256: ${sha256Result}`))
        .catch(error => alert(error))
        .finally(() => {
            shaButton.disabled = false;
            shaButton.textContent = originalText;
        });
}

// 下载文件
function downloadFile(path) {
    window.open(`/download?path=${encodeURIComponent(path)}`);
}

// 预览文件
function previewFile(path) {
    const previewOverlay = document.getElementById("previewOverlay");
    const previewImage = document.getElementById("previewImage");
    const previewText = document.getElementById("previewText");
    const previewVideo = document.getElementById("previewVideo");

    previewImage.style.display = previewText.style.display = previewVideo.style.display = "none";
    previewVideo.src = ""; // 清空视频源

    const fileExtension = path.split('.').pop().toLowerCase();
    if (fileTypes.image.includes(fileExtension)) {
        // 图片文件预览
        previewImage.src = `/preview?path=${encodeURIComponent(path)}`;
        previewImage.style.display = "block";
        resetZoom();
    } else if (fileTypes.text.includes(fileExtension)) {
        // 文本文件预览
        fetch(`/preview?path=${encodeURIComponent(path)}`)
            .then(response => response.text())
            .then(content => {
                previewText.textContent = content;
                previewText.style.display = "block";
            });
    } else if (fileTypes.video.includes(fileExtension)) {
        // 视频文件预览
        previewVideo.src = `/preview?path=${encodeURIComponent(path)}`;
        previewVideo.style.display = "block";

        // 添加错误事件监听器
        previewVideo.onerror = () => {
            if(previewVideo.src != "") {
                showMessage("videoPlayError"); // 使用键值来显示翻译后的错误提示信息
            }
        };
    } else {
        showMessage("unsupportedFileType"); // 不支持的文件类型
        return;
    }

    // 显示遮罩层
    previewOverlay.style.display = "flex";
}

// 放大功能
function zoomIn() {
    currentZoom += 0.1;
    document.getElementById("previewContent").style.width = `${currentZoom * 100}%`;
}

// 缩小功能
function zoomOut() {
    if (currentZoom > 0.2) currentZoom -= 0.1;
    document.getElementById("previewContent").style.width = `${currentZoom * 100}%`;
}

// 重置缩放比例
function resetZoom() {
    currentZoom = 0.8;
    const previewImage = document.getElementById("previewImage");
    previewImage.style.width = "auto";
    previewImage.style.height = "auto";
}

// 关闭预览
function closePreview() {
    document.getElementById("previewOverlay").style.display = "none";
    document.getElementById("previewVideo").pause();
}
