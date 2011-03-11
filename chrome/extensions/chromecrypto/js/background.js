/* Initialize listening handlers */
setupHandlers();

var settings;

const defaultSettings = {
    key: '',
    isEnabled: false,
    isAutoDecrypt: true,
    isSaveOnDisk: true
};

/* Save settings in memory and on disk if possible. */
function saveSettings(newSettings)
{
    console.log("Saving settings.");
    var saveState = defaultSettings;
    if (newSettings.isSaveOnDisk)
    {
        saveState.key = newSettings.key;
    } else {
        saveState.key = '';
    }
    saveState.isSaveOnDisk = newSettings.isSaveOnDisk;
    saveState.isEnabled = newSettings.isEnabled;
    saveState.isAutoDecrypt = newSettings.isAutoDecrypt;
    localStorage["settings"] = JSON.stringify(saveState);

    settings = newSettings;
    return settings;
}

/* Load settings from disk */
function loadSettings()
{
    if (settings) return settings;
    console.log("Loading settings.");
    if (! localStorage["settings"])
    {
        console.log("Loading default settings.");
        settings = defaultSettings;
        saveSettings(settings);
    } else {
        try {
            settings = JSON.parse(localStorage["settings"]);
        } catch (e) {
            console.log("Error loading settings: " + e);
        }
    }
    return settings;
}

function setupHandlers()
{
    chrome.extension.onRequest.addListener(
        function(request, sender, sendResponse)
        {
            try {
                switch(request.action)
                {
                     case "mayUncipher":
                        /* Show the crypto icon on the page */
                        chrome.pageAction.show(sender.tab.id);
                        //chrome.pageAction.setPopup(sender.tab.id, "popup.html");
                        sendResponse({"settings": loadSettings()});
                        break;
                     default:
                        sendResponse({});
                        break;
                }
            } catch (e) {
                /* LC: catchall needed to let the app "release" the signal */
                alert(e);
                console.log("Error in background page listener: " + e);
                sendResponse({});
            }    
        }
    );
}
