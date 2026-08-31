import json
import csv
import openpyxl


def read_json_data(file_path: str):
    
    Reads test data from a JSON file.

    Expected JSON structure:
    [
        {
            "testName": "Valid login",
            "email": "pavanol@gi.com",
            "password": "test@123",
            "expected": "success"
        },
        {
            "testName": "Invalid login",
            "email": "abcxyz@xyz.com",
            "password": "abcxyx",
            "expected": "failure"
        }
    ]

    Returns:
        List of tuples:
        [
            ("Valid login", "pavanol@gi.com", "test@123", "success"),
            ("Invalid login", "abcxyz@xyz.com", "abcxyx", "failure")
        ]
    

    data = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        if not isinstance(json_data, list):
            raise ValueError("JSON file must contain a list of objects")

        for record in json_data:

            if not isinstance(record, dict):
                raise ValueError(
                    f"Each JSON record must be an object/dictionary. "
                    f"Found: {record}"
                )

            data.append(
                (
                    record["testName"],
                    record["email"],
                    record["password"],
                    record["expected"]
                )
            )

    except Exception as e:
        print(f"Error reading JSON file: {e}")
        raise

    return data


def read_csv_data(file_path: str):
    
    Reads test data from a CSV file.
    

    data = []

    try:
        with open(
            file_path,
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                data.append(
                    tuple(row.values())
                )

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise

    return data


def read_excel_data(file_path: str, sheet_name: str = None):
    
    Reads test data from an Excel file.
    

    data = []

    try:
        workbook = openpyxl.load_workbook(file_path)

        sheet = (
            workbook[sheet_name]
            if sheet_name
            else workbook.active
        )

        for row in sheet.iter_rows(
            min_row=2,
            values_only=True
        ):
            data.append(row)

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise

    return data

