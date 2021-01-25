from datetime import date
import logging

from jira import JIRA

from app import app


def create_jira_release(change_number, user_name, description):
    if app.config["ENABLE_JIRA_INTEGRATION"]:
        logging.debug("Creating Jira client")
        jira_options = {"server": app.config["JIRA_SERVER"]}

        try:
            jira_client = JIRA(
                options=jira_options,
                basic_auth=(app.config["JIRA_USERNAME"], app.config["JIRA_PASSWORD"]),
            )
            logging.debug("Jira client created")

        except Exception as e:
            logging.exception(f"Couldn't create Jira client")

        today = date.today()
        change_name = app.config["JIRA_PREFIX"] + change_number

        try:
            version = jira_client.create_version(
                name=change_name,
                project=app.config["JIRA_PROJECT_KEY"],
                startDate=today.strftime("%Y-%m-%d"),
                description=description,
            )
            version_id = version.id
            return f"{app.config['JIRA_SERVER']}/projects/{app.config['JIRA_PROJECT_KEY']}/versions/{version_id}"

        except Exception as e:
            logging.exception("Couldn't create Jira version")
            return False
    else:
        return False
