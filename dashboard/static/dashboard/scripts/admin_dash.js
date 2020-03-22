let navbar = new Navbar(session_key);
navbar.set_date();

let renderer = new Renderer();
meetings.on('data', function ()
{
    renderer.render_meetings();
});

meetings.on('clear', function ()
{
    renderer.clear_meetings();
});

tasks.on('data', function() 
{
    renderer.render_tasks();
});

tasks.on('clear', function() 
{
    renderer.clear_tasks();
});

event_dispatcher_channel.on('open', function()
{
    tasks.get_week();
    meetings.get_today();
})

$('#meetings .day_events_expander .button').on('click', () => 
{
    const url = locations.get_filters(session_key, 'meetings');
    window.location = url;
});

$('#tasks .day_events_expander .button').on('click', () => 
{
    const url = locations.get_filters(session_key, 'tasks');
    window.location = url;
});