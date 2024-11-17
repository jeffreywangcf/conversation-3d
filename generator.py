import yaml

def generate_playbook(selected_devices, output_files, output_file="playbook.yml"):
    if len(selected_devices) != len(output_files):
        raise ValueError("Number of selected devices must match the number of audio files.")

    devices = [{"ip": ip, "file": file} for ip, file in zip(selected_devices, output_files)]

    playbook = [
        {
            "name": "Conversation4D Deployment",
            "hosts": "audio_devices",
            "become": "yes",
            "vars": {
                "ansible_become_pass": "iostream",
                "devices": devices
            },
            "tasks": [
                {
                    "name": "copying audio",
                    "copy": {
                        "src": "output/{{ item.file }}",
                        "dest": "/tmp/play.wav"
                    },
                    "delegate_to": "{{ item.ip }}",
                    "with_items": "{{ devices }}",
                    "vars": {
                        "ansible_user": "jeffreywangcf"
                    }
                },
                {
                    "name": "copy run scripts",
                    "copy": {
                        "src": "play.py",
                        "dest": "/tmp/play.py"
                    },
                    "delegate_to": "{{ item.ip }}",
                    "with_items": "{{ devices }}",
                    "vars": {
                        "ansible_user": "jeffreywangcf"
                    }
                },
                {
                    "name": "sync with other devices",
                    "wait_for": {
                        "path": "/tmp/play.wav",
                        "state": "present",
                        "timeout": 180
                    },
                    "delegate_to": "{{ item.ip }}",
                    "with_items": "{{ devices }}",
                    "vars": {
                        "ansible_user": "jeffreywangcf"
                    }
                },
                {
                    "name": "running scripts",
                    "command": "python3 /tmp/play.py",
                    "delegate_to": "{{ item.ip }}",
                    "with_items": "{{ devices }}",
                    "vars": {
                        "ansible_user": "jeffreywangcf"
                    },
                    "async": 120,
                    "poll": 0
                }
            ]
        }
    ]

    with open(output_file, "w") as file:
        yaml.dump(playbook, file, default_flow_style=False)

    print(f"Playbook saved to {output_file}")
