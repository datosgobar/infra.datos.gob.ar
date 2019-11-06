function copyUrlToClipBoard(element){
    var url = window.location.hostname;
    if (window.location.port !== "") {
        url += ":" + window.location.port;
    }
    url += element.dataset.url;

    var input = document.createElement("input");
    document.getElementsByTagName("BODY")[0].append(input);
    input.value = url
    input.select();
    document.execCommand("copy");
    input.remove();
}