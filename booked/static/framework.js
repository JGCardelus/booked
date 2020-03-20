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
}

let locations = new Locations();