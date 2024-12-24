# Python module imports
import datetime as dt
import hashlib
from flask import Flask, request, render_template, Response

class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode() + str(self.timestamp).encode() + str(self.data).encode() + str(self.prev_hash).encode())
        return sha.hexdigest()


def check_integrity(chain):
    integrity_report = []

    # Iterate through the blockchain
    for i in range(len(chain)):
        if i == 0:
            integrity_report.append(f"Genesis Block (Block {i}) is intact.")
            continue
        # Check the current block's prev_hash against the previous block's hash
        expected_hash = chain[i - 1].hash  # Previous block's hash
        print(f"Block {i}: prev_hash={chain[i].prev_hash}, expected_hash={expected_hash}")
        if chain[i].prev_hash != expected_hash:
            integrity_report.append(f"Block {i} is not intact.")
        else:
            integrity_report.append(f"Block {i} is intact.")

    return integrity_report


def create_genesis_block():
    return [Block(0, dt.datetime.now(), "Genesis Block", "0")]

def find_records(form, blockchain):
    for block in blockchain:
        print(block.data)
        condition = (block.data[0] == form.get("name") and
                    block.data[1] == form.get("date") and
                    block.data[2] == form.get("course") and
                    block.data[3] == form.get("class") and
                    len(block.data[4]) == int(form.get("number")))
        if condition:
            return block.data[4]
    return -1

def next_block(last_block, data):
    this_index = last_block.index + 1
    this_timestamp = dt.datetime.now()
    # A one level deep copy of data has been created since data is modified repeatedly
    # in the calling function and if data is a direct pointer, it leads to modification
    # of old data in the chain.
    this_data = data[:]
    this_prev_hash = last_block.hash
    return Block(this_index, this_timestamp, this_data, this_prev_hash)


def add_block(form, data, blockchain):
    data.append([])
    i = 1
    while form.get("roll_no{}".format(i)):
        data[-1].append(form.get("roll_no{}".format(i)))
        i += 1
    previous_block = blockchain[-1]
    block_to_add = next_block(previous_block, data)
    blockchain.append(block_to_add)
    previous_block = block_to_add
    return "Block #{} has been added to the blockchain!".format(block_to_add.index)



def create_genesis_block():
    return [Block(0, dt.datetime.now(), "Genesis Block", "0")]

# Flask declarations
app = Flask(__name__)
response = Response()
response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')

# Initializing blockchain with the genesis block
blockchain = create_genesis_block()
data = []

# Default Landing page of the app
@app.route('/',  methods = ['GET'])
def index():
    return render_template("index.html")

# Get Form input and decide what is to be done with it
@app.route('/', methods = ['POST'])
def parse_request():
    if(request.form.get("name")):
        while len(data) > 0:
            data.pop()
        data.append(request.form.get("name"))
        data.append(str(dt.date.today()))
        return render_template("class.html",
                                name = request.form.get("name"),
                                date = request.form.get("date", dt.date.today()))

    elif(request.form.get("number")):
        while len(data) > 2:
            data.pop()

        # Update the date in the data list with the selected date from the form
        updated_date = request.form.get("date")
        if updated_date:
            data[1] = updated_date  # Update the date stored at index 1
        data.append(request.form.get("course"))
        data.append(request.form.get("class"))
        return render_template("attendance.html",
                                name = data[0],
                                course = request.form.get("course"),
                                year = request.form.get("year"),
                                number = int(request.form.get("number")))

    elif(request.form.get("roll_no1")):
        while len(data) > 4:
            data.pop()
        return render_template("result.html", result = add_block(request.form, data, blockchain))

    else:
        return "Invalid POST request. This incident has been recorded."

# Show page to get information for fetching records
@app.route('/view.html',  methods = ['GET'])
def view():
    return render_template("class.html")

# Process form input for fetching records from the blockchain
@app.route('/view.html',  methods = ['POST'])
def show_records():
    data = []
    data = find_records(request.form, blockchain)
    if data == -1:
        return "Records not found"
    return render_template("view.html",
                            name = request.form.get("name"),
                            course = request.form.get("course"),
                            year = request.form.get("year"),
                            status = data,
                            number = int(request.form.get("number")),
                            date = request.form.get("date"))

# Show page with result of checking blockchain integrity
@app.route('/integrity_result.html', methods=['GET'])
def check():
    integrity_report = check_integrity(blockchain)
    return render_template("integrity_result.html", result=integrity_report)

# New route to view the entire blockchain
@app.route('/view_blockchain.html', methods=['GET'])
def view_blockchain():
    # Format the blockchain data for display
    blockchain_data = []
    for block in blockchain:
        blockchain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'prev_hash': block.prev_hash,
            'hash': block.hash
        })
    return render_template("view_blockchain.html", blockchain=blockchain_data)


# Start the flask app when program is executed
if __name__ == "__main__":
    app.run()
