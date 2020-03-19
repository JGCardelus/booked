$('#enter').on('click', e => {
    login();
});

function login()
{
    const username = $('#username').val();
    const password = $('#password').val();

    console.log(username, password);
}