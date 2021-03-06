import logging

from flask import request, make_response

from app import app
from app.views.create_change_start import show_view_create_change_start
from app.views import rename_change
from app.helpers.slack import verify_request
from app.helpers.redis import redis_q
from app.workflows import change_going_live, next_change


@app.route("/commands", methods=["POST"])
def process_command():
    if not verify_request(request):
        return make_response("", 403)

    form = request.form
    command_text = form["text"]
    logging.debug(f"Command received: {request.form['command']} {command_text}")

    trigger_id = request.form["trigger_id"]

    if command_text == "new":
        # We show an initial start view so that we can give enough time to perform slow actions async.
        # This is to help us manage Slack's strict timeout rules.
        redis_q.enqueue(show_view_create_change_start, trigger_id, form)
        return make_response("", 200)

    elif command_text == "next":
        response_url = request.form["response_url"]
        redis_q.enqueue(next_change.next_change, response_url)
        return make_response("", 200)

    elif command_text == "rename":
        redis_q.enqueue(rename_change.rename_channel, request.form)
        return make_response("", 200)

    elif command_text == "release":
        redis_q.enqueue(change_going_live.change_going_live, request.form)
        return make_response("", 200)

    else:
        return make_response(
            f"*{command_text}* command is not supported currently.", 200
        )
