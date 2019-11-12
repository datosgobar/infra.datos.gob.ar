var deleteDistribution = function (id) {
    var CSRFtoken = $("input[name=csrfmiddlewaretoken]").val();

    var url = $("#distributionDelete" + id).attr("data-url");
    $.post(url, {csrfmiddlewaretoken: CSRFtoken},
        function() {
            location.reload();
        });
};