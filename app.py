from flask import Flask, json, render_template, request, session, url_for, jsonify, flash, redirect, send_file
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import json
import io
from PIL import Image
from datetime import date, time
import tempfile
import csv
from collections import defaultdict

app = Flask(__name__)

item_data = []
misc_data = {}

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect(url_for('pre'))
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route('/pre', methods=['POST', 'GET'])
def pre():
    return render_template('pre.html')

@app.route('/input', methods=['GET'])
def input_page():
    return render_template('input.html')

@app.route('/upload_fake', methods=['POST'])
def handle_extraction_fake():
    global item_data
    global misc_data
    result = {'item_data': [{'Name': 'TRKY BRGR / NO BUN', 'Name_Confidence': 0.872, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 12.0, 'TotalPrice_Confidence': 0.971}, {'Name': 'CHCKN POT PIE', 'Name_Confidence': 0.908, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 11.5, 'TotalPrice_Confidence': 0.971}, {'Name': 'ROAST CHCKN', 'Name_Confidence': 0.925, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 13.5, 'TotalPrice_Confidence': 0.971}, {'Name': 'SALAD', 'Name_Confidence': 0.932, 'Quantity': 1.0, 'Quantity_Confidence': 0.938, 'TotalPrice': 8.95, 'TotalPrice_Confidence': 0.971}, {'Name': 'BRUSSELS SPROUTS', 'Name_Confidence': 0.927, 'Quantity': 1.0, 'Quantity_Confidence': 0.937, 'TotalPrice': 7.95, 'TotalPrice_Confidence': 0.971}, {'Name': 'ICED TEA', 'Name_Confidence': 0.925, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 3.0, 'TotalPrice_Confidence': 0.971}, {'Name': 'SODA', 'Name_Confidence': 0.933, 'Quantity': 1.0, 'Quantity_Confidence': 0.938, 'TotalPrice': 3.0, 'TotalPrice_Confidence': 0.971}, {'Name': 'LEMONADE', 'Name_Confidence': 0.933, 'Quantity': 1.0, 'Quantity_Confidence': 0.937, 'TotalPrice': 5.0, 'TotalPrice_Confidence': 0.971}], 'misc_data': {'ReceiptType': 'Itemized', 'ReceiptType_Confidence': 0.994, 'Subtotal': 64.9, 'Subtotal_Confidence': 0.983, 'Tax': 5.84, 'Tax_Confidence': 0.987, 'Total': 70.74, 'Total_Confidence': 0.982, 'TransactionTime': '18:42:00', 'TransactionTime_Confidence': 0.985}}
    item_data = result.get('item_data', [])
    misc_data = result.get('misc_data', {})
    ######
    # Combine the 'Person' input with the item data
    for i, item in enumerate(item_data):
        item['Person'] = ''
    return render_template('table.html', item_data=item_data, misc_data=misc_data)

@app.route('/save', methods=['POST'])
def process_data():
    global item_data
    global misc_data
    # Get the user input for the 'Person' column
    persons = [request.form.get(f'person{i+1}') for i in range(len(item_data))]
    # Combine the 'Person' input with the item data
    for i, item in enumerate(item_data):
        item['Person'] = persons[i] if i < len(persons) else ''
    
    misc_data['Total'] = request.form.get('total')
    misc_data['Tax'] = request.form.get('tax')
    misc_data['Tip'] = request.form.get('tip')

    return render_template('table2.html', item_data=item_data, misc_data=misc_data)


@app.route('/done', methods=['GET'])
def done():
    global item_data
    global misc_data
    tax = float(misc_data["Tax"])
    tip = float(misc_data.get('Tip', 0))
    bill_total = float(misc_data["Total"])
    bill_subtotal = float(misc_data["Subtotal"])
    sums_by_person = defaultdict(float)
    for item in item_data:
        person = item['Person']
        total_price = item['TotalPrice']
        sums_by_person[person] += total_price
    # Calculate tax and tip per person
    tax_per_person = {}
    tip_per_person = {}
    total_per_person = {}
    for person, person_total in sums_by_person.items():
        tax_per_person[person] = tax * (person_total / bill_subtotal)
        tip_per_person[person] = tip * (person_total / bill_subtotal)
        total_per_person[person] = sums_by_person[person] + tax_per_person[person] + tip_per_person[person]

    return render_template('table3.html', sums_by_person=sums_by_person, tax_per_person=tax_per_person, tip_per_person=tip_per_person, total_per_person=total_per_person)


@app.route('/upload', methods=['POST'])
def handle_extraction():
    global item_data
    global misc_data
    if 'file' not in request.files:
        return 'No file part in the request', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    # Process the binary image data
    image_data = file.read()
    
    # Handle the image data as needed (e.g., perform image processing)
    result = extract_receipt_data(image_data)
    # Parse the result string into a JSON object
    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        return 'Invalid JSON data', 400
    result_ = json.dumps(result, indent=4)
    #print(result_)
    item_data = result.get('item_data', [])
    misc_data = result.get('misc_data', {})
    
    # Combine the 'Person' input with the item data
    for i, item in enumerate(item_data):
        item['Person'] = ''
    return render_template('table.html', item_data=item_data, misc_data=misc_data)

def extract_receipt_data(image_bytes):
    # Resize the image if it exceeds 4MB
    max_image_size = 4 * 1024 * 1024  # 4MB
    if len(image_bytes) > max_image_size:
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail((1920, 1920))  # Resize to a maximum of 1920x1920 pixels
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            image_bytes = output.getvalue()

    credentials = json.load(open('./credential.json'))
    API_KEY = credentials['API_KEY']
    ENDPOINT = credentials['ENDPOINT']
    form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))
    poller = form_recognizer_client.begin_recognize_receipts(receipt=image_bytes, locale="en-US")
    result = poller.result()
    result = format(result)
    return result

def format(result):
    data = []
    my_dict = {}

    for receipt in result:
        for name, field in receipt.fields.items():
            if name == 'Items':
                for indx, item in enumerate(field.value):
                    item_dict = {}
                    for item_name, item_field in item.value.items():
                        item_dict[item_name] = item_field.value
                        item_dict[item_name + '_Confidence'] = item_field.confidence
                    data.append(item_dict)
            else:
                my_dict[name] = field.value
                my_dict[name + '_Confidence'] = field.confidence

    # Merge data and my_dict into a single dictionary
    output = {
        'item_data': data,
        'misc_data': my_dict
    }
    # Return the merged dictionary as a JSON string
    output_json = json.dumps(output, default=serialize)
    return output_json

def serialize(obj):
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


if __name__ == '__main__':
    app.run(debug=True)

    ##notes
    #conda activate tester
    #python app.py
    #git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY