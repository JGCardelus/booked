class Renderer
{
    render_meetings()
    {
        for(let meeting in meetings.meetings)
        {
            this.render_meetings(meeting);
        }
    }
    
    render_meeting(meeting)
    {
        let id = '#meeting_' + meeting.meeting_id;
        if (!$(id).length)
        {
            // Does not exist, we can render
            let elem = `
                <div class="meeting_card" id="meeting_` + meeting.meeting_id + `">
                <div class="meeting_card_title">
                <h3>` + meeting.group_name + `</h3>
                </div>
                <div class="meeting_card_hour">
                <p>` + meeting.render_timestamp() + `</p>
                </div>
                <div class="meeting_card_buttons">
                <div class="button meeting_link">
                <p>Link</p>
                </div>
                <div class="button meeting_expand">
                <p>Más</p>
                </div>
                </div>
            `;
    
            $('div#meetings div.day_events_body').append(elem);
            meeting.add_triggers();
        }
    }
    
    clear_meetings()
    {
        $('div#meetings .day_events_body').html('');
    }
    
    render_tasks()
    {
        for(let task of tasks.tasks)
        {
            this.render_task(task);
        }
    }

    render_task(task)
    {
        let id = '#task_' + task.task_id;
        if (!$(id).length)
        {
            // The object does not exist, we can create it
            let elem = `
                <div class="task_card" id=task_` + task.task_id + `>
                    <div class="task_card_title">
                        <h3>` + task.group_name + ` </h3>
                    </div>
                    <div class="task_card_description">
                        <p>` + task.get_reduced_name() + `</p>
                    </div>
                    <div class="task_card_date">
                        <p>Para el `+ task.get_full_timestamp() +`</p>
                    </div>
                    <div class="task_card_button">
                        <div class="button">
                            <p>Más</p>
                        </div>
                    </div>
                </div>
            `;

            $('div#tasks div.day_events_body').append(elem);
            task.add_triggers();
        }
    }

    clear_tasks()
    {
        $('div#tasks div.day_events_body').html(''); 
    }
}

