
const channel = new Channel('logger/setup');
channel.on('data', handle_data);

function handle_data(data)
{
    let result = data.result
    if (result == "verified")
    {
        window.location = locations.get_dashboard(data.session_key);
    }
    else
    {
        console.log("There was an error");
    }
}

$('#setup').on('click', e => {
    setup();
});

function setup()
{
    const username = $('#username').val();
    const name = $('#name').val();
    const email = $('#email').val();
    const password = $('#password').val();
    const password_repeat = $('#password_repeat').val();

    let is_teacher = 'False';
    if ($('#is_teacher').is(':checked')) 
    {
        is_teacher = 'True';
    }
    
    if (password != password_repeat)
    {
        console.log("Cannot do");
        return;
    }
    
    const hashed_password = crypto.hash(password)
    const message = JSON.stringify({
        "username": username,
        "name": name,
        "email": email,
        "password": hashed_password,
        "is_teacher": is_teacher
    });

    channel.send(message);
}