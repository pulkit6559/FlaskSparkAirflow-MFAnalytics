

document.addEventListener('DOMContentLoaded', function() {
    // Get the matched_lines data from the page
    var matchedLines = {% if matched_lines %} {{ matched_lines | tojson | safe }} {% else %} [] {% endif %};

    // Attach a click event listener to the "Submit Job" button
    document.getElementById('submitJobBtn').addEventListener('click', function() {
        // Send an AJAX request with the matched_lines data
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '{{ url_for('start_dag') }}', true);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({ matched_lines: matchedLines }));

        // You can perform additional actions after sending the request if needed
        // For example, display a success message or redirect the user
    });
});
