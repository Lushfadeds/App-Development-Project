from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from Inventory import Inventory
import sqlite3

app = Flask(__name__)
inventory_manager = Inventory()
items = []

Allowed_Extensions = {'png','jpg','jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Allowed_Extensions

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rewards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    points_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)


with app.app_context():
    db.create_all()



@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/rewards_index')
def rewards_index():
    rewards = Reward.query.all()
    return render_template('rewards_index.html', rewards=rewards)


@app.route('/create_rewards', methods=['GET', 'POST'])
def create_rewards():
    if request.method == 'POST':
        name = request.form['name']
        points_required = request.form['points_required']
        description = request.form['description']
        new_reward = Reward(name=name, points_required=points_required, description=description)
        db.session.add(new_reward)
        db.session.commit()
        return redirect(url_for('rewards_index'))
    return render_template('create_rewards.html')


@app.route('/update_rewards/<int:id>', methods=['GET', 'POST'])
def update_rewards(id):
    reward = Reward.query.get_or_404(id)
    if request.method == 'POST':
        reward.name = request.form['name']
        reward.points_required = request.form['points_required']
        reward.description = request.form['description']
        db.session.commit()
        return redirect(url_for('rewards_index'))
    return render_template('update_rewards.html', reward=reward)


@app.route('/delete_rewards/<int:id>')
def delete_rewards(id):
    reward = Reward.query.get_or_404(id)
    db.session.delete(reward)
    db.session.commit()
    return redirect(url_for('rewards_index'))

rewards = [
    {"id": 1, "name": "$5 voucher", "points_required": 500, "description": None},
    {"id": 2, "name": "$15 voucher", "points_required": 1500, "description": None},
    {"id": 3, "name": "20% voucher", "points_required": 2000, "description": "$60 minimum spend"},
    {"id": 4, "name": "$20 voucher", "points_required": 2000, "description": None},
    {"id": 5, "name": "$2 voucher", "points_required": 200, "description": None},
    {"id": 6, "name": "Free shipping voucher", "points_required": 1350, "description": None}
]

user_points = 8888

inventory = [
        {"id": 1, "name": "Candy", "stock": 20, "category": "snacks" },
        {"id": 2, "name": "Cookies", "stock": 0, "category": "snacks"},
        {"id": 3, "name": "Biscuits", "stock": 10, "category": "biscuits"},
        {"id": 4, "name": "Juice", "stock": 15, "category": "beverages"},
        {"id": 5, "name": "Decorations", "stock": 5, "category": "decorations"},
        {"id": 6, "name": "Plates", "stock": 30, "category": "supplies"}
        ]

@app.route('/rewards', methods=['GET', 'POST'])
def rewards_page():
    global user_points
    message = None
    if request.method == 'POST':
        reward_id = int(request.form.get('reward_id'))
        reward = next((r for r in rewards if r['id'] == reward_id), None)
        if reward:
            if user_points >= reward['points_required']:
                user_points -= reward['points_required']
                message = f"Successfully redeemed {reward['name']}!"
            else:
                message = "Not enough points to redeem this reward."

    return render_template('rewards.html', rewards=rewards, user_points=user_points, message=message)


@app.route("/inventory", methods=["GET"])
def inventory_page():
    category = request.args.get("category", "")
    search_query = request.args.get("search", "")
    filter_option = request.args.get("filter", "")
    inventory_items = inventory_manager.get_items(search_query, filter_option, category)


    return render_template("inventory.html", items=inventory_items)


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return "Item not found", 404

    if request.method == "POST":
        # Update item stock
        new_stock = request.form.get("stock")
        if new_stock.isdigit():
            item["stock"] = int(new_stock)
        return redirect(url_for("inventory_page"))

    return render_template("edit_item.html", item=item)

@app.route('/inventory/new', methods=['GET', 'POST'])
def add_new_item():
    if request.method == 'POST':
        name = request.form['name']
        stock = int(request.form['stock'])
        category = request.form['category']
        expiration_date = request.form['expiration_date']
        remarks = request.form['remarks']
        picture = request.files['picture']

        # Validate file upload
        if picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            picture.save(os.path.join('static/uploads', filename))
        else:
            flash('Invalid file format. Only .jpg, .jpeg, .png allowed.')
            return redirect(request.url)

        # Add item to inventory
        new_item = {
            "id": len(items) + 1,
            "name": name,
            "stock": stock,
            "category": category,
            "expiration_date": expiration_date,
            "remarks": remarks,
            "picture": filename
        }
        items.append(new_item)

        flash('Item successfully added!')
        return redirect(url_for('inventory'))

    return render_template('add_item.html')

if __name__ == '__main__':
    app.run(debug=True)
