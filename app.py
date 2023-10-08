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
import credential
import asyncio
import threading

app = Flask(__name__, static_url_path='/static', static_folder='static')

item_data = []
misc_data = {}
names_array = []
image_processing_complete = False
#SUPPORTING FUNCTIONS

# # Define the asynchronous function to process the image and handle extraction
# async def process_image_and_extraction(file):
#     global item_data,misc_data
#     loop = asyncio.get_event_loop()
#     item_data, misc_data = await loop.run_in_executor(None, extract_receipt_data, file)
#     return item_data, misc_data

# Define a function for processing the image and handling extraction
def process_image_and_extraction(file):
    global item_data, misc_data, image_processing_complete
    #try:
    item_data, misc_data = extract_receipt_data(file)
    #except:
    #print('d')
    image_processing_complete = True  # Set processing status to True upon completion
    return item_data, misc_data

def extract_receipt_data(file):

    a = 1 #varaible to test and not calling API (1 for production)
    if a == 1:
        # Process the binary image data
        image_bytes = file.read()

        # Resize the image if it exceeds 4MB
        max_image_size = 4 * 1024 * 1024  # 4MB
        if len(image_bytes) > max_image_size:
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail((1920, 1920))  # Resize to a maximum of 1920x1920 pixels
            with io.BytesIO() as output:
                image.save(output, format="JPEG")
                image_bytes = output.getvalue()

        # credentials = json.load(open('./credential1.json'))
        # API_KEY = credentials['API_KEY']
        # ENDPOINT = credentials['ENDPOINT']
        API_KEY = credential.API_KEY
        ENDPOINT = credential.ENDPOINT

        form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))
        poller = form_recognizer_client.begin_recognize_receipts(receipt=image_bytes, locale="en-US")
        result = poller.result()
        result = format(result)
        print('AAAA')
        print(result)
        print(type(result))
    else:
        # result = str({"item_data": [{"Name": "TRKY BRGR / NO BUN", "Name_Confidence": 0.872, "Quantity": 1.0, "Quantity_Confidence": 0.936, "TotalPrice": 12.0, "TotalPrice_Confidence": 0.971}, {"Name": "CHCKN POT PIE", "Name_Confidence": 0.908, "Quantity": 1.0, "Quantity_Confidence": 0.936, "TotalPrice": 11.5, "TotalPrice_Confidence": 0.971}, {"Name": "ROAST CHCKN", "Name_Confidence": 0.925, "Quantity": 1.0, "Quantity_Confidence": 0.936, "TotalPrice": 13.5, "TotalPrice_Confidence": 0.971}, {"Name": "SALAD", "Name_Confidence": 0.932, "Quantity": 1.0, "Quantity_Confidence": 0.938, "TotalPrice": 8.95, "TotalPrice_Confidence": 0.971}, {"Name": "BRUSSELS SPROUTS", "Name_Confidence": 0.927, "Quantity": 1.0, "Quantity_Confidence": 0.937, "TotalPrice": 7.95, "TotalPrice_Confidence": 0.971}, {"Name": "ICED TEA", "Name_Confidence": 0.925, "Quantity": 1.0, "Quantity_Confidence": 0.936, "TotalPrice": 3.0, "TotalPrice_Confidence": 0.971}, {"Name": "SODA", "Name_Confidence": 0.933, "Quantity": 1.0, "Quantity_Confidence": 0.938, "TotalPrice": 3.0, "TotalPrice_Confidence": 0.971}, {"Name": "LEMONADE", "Name_Confidence": 0.933, "Quantity": 1.0, "Quantity_Confidence": 0.937, "TotalPrice": 5.0, "TotalPrice_Confidence": 0.971}], "misc_data": {"ReceiptType": "Itemized", "ReceiptType_Confidence": 0.994, "Subtotal": 64.9, "Subtotal_Confidence": 0.983, "Tax": 5.84, "Tax_Confidence": 0.987, "Total": 70.74, "Total_Confidence": 0.982, "TransactionTime": "18:42:00", "TransactionTime_Confidence": 0.985}})
        print(type(result))
        #result = str({'item_data': [{'Name': 'TRKY BRGR / NO BUN', 'Name_Confidence': 0.872, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 12.0, 'TotalPrice_Confidence': 0.971}, {'Name': 'CHCKN POT PIE', 'Name_Confidence': 0.908, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 11.5, 'TotalPrice_Confidence': 0.971}, {'Name': 'ROAST CHCKN', 'Name_Confidence': 0.925, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 13.5, 'TotalPrice_Confidence': 0.971}, {'Name': 'SALAD', 'Name_Confidence': 0.932, 'Quantity': 1.0, 'Quantity_Confidence': 0.938, 'TotalPrice': 8.95, 'TotalPrice_Confidence': 0.971}, {'Name': 'BRUSSELS SPROUTS', 'Name_Confidence': 0.927, 'Quantity': 1.0, 'Quantity_Confidence': 0.937, 'TotalPrice': 7.95, 'TotalPrice_Confidence': 0.971}, {'Name': 'ICED TEA', 'Name_Confidence': 0.925, 'Quantity': 1.0, 'Quantity_Confidence': 0.936, 'TotalPrice': 3.0, 'TotalPrice_Confidence': 0.971}, {'Name': 'SODA', 'Name_Confidence': 0.933, 'Quantity': 1.0, 'Quantity_Confidence': 0.938, 'TotalPrice': 3.0, 'TotalPrice_Confidence': 0.971}, {'Name': 'LEMONADE', 'Name_Confidence': 0.933, 'Quantity': 1.0, 'Quantity_Confidence': 0.937, 'TotalPrice': 5.0, 'TotalPrice_Confidence': 0.971}], 'misc_data': {'ReceiptType': 'Itemized', 'ReceiptType_Confidence': 0.994, 'Subtotal': 64.9, 'Subtotal_Confidence': 0.983, 'Tax': 5.84, 'Tax_Confidence': 0.987, 'Total': 70.74, 'Total_Confidence': 0.982, 'TransactionTime': '18:42:00', 'TransactionTime_Confidence': 0.985}})
        #result = {"item_data": [{"Name": "Blackened Salmon Sandwich", "Name_Confidence": 0.973, "Quantity": 2.0, "Quantity_Confidence": 0.983, "TotalPrice": 42.0, "TotalPrice_Confidence": 0.987}, {"Name": "Chicken Quesadilla", "Name_Confidence": 0.976, "Quantity": 2.0, "Quantity_Confidence": 0.983, "TotalPrice": 30.0, "TotalPrice_Confidence": 0.987}, {"Name": "French Dip", "Name_Confidence": 0.976, "Quantity": 1.0, "Quantity_Confidence": 0.983, "TotalPrice": 22.0, "TotalPrice_Confidence": 0.987}, {"Name": "520 Burger", "Name_Confidence": 0.976, "Quantity": 1.0, "Quantity_Confidence": 0.983, "TotalPrice": 20.0, "TotalPrice_Confidence": 0.987}], "misc_data": {"MerchantAddress": "10146 Main Street Bellevue, WA 98004", "MerchantAddress_Confidence": 0.981, "MerchantName": "520 Bar and Grill", "MerchantName_Confidence": 0.972, "ReceiptType": "Itemized", "ReceiptType_Confidence": 0.99, "Subtotal": 114.0, "Subtotal_Confidence": 0.987, "Tax": 11.52, "Tax_Confidence": 0.988, "Tip": 22.59, "Tip_Confidence": 0.965, "Total": 148.11, "Total_Confidence": 0.72, "TransactionDate": "2023-07-30", "TransactionDate_Confidence": 0.989, "TransactionTime": "21:51:00", "TransactionTime_Confidence": 0.977}}
   

     # Parse the result string into a JSON object
    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        return 'Invalid JSON data', 400
    misc_data = result.get('misc_data', {})
    item_data = result.get('item_data', [])

    updated_item_data = []
    for item in item_data:
        quantity = item.get('Quantity', 1)
        if quantity > 1.0:
            # Calculate the individual price for each item with quantity > 1.0
            individual_price = item['TotalPrice'] / quantity
            for i in range(int(quantity)):
                new_item = {
                    'Name': item['Name'],
                    'Name_Confidence': item['Name_Confidence'],
                    'Quantity': 1.0,
                    'Quantity_Confidence': item['Quantity_Confidence'],
                    'TotalPrice': individual_price,
                    'TotalPrice_Confidence': item['TotalPrice_Confidence']
                }
                updated_item_data.append(new_item)
        else:
            updated_item_data.append(item)

    item_data = updated_item_data

    if 'Tip' not in misc_data.keys() or misc_data['Tip'] == None:
        misc_data['Tip'] = 0.00

    if 'Tax' not in misc_data.keys():
        misc_data['Tax'] = 0.00
    
    # Calculate subtotal_amount
    subtotal_amount = sum(item['TotalPrice'] for item in result['item_data'])
    misc_data['Subtotal2'] = "{:.2f}".format(subtotal_amount)

    # Calculate total_amount (subtotal + tax)
    total_amount = subtotal_amount + misc_data['Tax'] + misc_data['Tip']
    misc_data['Total2'] = "{:.2f}".format(total_amount)

    # Combine the 'Person' input with the item data
    for i, item in enumerate(item_data):
        item['Person'] = ''

    return item_data,misc_data

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


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('1_pre.html')
    return redirect(url_for('pre'))
    
@app.route('/pre', methods=['POST', 'GET'])
def pre():
    return render_template('pre.html')

@app.route('/input', methods=['GET'])
def input_page():
    return render_template('2_input.html')

@app.route('/people', methods=['POST'])
def people():
    return render_template('people.html')

@app.route('/upload', methods=['POST'])
def handle_extraction():
    global item_data, misc_data, image_processing_complete
    if 'file' not in request.files:
        return 'No file part in the request', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    # Start the image processing and extraction in a separate thread
    # thread = threading.Thread(target=process_image_and_extraction, args=(file,))
    # thread.start()
    item_data, misc_data = extract_receipt_data(file)

    # Set processing status to False initially
    image_processing_complete = False

    return render_template('3_people.html')

@app.route('/table', methods=['POST', 'GET'])
def table():
    global item_data, misc_data, names_array, image_processing_complete
    #print (item_data, misc_data, names_array, image_processing_complete)
    
    if request.method == 'POST':
        data = request.json
        names_array = data.get('names', [])
        print(names_array)
    return render_template('4_table_stage.html', item_data=item_data, misc_data=misc_data, names_array=names_array)

@app.route('/save', methods=['POST'])
def save_changes():
    global item_data, misc_data

    if request.method == 'POST':
        # Get the form data sent from the 'editable-cell' cells
        for key, value in request.form.items():
            if key.startswith('person'):
                # Assuming 'person1', 'person2', ... keys represent 'Person' column values
                person_index = int(key.replace('person', '')) - 1
                item_data[person_index]['Person'] = value
            elif key == 'tax':
                # Assuming the 'tax' key represents the 'Tax' cell value
                misc_data['Tax'] = float(value)
            elif key == 'tip':
                # Assuming the 'tip' key represents the 'Tip' cell value
                misc_data['Tip'] = float(value)

        # Perform any other necessary calculations or updates here

        # Redirect back to the table page after saving changes
        # return render_template('table2.html', item_data=item_data, misc_data=misc_data)

        tax = float(misc_data["Tax"])
        tip = float(misc_data.get('Tip', 0))
        bill_total = float(misc_data["Total2"])
        bill_subtotal = float(misc_data["Subtotal2"])
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

if __name__ == '__main__':
    app.run(debug=True)

    ##notes
    #conda create --name your_env_name 
    #conda info --envs
    #conda activate tester
    #python app.py

    #git init
    #git add .
    #git commit -m "frst commit" 
    ##git remote add origin https://github.com/augustochang/rezipt.git (no usar)
    #git push -u origin master
    #git remote remove origin  (no usar)

    #Add to python anywhere
    #git clone https://github.com/augustochang/rezipt.git
    # github, settings, developer settings, tokens classic
    # add credential.py
    #reload