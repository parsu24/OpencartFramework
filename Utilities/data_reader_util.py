import json
import csv
import openpyxl


def read_json_data(file_path):
    """
    Reads test data from a JSON file.
    Returns a list of dictionaries.
    """

    # Convert relative path to absolute path
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)

    print(f"Reading JSON file: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"JSON file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"JSON data loaded successfully: {data}")

    return data

def read_csv_data(file_path: str):
    """
    Reads test data from a CSV file and returns a list of tuples.
    CSV file should contain headers: email,password,validity
    """
    data = []
    try:
        file= open(file_path, newline='', encoding='utf-8')
        reader = csv.DictReader(file)
        for row in reader:
            #data.append((row["email"], row["password"], row["validity"]))
            data.append(tuple(row.values()))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return data


def read_excel_data(file_path: str, sheet_name: str = None):
    """
    Reads test data from an Excel file and returns a list of tuples.
    Assumes the first row contains headers (email, password, validity).
    """
    data = []
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook[sheet_name] if sheet_name else workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(row)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
    return data
