dojo.require('dojox.fx.scroll');
dojo.require('dojox.fx');

function confirmDialog(title, question, callbackFn, callback_arg)
{
    console.log(callback_arg);
    var errorDialog = new dijit.Dialog({ id: 'queryDialog', title: title });
    function callback(mouseEvent)
    {
        errorDialog.hide();
        errorDialog.destroyRecursive();
        var srcEl = mouseEvent.srcElement? mouseEvent.srcElement : mouseEvent.target;
        if(srcEl.id == "yes_label"
            || srcEl.id == "yes"
            || srcEl.children[0].id == "yes")
            callbackFn(true, callback_arg);
        else
            callbackFn(false, callback_arg);
    };
    var questionDiv = dojo.create('div', { innerHTML: question });
    var yesButton = new dijit.form.Button(
        {label: 'Oui', id: 'yes', onClick: callback});
    var noButton = new dijit.form.Button(
        {label: 'Non', id: 'no', onClick: callback});
    errorDialog.containerNode.appendChild(questionDiv);
    errorDialog.containerNode.appendChild(yesButton.domNode);
    errorDialog.containerNode.appendChild(noButton.domNode);
    errorDialog.show();
}

/* Post "inputs" dictionnary to post_url_or_form */
function postwith (inputs,post_url_or_form)
{
    function convert_to_form(url)
    {
        f = document.createElement("form");
        f.method = "POST";
        f.action = url;
        return f;
    }
    console.log("postwith "+post_url_or_form);
    if (typeof post_url_or_form == 'string')
        f = convert_to_form(post_url_or_form)
    else
        f = post_url_or_form;
    console.log(f);
    inputs["csrfmiddlewaretoken"] = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    for (var k in inputs)
    {
        var i = document.createElement("input") ;
        i.setAttribute("name", k);
        i.setAttribute("value", inputs[k]);
        f.appendChild(i);
    }
    document.body.appendChild(f);
    f.submit();
    document.body.removeChild(f);
}

function scrollAndHighlight(target, scrollDuration, highlightDuration)
{
    dojox.fx.smoothScroll({
            node: target,
            win: window,
            duration: scrollDuration
    }).play();
    if(highlightDuration)
        highlight(target, highlightDuration, '#ffd76a');
}

function highlight(target, highlightDuration, color, endCallback)
{
    dojox.fx.highlight({
            node: target,
            duration: highlightDuration,
            color: color,
            onEnd: endCallback
    }).play();
}
