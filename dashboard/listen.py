import time
import db
import gitlab
import applications
from datetime import datetime
from serve import app


def listen(timeout=300):
    with app.app_context():
        while True:
            print(
                f"[{  datetime.now().strftime('%Y-%m-%d %H:%M:%S')    }] Querying for new pipelines"
            )
            pipelines = gitlab.query_pipelines()

            # if first pipeline id is not in database, run the new_pipeline function
            latest_pipeline_id = pipelines[0]["id"].split("/")[-1]
            if not db.get_versions(latest_pipeline_id):

                print(
                    f" * New pipeline detected ({latest_pipeline_id}), capturing versions"
                )

                lb_version = applications.fetch_version(
                    "https://uat.limber.psd.sanger.ac.uk/", ".version-info .container"
                )
                ss_version = applications.fetch_version(
                    "https://uat.sequencescape.psd.sanger.ac.uk/", ".deployment-info"
                )

                db.add_versions(latest_pipeline_id, ss_version, lb_version)

            time.sleep(timeout)


if __name__ == "__main__":
    listen()
