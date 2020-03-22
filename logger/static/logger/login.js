// Start websocket
const channel = new Channel('logger/login');
channel.on('data', handle_data);

$('#enter').on('click', e => {
    login();
});

function login()
{
    const username = $('#username').val();
    const password = $('#password').val();

    const hashed_password = crypto.hash(password);
    if (channel.connected)
    {
        // Build message
        const message = JSON.stringify(
            {
                "request": "verify",
                "username": username,
                "password": hashed_password
            }
        );

        channel.send(message);
    }
}

function handle_data(data)
{
    let response = data.response;
    if (response == 'verified')
    {
        window.location = locations.get_dashboard(data.session_key);
    }
    else 
    {
        console.log("Raise error message");
    }
}