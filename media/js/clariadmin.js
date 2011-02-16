function confirmDialog(title, question, callbackFn, e) {
    var errorDialog = new dijit.Dialog({ id: 'queryDialog', title: title });
    function callback(mouseEvent) {
        errorDialog.hide();
        errorDialog.destroyRecursive();
        if (window.event) e = window.event;
        var srcEl = mouseEvent.srcElement? mouseEvent.srcElement : mouseEvent.target; //IE or Firefox
        if(srcEl.id == "yes_label" || srcEl.id == "yes" || srcEl.children[0].id == "yes"){
            callbackFn(true, e);
        } else {
            callbackFn(false, e);}
    };
    var questionDiv = dojo.create('div', { innerHTML: question });
    var yesButton = new dijit.form.Button(
        { label: 'Oui', id: 'yes', onClick: callback });
    var noButton = new dijit.form.Button(
        { label: 'Non', id: 'no', onClick: callback });
    errorDialog.containerNode.appendChild(questionDiv);
    errorDialog.containerNode.appendChild(yesButton.domNode);
    errorDialog.containerNode.appendChild(noButton.domNode);
    errorDialog.show();
}
function postwith (inputs,post_url_or_form) {
    function convert_to_form(url){
        f=document.createElement("form");
        f.method="POST" ;f.action = url;
        return f;
    }
    f = (typeof post_url_or_form == 'string')?convert_to_form(post_url_or_form):post_url_or_form;
    inputs["csrfmiddlewaretoken"]=document.getElementsByName("csrfmiddlewaretoken")[0].value;
    for (var k in inputs){
        var i = document.createElement("input") ;
        i.setAttribute("name", k) ;
        i.setAttribute("value", inputs[k]);
        f.appendChild(i) ;
    }
    document.body.appendChild(f) ;
    f.submit() ;
    document.body.removeChild(f) ;
}
