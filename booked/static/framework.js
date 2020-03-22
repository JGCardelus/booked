class Channel
{
    constructor(url)
    {
        this.url = url;
        this.connected = true;
        this.interval = null;

        this.queue = [];
        this.socket = this.create(url);

        this.event_triggers = {};
    }

    create(url)
    {
        let socket = null;
        try {
            socket = new WebSocket(
                'ws://' + window.location.host + '/ws/'  + url
            );
        } catch ( error ) {
            return null;
        }
        

        socket.onopen = e => 
        {
            if (this.interval != null)
            {
                clearInterval(this.interval);
            }

            this.trigger('open');
            this.connected = true;
            this.clear_queue();
        }

        socket.onmessage = e => {
            this.trigger('data', JSON.parse(e.data));
        }

        socket.onclose = e => {
            this.connected = false;
            this.trigger('close');
            this.interval = setInterval(this.reopen(), 2000);
        }

        return socket
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

    reopen()
    {
        this.socket = this.create(this.url)
    }

    send(data)
    {
        this.queue.push(data);
        this.clear_queue();
    }

    clear_queue()
    {
        if (this.connected)
        {
            if (this.queue.length > 0)
            {
                let send_queue = this.queue
                for (let i = 0; i < send_queue.length; i++)
                {
                    this.socket.send(send_queue[i]);
                    this.queue.splice(i, 1);
                }
            }
        }
    }
}

class Crypto
{
    hash(data)
    {
        const data_bin = sjcl.hash.sha256.hash(data);
        const data_str = sjcl.codec.hex.fromBits(data_bin);

        return data_str;
    }
}

let crypto = new Crypto();

class Locations
{
    constructor()
    {
        this.header = 'http://' + window.location.host;
    }

    get_dashboard(session_key)
    {
        const url = this.header + '/dashboard/' + session_key;
        return url;
    }

    get_filters(session_key, params)
    {
        const url = this.header + '/dashboard/' + session_key + '/filters/' + params;
        return url;
    }

    get_groups(session_key)
    {
        const url = this.header + '/dashboard/' + session_key + '/groups';
        return url;
    }

    get_new_meeting(session_key, params)
    {
        const url = this.header + '/dashboard/' + session_key + '/new_meeting/' + params;
        return url;
    }

    get_new_task(session_key, params)
    {
        const url = this.header + '/dashboard/' + session_key + '/new_task/' + params;
        return url;
    }
}

let locations = new Locations();

class Date_Var
{
    constructor()
    {
        this.year = null;
        this.month = null;
        this.day = null;
        this.weekday = null;
        this.hour = null;
        this.min = null;
    }

    set_week(year, month, day)
    {
        this.year = year;
        this.month = month;
        this.day = day;
    }

    set_time(hour, minutes)
    {
        this.hour = hour;
        this.min = minutes;
    }

    render_timestamp()
    {
        let hour = this.pad(this.hour.toString(), 2);
        let minute = this.pad(this.min.toString(), 2);
        let a =  hour + ':' + minute;
        return a;
    }

    render_datestamp()
    {
        let year = this.pad(this.year.toString(), 4);
        let month = this.pad(this.month.toString(), 2);
        let day = this.pad(this.day.toString(), 2);
        let a =  year + '-' + month + '-' + day;
        return a;
    }

    pad(num, size) {
        let s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }
}

class Dates
{
    constructor()
    {
        this.days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    }

    get_today()
    {
        let date = new Date();
        let date_var = new Date_Var();
        date_var.year = 1900 + date.getYear();
        date_var.month = 1 + date.getMonth();
        date_var.day = date.getDate();
        date_var.weekday = this.days[date.getDay()];
        date_var.hour = date.getHours();
        date_var.min = date.getMinutes();

        return date_var;
    }

    get_dayname(year, month, day) {
        let date = new Date(year, month - 1, day);
        let day_name = this.days[date.getDay()];
        return day_name;
    }

    get_monday_of_current_week(date)
    {
        let d = this.to_date(date);
        let day = d.getDay();
        if (day == 0)
        {
            day = 7;
        }
        let raw_date = new Date(d.getFullYear(), d.getMonth(), d.getDate() - day);
        let final_date = this.to_date_var(raw_date);

        return final_date;
    }

    get_sunday_of_current_week(date)
    {
        let d = this.to_date(date);
        let day = d.getDay();
        if (day == 0)
        {
            day = 7;
        }
        day = 7 - day;
        let raw_date = new Date(d.getFullYear(), d.getMonth(), d.getDate() + day);
        let final_date = this.to_date_var(raw_date);
        
        return final_date;
    }

    parse_time(raw_time)
    {
        let raw_time_parts = raw_time.split(':');
        let hour = parseInt(raw_time_parts[0]);
        let minute = parseInt(raw_time_parts[1]);

        let time = new Date_Var();
        time.set_time(hour, minute);
        
        return time;
    }

    parse_date(raw_date)
    {
        let raw_date_parts = raw_date.split('-');
        let year = parseInt(raw_date_parts[0]);
        let month = parseInt(raw_date_parts[1]);
        let day = parseInt(raw_date_parts[2])

        let date = new Date_Var();
        date.set_week(year, month, day);
        
        return date;
    }

    parse_dateobj(obj)
    {
        let date_elem = obj.split('+')[0];
        let date_time = date_elem.split(' ');

        let date = this.parse_date(date_time[0]);
        let time = this.parse_time(date_time[1]);

        return {
            date: date,
            time: time
        }
    }

    add_time(time_a, time_b)
    {
        let minutes = time_a.min + time_b.min;
        let extra_hours = 0;

        while (minutes >= 60)
        {
            minutes -= 60;
            extra_hours++;
        }

        let hours = time_a.hour + time_b.hour + extra_hours;
        while (hours >= 24)
        {
            hours -= 24;
        }

        let time = new Date_Var();
        time.set_time(hours, minutes);

        return time;
    }

    is_date_bigger(date_a, date_b)
    {
        if (date_a.year > date_b.year)
        {
            return true;
        }

        if (date_a.month > date_b.month)
        {
            return true;
        }

        if (date_a.day > date_b.day)
        {
            return true;
        }

        return false;
    }

    is_date_equal(date_a, date_b)
    {
        if (date_a.year != date_b.year)
        {
            return false;
        }

        if (date_a.month != date_b.month)
        {
            return false;
        }

        if (date_a.day != date_b.day)
        {
            return false;
        }

        return true;
    }

    is_time_bigger(time_a, time_b)
    {
        if (time_a.hour > time_b.hour)
        {
            return true;
        }

        if (time_a.min > time_a.min)
        {
            return true;
        }

        return false;
    }

    sort_by_datetime(elements)
    {
        for (let i = 0; i < elements.length; i++)
        {
            for(let j = i; j < elements.length; j++)
            {
                if (i != j)
                {
                    let change = false;
                    let date_a = elements[i].date;
                    let date_b = elements[j].date;

                    change = this.is_date_bigger(date_a, date_b);
                    if (!change)
                    {
                        let check_time = this.is_date_equal(date_a, date_b);
                        if (check_time)
                        {
                            let time_a = elements[i].time;
                            let time_b = elements[j].time;
                            change = this.is_time_bigger(time_b, time_a);
                        }
                    }
                    
                    if (change)
                    {
                        let helper = elements[i];
                        elements[i] = elements[j];
                        elements[j] = helper;
                    }
                }
            }
        }

        return elements;
    }

    to_date(date_var)
    {
        let date = new Date(date_var.year, date_var.month - 1, date_var.day);
        return date;
    }

    to_date_var(date)
    {
        let date_var = new Date_Var();
        date_var.set_week(date.getFullYear(), date.getMonth() + 1, date.getDate());
        return date_var;
    }
}

let dates = new Dates();

class Navbar
{
    constructor(session_key)
    {
        this.session_key = session_key;

        this.elem = $('nav');
        this.refresh_date = setInterval(e => {
            this.set_date();
        }, 60000);

        this.add_triggers();
    }

    set_date()
    {
        let date = dates.get_today();
        let num = date.day;
        let weekday_part = date.weekday.slice(0, 3);

        $('nav div#nav_date h1').html(weekday_part + ', ' + num.toString());
    }

    go(url)
    {
        window.location = url;
    }

    add_triggers()
    {
        if($('#nav_groups').length)
        {
            $('#nav_groups').on('click', () => 
            {
                const url = locations.get_groups(this.session_key);
                this.go(url); 
            });
        }

        if($('#nav_meeting').length)
        {
            $('#nav_meeting').on('click', () => 
            {
                const url = locations.get_new_meeting(this.session_key, 'none');
                this.go(url); 
            });
        }

        if($('#nav_task').length)
        {
            $('#nav_task').on('click', () => 
            {
                const url = locations.get_new_task(this.session_key, 'none');
                this.go(url); 
            });
        }

        if($('#nav_home').length)
        {
            $('#nav_home').on('click', () => 
            {
                const url = locations.get_dashboard(this.session_key);
                this.go(url); 
            });
        }
    }
}