function filterDataset(value) {
    var selectedDataset = value;
    var url = window.location.origin + window.location.pathname;
    window.location = url + "?dataset_identifier=" + selectedDataset;
}