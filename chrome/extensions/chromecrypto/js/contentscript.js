const cryptoRegex = /\{chromecrypto:([^\}]+)\}/gi;

function findAndDecrypt()
{
    chrome.extension.sendRequest({"action": "mayUncipher"}, 
        function(response)
        {
            var settings = response.settings;
            if (! settings) { return; }
            if (settings.isEnabled && settings.isAutoDecrypt && settings.key) {
                uncipherAll(settings);
            }
        }
    );
}

function uncipherAndReplaceTagData(settings, tag)
{
    var byValue = dojo.attr(tag, "value") != null;
    if (byValue) {
        var original = dojo.attr(tag, "value");
    } else {
        var original = tag.innerHTML;
    }
    if (original) 
    {
        var unciphered = original.replace(cryptoRegex, 
            function(matches, data) 
            { 
                return uncipherData(settings, data); 
            }
        );
        if (unciphered != original)
        {
            var imgURL = chrome.extension.getURL("images/unciphered.png");
            var imgTAG = '<img style="display: inline;" src="'+imgURL+'" alt="unciphered">';
            if (byValue)
            {
                dojo.attr(tag, "value", unciphered);
                dojo.place(imgTAG, tag.parentNode.parentNode, "after");
//            } else {
//                tag.innerHTML = imgTAG + " " + unciphered;
            }
        }
   }
}

/* Find and replace all ciphered text. */
function uncipherAll(settings)
{
    dojo.forEach(dojo.query('input[type="text"], p, span, td'), 
        function(tag) 
        { 
            uncipherAndReplaceTagData(settings, tag); 
        }
    );
}

function uncipherData(settings, ciphered)
{
    var data = base64Decode(ciphered);
    var plain = rc4Encrypt(settings.key, data);
    return plain;
}

window.setInterval("findAndDecrypt()", 1000);
