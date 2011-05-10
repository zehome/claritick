/* Switch widgets On or Off based on isActivated widget */
function ghostOptions() 
{
    var isDeactivated = !options.isActivated.checked;
    console.log("ghostOptions");
    options.style.color = isDeactivated ? 'graytext' : 'black';
    
    for (var i=0; i < options_widgets.text.length; i++)
    {
        console.log("options.disabled: " + isDeactivated);
        options[options_widgets.text[i].name].disabled = isDeactivated;
    }
    for (var i=0; i < options_widgets.checkbox.length; i++)
        if (! options_widgets.checkbox[i].onchange_callback)
            options[options_widgets.checkbox[i].name].disabled = isDeactivated;
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
        { name: "onNewTicket", default: true }, 
        { name: "onNewTicketAssignedTo", default: true },
        { name: "onNewAnswer", default: true }
    ]
};

function loadSettings()
{
    for (var i=0; i < options_widgets.text.length; i++)
    {
        var widgetName = options_widgets.text[i].name;
        console.log('Setting value of ' + options[widgetName] + ' => ' +JSON.parse(localStorage[widgetName]));
        options[widgetName].value = JSON.parse(localStorage[widgetName]);
    }
    for (var i=0; i < options_widgets.checkbox.length; i++) 
    {
        var widgetName = options_widgets.checkbox[i].name;
        console.log('Setting value of ' + options[widgetName] + ' => ' +JSON.parse(localStorage[widgetName]));
        options[widgetName].checked = JSON.parse(localStorage[widgetName]);
    }
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
        var onchange = function(widget, widgetOption) {
            return function() {
                localStorage[widgetOption.name] = options[widgetOption.name].checked;
                if (widgetOption.onchange_callback) {
                    widgetOption.onchange_callback();
                }
            }
        };
    }
}
