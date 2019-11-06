window.onload = function () {
    showFieldEvents();
    returnEvents();
};


function hideHelp() {
    document.getElementById("file-or-url").className += " hidden";
}

function showHelp() {
    document.getElementById("file-or-url").classList.remove("hidden");
}

function showFieldEvents() {
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

function returnEvents() {
    var fileButton = document.getElementById("file-return-button");
    fileButton.onclick = function () {
        document.getElementById("file-field").classList.add("hidden");
        document.getElementById("id_file").value = "";
        showHelp();
    };
    var url_button = document.getElementById("url-return-button");
    url_button.onclick = function () {
        document.getElementById("url-field").classList.add("hidden");
        document.getElementById("id_url").value = "";
        showHelp();
    };
}
