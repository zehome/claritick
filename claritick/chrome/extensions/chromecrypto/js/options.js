function onUIChanged(onload)
{
    var isEnabled = dojo.attr("cc_isEnabled", "checked");
    dojo.attr("cc_key", "disabled", ! isEnabled);
    dojo.attr("cc_isSaveOnDisk", "disabled", ! isEnabled);
    dojo.attr("cc_isAutoDecrypt", "disabled", ! isEnabled);
    if (! onload)
        dojo.attr("save-button", "disabled", false);
}

/* Connect signals for save, and "dirty" flag for save */
function connectOptions()
{
    dojo.connect(dojo.byId("cc_isEnabled"), "onclick", function() { onUIChanged(); });
    dojo.connect(dojo.byId("cc_isSaveOnDisk"), "onclick", function() { onUIChanged(); });
    dojo.connect(dojo.byId("cc_isAutoDecrypt"), "onclick", function() { onUIChanged(); });
    dojo.connect(dojo.byId("cc_key"), "keyup", function() { onUIChanged(); });
    dojo.connect(dojo.byId("save-button"), "onclick", function() { saveUI(); });
    dojo.attr("save-button", "disabled", true);
    loadUI();
}

function saveUI()
{
    var bg = chrome.extension.getBackgroundPage();
    var settings = bg.loadSettings();
    settings.isEnabled = dojo.attr("cc_isEnabled", "checked");
    settings.isSaveOnDisk = dojo.attr("cc_isSaveOnDisk", "checked");
    settings.isAutoDecrypt = dojo.attr("cc_isAutoDecrypt", "checked");
    settings.key = dojo.attr("cc_key", "value");
    bg.saveSettings(settings);
    dojo.attr("save-button", "disabled", true);
}

function loadUI()
{
    var bg = chrome.extension.getBackgroundPage();
    var settings = bg.loadSettings();
    dojo.attr("cc_key", "value", settings.key);
    dojo.attr("cc_isAutoDecrypt", "checked", settings.isAutoDecrypt); 
    dojo.attr("cc_isSaveOnDisk", "checked", settings.isSaveOnDisk); 
    dojo.attr("cc_isEnabled", "checked", settings.isEnabled);
    onUIChanged(onload = true);
}
