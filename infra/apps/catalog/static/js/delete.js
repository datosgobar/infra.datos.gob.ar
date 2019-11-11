var deleteDistribution = function () {
    var CSRFtoken = $("input[name=csrfmiddlewaretoken]").val();

    var url = $("#distributionDelete").attr("data-url");
    $.post(url, {csrfmiddlewaretoken: CSRFtoken},
        function() {
            location.reload();
        });
};