

var conf=js_vars["teedoc-plugin-thumbs-up"];
(function(){
    document.addEventListener("DOMContentLoaded", function(event) {
        var contentBody = document.getElementById("content_body");
        if(!contentBody){
            return;
        }
        // add message show element
        var messageEL = document.createElement("div");
        messageEL.className = "thumbs-message";
        let msgContentEl = document.createElement("div");
        msgContentEl.classList = ["thumbs-message-content"];
        messageEL.appendChild(msgContentEl);
        contentBody.appendChild(messageEL);
        // create a div to hold the thumbs up button, and add it to the content body
        var thumbsUpDiv = document.createElement("div");
        thumbsUpDiv.id = "thumbs_up_container";
        contentBody.appendChild(thumbsUpDiv);
        // create the thumbs up button
        var thumbsUpButton = document.createElement("button");
        thumbsUpButton.classList = ["thumbs-up"];
        thumbsUpDiv.appendChild(thumbsUpButton);
        var thumbsUpIcon = document.createElement("img");
        thumbsUpIcon.src = conf.icon;
        thumbsUpIcon.classList = ["thumbs-up-icon"];
        thumbsUpButton.appendChild(thumbsUpIcon);
        var thumbsUpLabel = document.createElement("span");
        thumbsUpLabel.classList = ["thumbs-up-label"];
        thumbsUpLabel.innerHTML = conf.label_up;
        thumbsUpButton.appendChild(thumbsUpLabel);
        var thumbsUpCount = document.createElement("span");
        thumbsUpCount.classList = ["thumbs-up-count"];
        thumbsUpCount.innerHTML = "(0)";
        thumbsUpButton.appendChild(thumbsUpCount);
        // create the thumbs down button
        var thumbsDownButton = document.createElement("button");
        thumbsDownButton.classList = ["thumbs-down"];
        thumbsUpDiv.appendChild(thumbsDownButton);
        var thumbsDownIcon = document.createElement("img");
        thumbsDownIcon.src = conf.icon;
        thumbsDownIcon.classList = ["thumbs-down-icon"];
        thumbsDownButton.appendChild(thumbsDownIcon);
        var thumbsDownLabel = document.createElement("span");
        thumbsDownLabel.classList = ["thumbs-down-label"];
        thumbsDownLabel.innerHTML = conf.label_down;
        thumbsDownButton.appendChild(thumbsDownLabel);
        var thumbsDownCount = document.createElement("span");
        thumbsDownCount.classList = ["thumbs-down-count"];
        thumbsDownCount.innerHTML = "";
        thumbsDownButton.appendChild(thumbsDownCount);
        // add click listeners to the buttons
        var thumbs_up = document.getElementsByClassName("thumbs-up");
        for (var i = 0; i < thumbs_up.length; i++) {
            thumbs_up[i].addEventListener("click", function(e) {
                onClick(true);
            });
        }
        var thumbs_down = document.getElementsByClassName("thumbs-down");
        for (var i = 0; i < thumbs_down.length; i++) {
            thumbs_down[i].addEventListener("click", function(e) {
                onClick(false);
            });
        }
        setIcon();
        getCount();
    });
})();

function showMsg(msg){
    let msgEl = document.getElementsByClassName("thumbs-message")[0];
    let msgContentEl = document.getElementsByClassName("thumbs-message-content")[0];
    msgContentEl.innerHTML = msg;
    if (jQuery) {
        $(msgEl).fadeIn(500, function(){
            setTimeout(function(){
                $(msgEl).fadeOut(500);
            }, 3000);
        });
    }else{
        console.log("no jquery");
        msgEl.style.display = "flex";
        setTimeout(function(){
            msgEl.style.display = "none";
        }, 5000);
    }
}

function onClick(up){
    let path = check_path(location.pathname);
    let did = localStorage.getItem("thumbs_" + (up?"up":"down") + "_" + path);
    if (did){
        showMsg(conf.msg_already_voted);
        return;
    }
    var url = conf.url;
    if(up){
        url = url + "/api/thumbs_up";
    }else{
        url = url + "/api/thumbs_down";
    }
    var page = location.pathname
    var data = {
        "type": up ? "up" : "down",
        "path": page,
        "url": location.protocol + "//" + location.host + location.pathname
    };
    if(!up){
        data["msg"] = prompt(conf.msg_down_prompt);
        if(!data["msg"]){
            return;
        }
        if(data["msg"].length < 10){
            showMsg(conf.msg_down_prompt_error);
            return;
        }
    }
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            setUpCount(response["up_count"], up);
            setDownCount(response["down_count"], !up);
            showMsg(conf.msg_thanks);
        }else if (xhr.status != 200){
            showMsg(conf.msg_error);
        }
    };
    xhr.send(JSON.stringify(data));
}

function getCount(){
    let path = check_path(location.pathname);
    let url = conf.url + "/api/thumbs_count";
    var data = {
        "path": path
    };
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            setUpCount(response["up_count"]);
            setDownCount(response["down_count"]);
        }else if (xhr.status != 200){
            showMsg(conf.msg_error);
        }
    };
    xhr.send(JSON.stringify(data));
}

function check_path(path){
    if(!path){
        return path;
    }
    if (path[path.length - 1] == "/"){
        path = path + "index.html";
    }else{
        let temp = path.split("/");
        if(temp[temp.length - 1].indexOf(".") == -1){
            path = path + ".html";
        }
    }
    return path;
}

function setUpCount(count, add=false){
    if(add){
        let path = check_path(location.pathname);
        localStorage.setItem("thumbs_up_" + path, true);
        setIcon();
    }
    if(!conf.show_up_count){
        return;
    }
    var selector = ".thumbs-up-count";
    var thumbs_up = document.querySelector(selector);
    thumbs_up.innerHTML = "(" + count + ")";
}

function setDownCount(count, add=false){
    if(add){
        let path = check_path(location.pathname);
        localStorage.setItem("thumbs_down_" + path, true);
        setIcon();
    }
    if(!conf.show_down_count){
        return;
    }
    var selector = ".thumbs-down-count";
    var thumbs_down = document.querySelector(selector);
    thumbs_down.innerHTML = "(" + count + ")";
}

function setIcon(){
    let path = check_path(location.pathname);
    let upIcon = document.getElementsByClassName("thumbs-up-icon")[0];
    let downIcon = document.getElementsByClassName("thumbs-down-icon")[0];
    let did = localStorage.getItem("thumbs_up_" + path);
    if (did){
        upIcon.src = conf.icon_clicked;
    }else{
        upIcon.src = conf.icon;
    }
    did = localStorage.getItem("thumbs_down_" + path);
    if (did){
        downIcon.src = conf.icon_clicked;
    }else{
        downIcon.src = conf.icon;
    }
}
