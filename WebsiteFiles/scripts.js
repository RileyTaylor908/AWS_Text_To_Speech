const API_ENDPOINT = "https://sve4a6z7y1.execute-api.us-east-2.amazonaws.com/dev";

document.getElementById("sayButton").onclick = function() {
    const inputData = {
        "voice": $('#voiceSelected option:selected').val(),
        "text": $('#postText').val()
    };

    $.ajax({
        url: API_ENDPOINT,
        type: 'POST',
        data: JSON.stringify(inputData),
        contentType: 'application/json; charset=utf-8',
        success: function(response) {
            document.getElementById("postIDreturned").textContent = "Post ID: " + response;
        },
        error: function() {
            alert("Error submitting text-to-speech request.");
        }
    });
};

document.getElementById("searchButton").onclick = function() {
    const postId = $('#postId').val();

    $.ajax({
        url: `${API_ENDPOINT}?postId=${postId}`,
        type: 'GET',
        success: function(response) {
            $('#posts tbody').empty();

            response.forEach(data => {
                const player = data.url ? `<audio controls><source src="${data.url}" type="audio/mpeg"></audio>` : "";

                $("#posts tbody").append(`
                    <tr>
                        <td>${data.id}</td>
                        <td>${data.voice}</td>
                        <td>${data.text}</td>
                        <td>${data.status}</td>
                        <td>${player}</td>
                    </tr>
                `);
            });
        },
        error: function() {
            alert("Error retrieving posts.");
        }
    });
};

document.getElementById("postText").onkeyup = function() {
    const length = $('#postText').val().length;
    document.getElementById("charCounter").textContent = "Characters: " + length;
};
