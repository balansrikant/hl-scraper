from flask import current_app as app
from flask import request, jsonify

from myinvestments import utility


def __init__(self, name, city):
    self.name = name
    self.city = city


@app.route('/api/1.0/transactions', methods=["GET"])
def get_transactins():
    try:
        result = utility.read_transactions()
        return jsonify(transactions = result)
    except Exception as e:
        return(str(e))