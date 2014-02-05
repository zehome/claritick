function onUIChanged(onload)
{
    console.log("onUIChanged")
    var isEnabled = options.cc_isEnabled.checked;
    options.cc_key.disabled = ! isEnabled;
    options.cc_isSaveOnDisk.disabled = ! isEnabled;
    options.cc_isAutoDecrypt.disabled = ! isEnabled;
    console.log("onload: "+onload);
    if (onload !== true) {
        options.save.disabled = false;
    }
}

function saveUI()
{
    var bg = chrome.extension.getBackgroundPage();
    var settings = bg.loadSettings();
    settings.isEnabled = options.cc_isEnabled.checked;
    settings.isSaveOnDisk = options.cc_isSaveOnDisk.checked;
    settings.isAutoDecrypt = options.cc_isAutoDecrypt.checked;
    settings.key = options.cc_key.value;
    bg.saveSettings(settings);
    options.save.disabled = true;
}

function loadUI()
{
    var bg = chrome.extension.getBackgroundPage();
    var settings = bg.loadSettings();
    options.cc_key.value = settings.key;
    options.cc_isAutoDecrypt.checked = settings.isAutoDecrypt;
    options.cc_isSaveOnDisk.checked = settings.isSaveOnDisk;
    options.cc_isEnabled.checked = settings.isEnabled;
    onUIChanged(onload = true);
}


/* Connect signals for save, and "dirty" flag for save */
function connectOptions()
{
    options.cc_isEnabled.onchange = onUIChanged;
    options.cc_isSaveOnDisk.onchange = onUIChanged;
    options.cc_isAutoDecrypt.onchange = onUIChanged;
    options.cc_key.onchange = onUIChanged;
    options.cc_isEnabled.onchange = onUIChanged;
    options.save.onclick = saveUI;
    options.save.disabled = true;
    loadUI();
}

document.addEventListener('DOMContentLoaded', connectOptions);