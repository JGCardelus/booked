
let direction = window.location.pathname;
let direction_parts = direction.split('/');
const session_key = direction_parts[2];
let is_admin = false;

class Meeting
{
    constructor(meeting_id, group_id, group_name, time, duration, description, links)
    {
        this.meeting_id = meeting_id;
        this.group_id = group_id;
        this.group_name = group_name;
        
        let parsed_time = dates.parse_dateobj(time);
        
        this.date = parsed_time.date;
        this.time = parsed_time.time;

        this.duration = dates.parse_time(duration);
        this.description = description;
        this.links = links;

        this.description_maxlen = 1024;
    }

    render_timestamp()
    {
        let start = this.time;
        let end = dates.add_time(this.time, this.duration);

        let timestamp = start.render_timestamp() + ' - ' + end.render_timestamp();
        return timestamp;
    }

    add_triggers()
    {
        let id = '#meeting_' + this.meeting_id;
        $(id + ' .meeting_card_buttons .meeting_link').on('click', e =>
        {
            this.link();
        });

        $(id + ' .meeting_card_buttons .meeting_expand').on('click', e =>
        {
            this.expand();
        });
    }

    remove_triggers()
    {
        let id = '#meeting_' + this.meeting_id;
        $(id + ' .meeting_card_buttons .meeting_link').unbind();
        $(id + ' .meeting_card_buttons .meeting_expand').unbind();
    }

    link()
    {
        console.log("going to link");
    }

    expand()
    {
        console.log("expand");
    }
}

class Meetings
{
    constructor()
    {
        this.meetings = [];
        this.event_triggers = [];
    }

    parse(data)
    {
        let unsorted_meetings = [];
        for(let meeting_id of Object.keys(data))
        {
            let meeting_data = data[meeting_id]
            let group_id = meeting_data["group_id"];
            let group_name = meeting_data["group_name"];
            let time = meeting_data["time"];
            let duration = meeting_data["duration"];
            let description = meeting_data["description"];
            let links = meeting_data["links"];

            let new_meeting = new Meeting(
                meeting_id.toString(),
                group_id,
                group_name,
                time, 
                duration,
                description,
                links
            );

            unsorted_meetings.push(new_meeting);
        }
        this.meetings = dates.sort_by_datetime(unsorted_meetings);
        this.trigger('data');
    }

    on(event, callback)
    {
        if (!this.event_triggers[event])
        {
            this.event_triggers[event] = [];
        }
        this.event_triggers[event].push(callback);
    }

    trigger(event, params)
    {
        if (this.event_triggers[event])
        {
            for (let trigger_function of this.event_triggers[event])
            {
                trigger_function(params);
            }
        }
    }

    clear()
    {
        if(this.meetings.length > 0)
        {
            for (let meeting of meetings)
            {
                meeting.remove_triggers();
            }
        }
        this.meetings = [];
        this.trigger('clear');
    }

    get_today()
    {   
        this.clear();
        let today = dates.get_today();
        let date = today.render_datestamp();
        
        this.get(date=date);
    }

    get(date='%-%-%', time='%:%', groups=null)
    {
        let message = JSON.stringify(
            {
                'request': 'filter',
                'data': 'meetings',
                'session_key': session_key,
                'date': date,
                'time': time,
                'groups': groups
            }
        );
    
        event_dispatcher_channel.send(message);
    }

    get_more(n, meeting_id, date='%-%-%', time='%:%', groups=null)
    {
        this.clear();
        let message = JSON.stringify(
            {
                'request': 'more',
                'data': 'meetings',
                'session_key': session_key,
                'n': n,
                'meeting_id': meeting_id,
                'date': date,
                'time': time,
                'groups': groups
            }
        );

        event_dispatcher_channel.send(message);
    }

    get_range(date_a='%-%-%', time_a='%:%', date_b='%-%-%', time_b='%:%', groups=null)
    {
        this.clear();
        let message = JSON.stringify(
            {
                'request': 'range',
                'data': 'meetings',
                'session_key': session_key,
                'date_a': date_a,
                'time_a': time_a,
                'date_b': date_b,
                'time_b': time_b,
                'groups': groups
            }
        );

        event_dispatcher_channel.send(message);
    }
}

class Task
{
    constructor(task_id, group_id, group_name, name, due_date, notes)
    {
        this.task_id = task_id;
        this.group_id = group_id;
        this.group_name = group_name;
        this.name = name;
        
        let date_time = dates.parse_dateobj(due_date);
        this.date = date_time.date;
        this.time = date_time.time;
        this.notes = notes;

        this.name_maxlen = 512;
    }

    get_reduced_name()
    {
        let reduced_length = this.name;
        if(this.name.length > this.name_maxlen)
        {
            reduced_length = this.name.slice(0, this.name_maxlen);
        }
        return reduced_length
    }

    get_full_timestamp()
    {
        let week_day = dates.get_dayname(this.date.year, this.date.month, this.date.day);
        let a = week_day + ', ' + this.date.day.toString();
        return a;
    }

    add_triggers()
    {
        let id = '#task_' + this.task_id;
        $(id + ' .task_card_button .button').on('click', e =>
        {
            this.expand();
        });
    }

    remove_triggers()
    {
        let id = '#task_' + this.task_id;
        $(id + ' .task_card_button .button').unbind();
    }

    expand()
    {
        console.log("expanded");
    }
}

class Tasks
{
    constructor()
    {
        this.tasks = [];
        this.event_triggers = [];
    }

    parse(data)
    {
        let unsorted_tasks = [];
        for(let task_id of Object.keys(data))
        {
            let task_data = data[task_id]
            let group_id = task_data["group_id"];
            let group_name = task_data["group_name"];
            let due_date = task_data["due_date"];
            let name = task_data["name"];
            let notes = task_data["notes"];
            
            let new_task = new Task(
                task_id,
                group_id,
                group_name,
                name,
                due_date,
                notes
            );

            unsorted_tasks.push(new_task);
        }

        this.tasks = dates.sort_by_datetime(unsorted_tasks);
        this.trigger('data');
    }

    on(event, callback)
    {
        if (!this.event_triggers[event])
        {
            this.event_triggers[event] = [];
        }
        this.event_triggers[event].push(callback);
    }

    trigger(event, params)
    {
        if (this.event_triggers[event])
        {
            for (let trigger_function of this.event_triggers[event])
            {
                trigger_function(params);
            }
        }
    }

    clear()
    {
        if(this.tasks.length > 0)
        {
            for(let task of tasks)
            {
                task.remove_triggers();
            }
        }
        this.tasks = [];
        this.trigger('clear');
    }

    get_week()
    {
        let today = dates.get_today();
        let monday = dates.get_monday_of_current_week(today);
        let sunday = dates.get_sunday_of_current_week(today);

        let monday_datestamp = monday.render_datestamp();
        let sunday_datestamp = sunday.render_datestamp();

        this.get_range(monday_datestamp, '%:%', sunday_datestamp, '%:%', null, null);
    }

    get(date='%-%-%', time='%:%', groups=null, name=null)
    {
        this.clear();
        let message = JSON.stringify(
            {
                'request': 'filter',
                'data': 'tasks',
                'session_key': session_key,
                'date': date,
                'time': time,
                'groups': groups,
                'name': name
            }
        );
    
        event_dispatcher_channel.send(message);
    }

    get_more(n, task_id, date='%-%-%', time='%:%', groups=null, name=null)
    {
        this.clear();
        let message = JSON.stringify(
            {
                'request': 'more',
                'data': 'tasks',
                'session_key': session_key,
                'n': n,
                'task_id': task_id,
                'date': date,
                'time': time,
                'groups': groups,
                'name': name
            }
        );

        event_dispatcher_channel.send(message);
    }

    get_range(date_a='%-%-%', time_a='%:%', date_b='%-%-%', time_b='%:%', groups=null, name=null)
    {
        this.clear();
        let message = JSON.stringify(
            {
                'request': 'range',
                'data': 'tasks',
                'session_key': session_key,
                'date_a': date_a,
                'time_a': time_a,
                'date_b': date_b,
                'time_b': time_b,
                'groups': groups,
                'name': name
            }
        );
        
        event_dispatcher_channel.send(message);
    }
}

const event_dispatcher_channel = new Channel('dashboard');
event_dispatcher_channel.on('open', e => {
    message = JSON.stringify(
        {
            'request': 'info',
            'data': 'handshake',
            'session_key': session_key
        }
    );

    event_dispatcher_channel.send(message);
});
event_dispatcher_channel.on('data', data_handler);

let meetings = new Meetings();
let tasks = new Tasks();

/* REWRITE AND DELETE */

function data_handler(data)
{
    let response = data.response;
    if (response == 'meetings')
    {
       meetings.parse(data["data"]);
    }
    if(response == 'tasks')
    {
        tasks.parse(data["data"]);
    }
    if(response == 'handshake')
    {
        is_admin = data["data"];
    }
}
