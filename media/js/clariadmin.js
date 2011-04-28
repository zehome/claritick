dojo.require('dojox.fx.scroll');
dojo.require('dojox.fx');

/* LC: TODO: WTF ? Where is the comment ? */
function postwith (inputs,post_url_or_form) 
{
    function convert_to_form(url)
    {
        f = document.createElement("form");
        f.method = "POST";
        f.action = url;
        return f;
    }
    /* LC: TODO: Horrible uggly */
    f = (typeof post_url_or_form == 'string')?convert_to_form(post_url_or_form):post_url_or_form;
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
  dojox.fx.smoothScroll(
	{
		node: target,
		win: window,
		duration: scrollDuration
	}).play();
  if(highlightDuration)
    highlight(target, highlightDuration, '#ffd76a');
}

function highlight(target, highlightDuration, color, endCallback) 
{
  dojox.fx.highlight(
	{
    node: target,
    duration: highlightDuration,
    color: color,
    onEnd: endCallback
	}).play();
}
