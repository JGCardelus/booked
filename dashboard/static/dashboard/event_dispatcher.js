
let direction = window.location.pathname;
let direction_parts = direction.split('/');

const session_key = direction_parts[2];
const event_dispatcher_channel = new Channel('dashboard');
event_dispatcher_channel.on('data', data_handler);

class Meetings
{
    constructor()
    {
        
    }

    parse(data)
    {
        
    }
}

let meetings = new Meetings();

function data_handler(data)
{
    let response = data.response;
    if (response == 'meetings')
    {
        meetings.parse(data["data"]);
    }
}

function get_meetings(date='%-%-%', time='%:%', groups=null)
{
    let message = JSON.stringify(
        {
            'request': 'meetings',
            'session_key': session_key,
            'date': date,
            'time': time,
            'groups': groups
        }
    );

    event_dispatcher_channel.send(message);
}