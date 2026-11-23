
import json
import os
from flask import current_app


def read_data(file_name):

    file_path = os.path.join(
        current_app.config["DATA_DIR"],
        file_name
    )

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def write_data(file_name, data):

    file_path = os.path.join(
        current_app.config["DATA_DIR"],
        file_name
    )

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    temp_path = file_path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    os.replace(temp_path, file_path)


def add_record(file_name, record):

    data = read_data(file_name)

    data.append(record)

    write_data(file_name, data)

    return record


def update_record(file_name, record_id, updated_data):

    data = read_data(file_name)

    for record in data:

        if record.get("id") == record_id:

            record.update(updated_data)

            write_data(file_name, data)

            return True

    return False


def delete_record(file_name, record_id):

    data = read_data(file_name)

    updated_data = [
        record for record in data
        if record.get("id") != record_id
    ]

    if len(data) == len(updated_data):
        return False

    write_data(file_name, updated_data)

    return True
