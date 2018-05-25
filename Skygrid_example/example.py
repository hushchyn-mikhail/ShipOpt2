import time
import json

from disneylandClient import (
    new_client,
    Job,
    RequestWithId,
)

STATUS_IN_PROCESS = set([
    Job.PENDING,
    Job.PULLED,
    Job.RUNNING,
])
STATUS_FINAL = set([
    Job.COMPLETED,
    Job.FAILED,
])

#descriptor = {
#    "descriptor": {
#        "input": [],

#        "container": {
#            "workdir": "",
#            "name": "busybox:latest",
#            "cpu_needed": 1,
#            "max_memoryMB": 1024,
#            "min_memoryMB": 512,
#            "cmd": "sh -lc 'echo 123 > /output/test.txt'",
#        },

#        "required_outputs": {
#            "output_uri": "none:",
#            "file_contents": [
#                {"file": "test.txt", "to_variable": "out"}
#            ]
#        }
#    }
#}

descriptor = {
    "input": [],

    "container": {
        "workdir": "",
        "name": "busybox:latest",
        "cpu_needed": 1,
        "max_memoryMB": 1024,
        "min_memoryMB": 512,
        "cmd": "sh -lc 'echo 123 > /output/test.txt'",
    },

    "required_outputs": {
        "output_uri": "none:",
        "file_contents": [
            {"file": "test.txt", "to_variable": "out"}
        ]
    }
}


def main():
    stub = new_client()

    job = Job(
        input=json.dumps(descriptor),
        kind="docker",
    )

    job = stub.CreateJob(job)
    print("Job", job)

    while True:
        time.sleep(3)
        job = stub.GetJob(RequestWithId(id=job.id))
        print("[{}] Job :\n {}\n".format(time.time(), job))

        if job.status in STATUS_FINAL:
            break

    if job.status == Job.FAILED:
        print("Job failed!")

    print("result:", json.loads(job.output))


if __name__ == '__main__':
    main()
