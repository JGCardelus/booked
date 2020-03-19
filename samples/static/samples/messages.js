const connection_id = 'msg';
const web_socket = new WebSocket(
    'ws://' + window.location.host + '/ws/samples/messages/' + connection_id + '/'
);

web_socket.onmessage = e => {
    const data = JSON.parse(e.data);
    document.getElementById('received_data').innerHTML += '<li>' + data.message + '</li>';
}

web_socket.onclose = e => {
    console.log("Socket closed unxepectedly");
}

function send()
{
    let data = document.getElementById('text').value;
    web_socket.send(JSON.stringify(
        {
            "message": data
        }
    ));
    document.getElementById('text').value = '';
}
