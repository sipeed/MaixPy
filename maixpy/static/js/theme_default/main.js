
(function () {
    var elements = document.getElementsByTagName("pre");
    for(var i=0; i<elements.length; ++i){
        elements[i].classList.add("language-none");
        elements[i].classList.add("line-numbers");
    }
    // $('pre').addClass("language-none");
    // $('pre').addClass("line-numbers").css("white-space", "pre-wrap");
}());

window.onload = function(){
}

var sleep = function(time) {
    var startTime = new Date().getTime() + parseInt(time, 10);
    while(new Date().getTime() < startTime) {}
};

$(document).ready(function(){
    $("#sidebar ul .show").slideDown(200);
    registerSidebarClick();
    addTOC();
    addSequence();
    var has_sidebar = document.getElementById("sidebar_wrapper");
    if(has_sidebar){
        addSplitter();
        focusSidebar();
    }
    addAnchor();
    registerOnWindowResize(has_sidebar);
    hello();
    imageViewer();
    if(false){
        addPrintPage();
    }
    addTocMobileListener();
    addTabsetListener();
});

var sidebar_width = "300px";
var sidebar_width_is_percent = false;
try{
    if(isNaN(sidebar_width)){
        if(sidebar_width.endsWith("px")){
            sidebar_width = parseInt(sidebar_width.substr(0, sidebar_width.length-2));
        }else if(sidebar_width.endsWith("%")){
            sidebar_width = parseInt(sidebar_width.substr(0, sidebar_width.length-1));
            sidebar_width_is_percent = true;
        }else{
            sidebar_width = parseInt(sidebar_width);
        }
    }
}catch(err){
    alert('plugin theme env sidebar_width value error, e.g. 300 or "300px" or "30%", not ' + sidebar_width);
}

function menu_show(show)
{
    if(show){
        $("#menu_wrapper").addClass("m_menu_fixed");
        $("#menu").addClass("close");
        $("#to_top").addClass("m_hide");
        $("#sidebar_wrapper").show(100);
        $(".gutter").css("display", "block");
        focusSidebar();
    }else{
        $("#menu_wrapper").removeClass("m_menu_fixed");
        $("#menu").removeClass("close");
        $("#to_top").removeClass("m_hide");
        $("#sidebar_wrapper").hide(100);
        $(".gutter").css("display", "none");
        $("#article").css("width", "100%"); // recover set by splitter
    }
}
function menu_toggle(){
    if(!$("#sidebar_wrapper").is(':visible')){ // show
        menu_show(true);
    }else{ // hide
        menu_show(false);
    }
}

function registerSidebarClick(){
    function show_collapse_item(a_obj){
        var o_ul = a_obj.next();
        var collapsed = !o_ul.hasClass("show");
        if(collapsed){
            o_ul.slideDown(200);
            o_ul.removeClass("collapsed");
            o_ul.addClass("show");
            a_obj.children(".sub_indicator").removeClass("sub_indicator_collapsed");
        }else {
            o_ul.slideUp(200);
            o_ul.removeClass("show");
            o_ul.addClass("collapsed");
            a_obj.children(".sub_indicator").addClass("sub_indicator_collapsed");
        }
    }
    $("#menu").bind("click", function(e){
        menu_toggle();
    });
    $("#navbar_menu_btn").bind("click", function(e){
        $("#navbar_items").toggle();
    });
    var theme = getTheme();
    setTheme(theme);
    $("#themes").bind("click", function(e){
        var theme = getTheme();
        if(theme == "light"){
            setTheme("dark");
        }else {
            setTheme("light");
        }
    });
    $("#to_top").bind("click", function(e){
        window.scrollTo({
                            top: 0, 
                            behavior: "smooth" 
                        });
        return false;
    });
    $("#sidebar ul li > a").bind("click", function(e){
        var is_click_indicator = $(e.target).hasClass("sub_indicator");
        var a_obj = $(this);
        if(a_obj.attr("href") == window.location.pathname){
            show_collapse_item(a_obj);
            return false;
        }
        show_collapse_item(a_obj);
        if(is_click_indicator){ // click indicator, only collapse, not jump to link
            return false;
        }
        var screenW = $(window).width();
        if(screenW > 900){
            return;
        }
        link_href = $(this).attr("href").split(location.host);
        if(link_href.length > 1){
            link_href = link_href[1];
        }else{
            link_href = link_href[0];
        }
        url_href = location.href.split(location.host)[1]
        let link_url = link_href.split("#")[0];
        let sub = $(this).next();
        var haveSub = false;
        if(sub && sub.prop("nodeName")){
            haveSub = sub.prop("nodeName").toLowerCase() == "ul";
        }
        if((link_href != decodeURIComponent(url_href) || !haveSub) && location.pathname == link_url){ // current page, and jump to header, close sidebar
            location.href = link_href;
            menu_toggle();
        }
    });
}

function hello(){
    console.log('\n\n\
     _                _            \n\
    | |              | |           \n\
    | |_ ___  ___  __| | ___   ___ \n\
    | __/ _ \\/ _ \\/ _` |/ _ \\ / __|\n\
    | ||  __/  __/ (_| | (_) | (__ \n\
     \\__\\___|\\___|\\__,_|\\___/ \\___|\n\
                                         \n\
                 generated by teedoc:            \n\
                                                 \n\
                 https://github.com/teedoc/teedoc\n\
                                                 \n\n\n\
');
}


function addTOC(){
    if(!document.getElementById("toc_content"))
        return;
    tocbot.init({
        // Where to render the table of contents.
        tocSelector: '#toc_content',
        // Where to grab the headings to build the table of contents.
        contentSelector: '#article_content',
        // Which headings to grab inside of the contentSelector element.
        headingSelector: 'h1, h2, h3, h4',
        // For headings inside relative or absolute positioned containers within content.
        hasInnerContainers: true,
        });
}

function toChineseNumber(n) {
    if (!Number.isInteger(n) && n < 0) {
      throw Error('请输入自然数');
    }

    const digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
    const positions = ['', '十', '百', '千', '万', '十万', '百万', '千万', '亿', '十亿', '百亿', '千亿'];
    const charArray = String(n).split('');
    let result = '';
    let prevIsZero = false;
    //处理0  deal zero
    for (let i = 0; i < charArray.length; i++) {
      const ch = charArray[i];
      if (ch !== '0' && !prevIsZero) {
        result += digits[parseInt(ch)] + positions[charArray.length - i - 1];
      } else if (ch === '0') {
        prevIsZero = true;
      } else if (ch !== '0' && prevIsZero) {
        result += '零' + digits[parseInt(ch)] + positions[charArray.length - i - 1];
      }
    }
    //处理十 deal ten
    if (n < 100) {
      result = result.replace('一十', '十');
    }
    return result;
  }

function addSequence(){
    if(!tocbot._parseContent){
        return;
    }
    var headings = tocbot._parseContent.selectHeadings(document.getElementById("article_content"), tocbot.options.headingSelector);
    var counth2=0, counth3=0, counth4=0;
    var html = document.getElementsByTagName("html")[0];
    var isZh = html.lang.substring(0, 2).toLowerCase() == "zh";
    for(var i=0; i<html.classList.length; ++i){
        if(html.classList[i] == "heading_no_counter"){
            return;
        }
    }

    var headerJoiner = ".";

    for(var i=0; i<headings.length; ++i){
        var headerEnd = ". ";
        if(headings[i].tagName == "H1"){
            counth2 = 0;
            continue;
        }

        if(headings[i].tagName == "H2"){
            counth2 += 1;
            counth3 = 0;
            var counts = [counth2];
            if (isZh){
                var counts = counts.map(toChineseNumber);
                headerEnd = "、";
            }
        } else if(headings[i].tagName == "H3"){
            counth3 += 1;
            counth4 = 0;
            var counts = [counth2, counth3];
        } else if(headings[i].tagName == "H4"){
            counth4 += 1;
            var counts = [counth2, counth3, counth4];
        }
        var seq = counts.join(headerJoiner) + headerEnd
        headings[i].insertAdjacentHTML('afterbegin', '<span class="sequence">' + seq + '</span>');
    }
}


function getSplitter(){
    var sizes = localStorage.getItem("splitter_w");
    if(sizes){
        try
        {
        sizes = JSON.parse(sizes);
        }
        catch(err)
        {
            sizes = false;
        }
    }
    if(!sizes){
        var screenW = $(window).width();
        var split_w = 0;
        if(!sidebar_width_is_percent){
            split_w = parseInt(sidebar_width/screenW*100);
        }else{
            split_w = sidebar_width;
        }
        sizes = [split_w, 100-split_w];
        setSplitter(sizes);
    }
    return sizes;
}
function setSplitter(sizes){
    localStorage.setItem("splitter_w", JSON.stringify(sizes));
}

var hasSplitter = false;

function createSplitter(){
    var split = Split(["#sidebar_wrapper", "#article"],{
        gutterSize: 3,
        gutterAlign: 'start',
        minSize: 200,
        elementStyle: function (dimension, size, gutterSize) {
            return {
                'width': 'calc(' + size + '% - ' + gutterSize + 'px)',
            }
        },
        onDragEnd: function (sizes) {
            setSplitter(sizes)
        },
    });
    hasSplitter = true;
    var screenW = $(window).width();
    var sizes = getSplitter();
    split_w = parseInt(sizes[0]);
    if(isNaN(split_w) || (split_w + 20) >= screenW){
    if(!sidebar_width_is_percent){
    split_w = parseInt(sidebar_width/screenW*100);
    }else{
    split_w = sidebar_width;
    }
    }
    split.setSizes([split_w, 100 - split_w]);
    $(".gutter").append('<div class="gutter_icon"></div>');
    $(".gutter").hover(function(){
        $(".gutter").css("width", "10px");
        $(".gutter_icon").css("width", "10px");
    },function(){
        $(".gutter").css("width", "3px");
        $(".gutter_icon").css("width", "3px");
    });
}

function addSplitter(){
    var screenW = $(window).width();
    if(screenW > 900)
    {
        createSplitter();
    }
}

function registerOnWindowResize(has_sidebar){
    window.onresize = function(){
        var screenW = $(window).width();
        if(!has_sidebar){
            return;
        }
        if(screenW < 900){
            $("#sidebar_wrapper").removeAttr("style");
            if($("#menu").hasClass("close")){
                $("#sidebar_wrapper").css("display", "block");    
            }
            $(".gutter").css("display", "none");
            $("#article").css("width", "100%");
        }else{
            if(!hasSplitter){
                createSplitter();
            }
            if($("#sidebar_wrapper").css("display") != "none"){
                $(".gutter").css("display", "block");
            }
        }
    }
}

function focusSidebar(){
    var windowH = window.innerHeight;
    var active = $("#sidebar .active")[0];
    if(!active)
        return;
    var offset = active.offsetTop;
    if(offset > windowH/2){
        $("#sidebar .show").scrollTop(offset);
    }
}

function imageViewer(){
    var content_e = document.getElementById("content_body");
    if(!content_e){
        content_e = document.getElementById("page_wrapper");
    }
    const gallery = new Viewer(content_e);
}

function addAnchor(){
    $("#content_body h2, #content_body h3, #content_body h4, #content_body h5").each(function(){
        if($(this).attr("id")){
            $(this).append('<a class="anchor" href="#'+ $(this).attr("id") +'">#</a>');
        }
    });
}

function rerender(){
    Prism.highlightAll();
}

function addPrintPage(){
    if(!$("#article_info_right")){
        return;
    }
    $("#article_info_right").append('<div id="print_page"></div>');

    var beforePrint = function(){
        // update style changed by js:
        $("#article").css("width", "100%");
        // rerender for proper output
        rerender();
    }
    var afterPrint = function() {
        // location.reload();
    }
    if (window.matchMedia) {
        var mediaQueryList = window.matchMedia('print'); 
        mediaQueryList.addListener(function(mql) {
            if (mql.matches) {
                beforePrint();
            } else {
                afterPrint();
            }
        });
    }
    window.onbeforeprint = beforePrint;
    window.onafterprint = afterPrint;
    $("#print_page").click(function(){
        window.print();
    });
}

function addTocMobileListener(){
    $("#toc_btn").click(function(){
        if($("#toc_wrapper").hasClass("show")){
            $("#toc_wrapper").removeClass("show");
        }else{
            $("#toc_wrapper").addClass("show");
        }
    });
    $("#toc_wrapper").click(function(){
        if($("#toc_btn").is(":visible")){
            $("#toc_wrapper").removeClass("show");
        }
    });
}

function addTabsetListener(){
    $(".tabset-tab-label").on("click", function(){
        let this_obj = $(this);
        // already active, do nothing
        if(this_obj.hasClass("tabset-tab-active")){
            return;
        }
        // remove all active tabset-tab-active and tabset-text-active class from all have class that startswith tabset-id-,
        // then add active class to the same idx tab-label and tab-text
        let tabset_id = null;
        let same_id_tabsets = [];
        let old_idx = this_obj.parent().find(".tabset-tab-active").attr("idx");
        let new_idx = this_obj.attr("idx");
        let tabset_obj = this_obj.parent().parent().parent();
        tabset_obj.attr("class").split(' ').forEach(function(item){
            if(item.startsWith("tabset-id-")){
                tabset_id = item;
            }
        });
        if(!tabset_id){
            same_id_tabsets = [tabset_obj[0]]; // to DOM element
        }else{
            same_id_tabsets = document.getElementsByClassName(tabset_id);
        }
        for (let tabset of same_id_tabsets) {
            console.log(tabset);
            let tab_labels = tabset.getElementsByClassName("tabset-tab-label");
            tab_labels[old_idx].classList.remove("tabset-tab-active");
            tab_labels[new_idx].classList.add("tabset-tab-active");
            let tab_texts = tabset.getElementsByClassName("tabset-text");
            tab_texts[old_idx].classList.remove("tabset-text-active");
            tab_texts[new_idx].classList.add("tabset-text-active");
        }
    });
}
