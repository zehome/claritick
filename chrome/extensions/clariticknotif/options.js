Storage.prototype.setObject = function(key, value) {
    this.setItem(key, JSON.stringify(value));
}
Storage.prototype.getObject = function(key) {
    return this.getItem(key) && JSON.parse(this.getItem(key));
}

/* Switch widgets On or Off based on isActivated widget */
function ghostOptions() 
{
    var isDeactivated = !options.isActivated.checked;
    console.log("ghostOptions");
    options.style.color = isDeactivated ? 'graytext' : 'black';
    
    for (var i=0; i < options_widgets.text.length; i++)
    {
        if (options_widgets.text[i].onchange_callback)
            continue;
        try {
            options[options_widgets.text[i].name].disabled = isDeactivated;
        } catch (e) { console.error("Unable to disable widget "+ options_widgets.text[i].name); }
    }
    for (var i=0; i < options_widgets.checkbox.length; i++)
    {
        if (options_widgets.checkbox[i].onchange_callback)
            continue;
        try {
            options[options_widgets.checkbox[i].name].disabled = isDeactivated;
        } catch (e) { console.error("Unable to disable widget "+ options_widgets.checkbox[i].name); }
    }
}

var options_widgets = {
    text: [
        { name: "wsHost", default: "localhost" },
        { name: "wsPort", default: 8010 },
        { name: "djangoURL", default: "http://localhost:8000/notifications/" },
        { name: "notificationTimeout", default: 10 }
    ],
    checkbox: [
        { name: "isActivated", default: false, onchange_callback: ghostOptions },
        { name: "isSecure", default: true },
    ]
};

function loadSettings()
{
    for (var i=0; i < options_widgets.text.length; i++)
    {
        var widgetName = options_widgets.text[i].name;
        console.log('Setting value of ' + options[widgetName] + ' => ' +JSON.parse(localStorage[widgetName]));
        try {
            options[widgetName].value = JSON.parse(localStorage[widgetName]);
        } catch (e) {
            console.error("Unable to get settings for " + widgetName);
        }
    }
    for (var i=0; i < options_widgets.checkbox.length; i++) 
    {
        var widgetName = options_widgets.checkbox[i].name;
        console.log('Setting value of ' + options[widgetName] + ' => ' +JSON.parse(localStorage[widgetName]));
        try {
            options[widgetName].checked = JSON.parse(localStorage[widgetName]);
        } catch (e) {
            console.error("Unable to get settings for " + widgetName);
        }
    }
    
    /* LC: Todo load tags */
}

/* Returns the javascript data */
function getOption(name)
{
    return JSON.parse(localStorage[name]);
}

function resetSettings()
{
    for (var i=0; i < options_widgets.text.length; i++)
    {
        var widgetOption = options_widgets.text[i];
        var default_value = widgetOption.default;
        localStorage[widgetOption.name] = JSON.stringify(default_value);
    }
    for (var i=0; i < options_widgets.checkbox.length; i++) 
    {
        var widgetOption = options_widgets.checkbox[i];
        var default_value = widgetOption.default;
        localStorage[widgetOption.name] = default_value;
    }
    localStorage.tags = {};
    localStorage.isInitialized = true;
}

/* Listen events on option widgets, store the result
 * in the local Storage
 */
function loadOptionPage()
{
    try {
        loadSettings();
    } catch (e) {
        console.log("Unable to load settings. Reinitializing it.");
        console.log("Original error: "+e);
        localStorage.isInitialized = false;
        resetSettings();
        loadSettings();
    }
    
    /* Load page colors */
    ghostOptions();
    
    /* Connect widgets to localStorage */
    for (var i=0; i < options_widgets.checkbox.length; i++) 
    {
        var widgetOption = options_widgets.checkbox[i];
        var widget = options[widgetOption.name];
        if (! widget)
            continue;
        
        var onchange = function(widget, widgetOption) {
            return function() {
                localStorage[widgetOption.name] = options[widgetOption.name].checked;
                if (widgetOption.onchange_callback) {
                    widgetOption.onchange_callback();
                }
            }
        };
        widget.onchange = onchange(widget, widgetOption);
    }
    for (var i=0; i < options_widgets.text.length; i++) 
    {
        var widgetOption = options_widgets.text[i];
        var widget = options[widgetOption.name];
        if (! widget)
            continue;
        
        var onchange = function(widget, widgetOption) {
            return function() {
                localStorage[widgetOption.name] = JSON.stringify(options[widgetOption.name].value);
                if (widgetOption.onchange_callback) {
                    widgetOption.onchange_callback();
                }
            }
        };
        widget.onchange = onchange(widget, widgetOption);
    }
    
    options_load_tags();
}

function options_load_tags()
{
    var lsTags = localStorage.getObject('tags');
    for (tagid in lsTags)
    {
        var formTagName = "tag_"+tagid 
        widget = options[formTagName];
        if (! widget)
        {
            console.log("add widget...");
            widget = add_tag_widget(tagid, lsTags[tagid].label, lsTags[tagid].value);
        }
        console.log("widget: "+ widget);
        var onchange = function(widget, tagid) {
            return function() {
                console.log("onchange widget: "+widget + " tagid: " + tagid);
                var lsTags = localStorage.getObject('tags');
                lsTags[tagid].value = options["tag_"+tagid].checked;
                localStorage.setObject('tags', lsTags);
            }
        };
        widget.onchange = onchange(widget, tagid);
    }
}

/* This will add a tag in the <div id="tag_checkboxes"> */
function add_tag_widget(tagid, label, value)
{
    var tagsWidget = document.getElementById("tag_checkboxes");
    var e = document.createElement("li");
    
    e.innerText = label;
    var i = document.createElement("input");
    i.setAttribute("type", "checkbox");
    i.setAttribute("name", "tag_"+tagid);
    if (value)
        i.setAttribute("checked", "");
    e.appendChild(i);
    tagsWidget.appendChild(e);
    return e;
}

/* This handle onClick event of get tags button. */
/* Uses client.js */
function options_get_tags()
{
    /* Getting div for displaying progress */
    var progressWidget = document.getElementById("get_tags_progress");
    var tagsWidget = document.getElementById("tag_checkboxes");
    
    progressWidget.innerHTML = "Checking... <progress></progress>";
    
    var okCallback = function(tags) {
        progressWidget.innerHTML = "Tags synchronized."
        var lsTags = localStorage.getObject('tags');
        sync_tags(tags);
        options_load_tags();
    };
    var errorCallback = function(status, message) {
        if (status === 403)
            progressWidget.innerHTML = "You are not logged. Please login the django application.";
        else 
            progressWidget.innerHTML = "An error occured. Not able to get tags. Check Django Notification URL.";
    };
    getOptionTags(okCallback, errorCallback);
}

/* This utility function permits to sync between django tags
 * received with xhr and localStorage.
 * If the tag does not exists in the localStorage,
 * then it will be set to true by default.
 */
function sync_tags(django_tags)
{
    var lsTags;
    lsTags = localStorage.getObject('tags');
    if (! lsTags)
        lsTags = {};
    
    for (var tagid in django_tags)
    {
        if (! lsTags[tagid])
        {
            lsTags[tagid] = {
                label: django_tags[tagid],
                value: true
            };
        }
    }
    
    /* Scan for orphan */
    if (django_tags)
    {
        for (var tagid in lsTags)
        {
            if (! django_tags[tagid])
            {
                /* Present in localStorage, but removed in django.
                 * Simply remove the widget if found, and remove
                 * localStorage value.
                 */
                if (options["tag_"+tagid])
                    document.getElementById("tag_checkboxes").removeChild(widget);
                delete lsTags[tagid];
            }
        }
    }
    
    localStorage.setObject('tags', lsTags);
}