let navbar = new Navbar(session_key);
navbar.set_date();

let elem = meetings;
let title = 'Reuniones';
if (params == 'tasks')
{
    title = 'Tareas';
    elem = tasks;
}

$('#title h1').html(title);

class Renderer
{
    constructor()
    {

    }

    render(elements)
    {
        for (element in elements)
        {
            
        }
    }

    create_meeting(meeting)
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
            
            return elem;
        }
        return $(id).html();
    }

    create_task(task)
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

            return elem;
        }
        return $(id).html();
    }
}