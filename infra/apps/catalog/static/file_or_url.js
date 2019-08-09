window.onload = function () {
    fileOrUrl();
};


function hideHelp() {
    document.getElementById("file-or-url").className += " hidden";
}

function fileOrUrl() {
    var file_button = document.getElementById("file-button");
    file_button.onclick = function () {
        document.getElementById("file-field").classList.remove("hidden");
        hideHelp();
    };
    var url_button = document.getElementById("url-button");
    url_button.onclick = function () {
        document.getElementById("url-field").classList.remove("hidden");
        hideHelp();
    };
}