(function(){
    var theme = getTheme();
    setTheme(theme);
}());

function addCss(filename) {
    var head = document.getElementsByTagName('head')[0];
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = filename;
    head.appendChild(link);
}
function removejscssfile(filename, filetype) {
    var targetelement = (filetype == "js") ? "script" : (filetype == "css") ? "link" : "none"
    var targetattr = (filetype == "js") ? "src" : (filetype == "css") ? "href" : "none"
    var allsuspects = document.getElementsByTagName(targetelement)
    for (var i = allsuspects.length; i >= 0; i--) {
        if (allsuspects[i] && allsuspects[i].getAttribute(targetattr) != null && allsuspects[i].getAttribute(targetattr).indexOf(filename) != -1)
            allsuspects[i].parentNode.removeChild(allsuspects[i])
    }
}


function getTheme(){
    var t = localStorage.getItem("theme");
    if(!t){
        t = "light";
        setTheme(t);
    }
    return t;
}
function setTheme(theme){
    var obj = document.getElementById("themes");
    if(theme=="dark"){
        if(obj){
            obj.classList.remove("light");
            obj.classList.add("dark");
        }
        document.getElementsByTagName("html")[0].classList.add("dark");
        // load dark and light togher, distingush by .dark class instead use single css file
        // removejscssfile("/maixpy/static/css/theme_default/light.css", "css");
        // addCss("/maixpy/static/css/theme_default/dark.css");
    }else{
        if(obj){
            obj.classList.remove("dark");
            obj.classList.add("light");
        }
        document.getElementsByTagName("html")[0].classList.remove("dark");
        // removejscssfile("/maixpy/static/css/theme_default/dark.css", "css");
        // addCss("/maixpy/static/css/theme_default/light.css");
    }
    localStorage.setItem("theme", theme);
}
