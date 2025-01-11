from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from Inventory import Inventory


app = Flask(__name__)
app.secret_key = 'App_Dev'
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = 'static'
inventory_manager = Inventory()
items = []

Allowed_Extensions = {'png','jpg','jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Allowed_Extensions

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rewards.db'
app.config['SQLALCHEMY_BINDS'] = {
    'inventory': 'sqlite:///inventory.db',
    'orders': 'sqlite:///orders.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    points_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)


with app.app_context():
    db.create_all()

class InventoryItem(db.Model):
    __bind_key__ = 'inventory'  # Specify the database bind key
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)  # Store the path to the uploaded image
class Customer(db.Model):
    __bind_key__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class Order(db.Model):
    __bind_key__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    total = db.Column(db.Float, nullable=False)

    # Add the relationship to OrderItem
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __bind_key__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, nullable=False)  # Reference to InventoryItem
    quantity = db.Column(db.Integer, nullable=False)
    cost_per_item = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    def get_inventory_item(self):
        return InventoryItem.query.filter_by(id=self.inventory_item_id).first()

# Create the database table
with app.app_context():
    db.create_all()

    if not InventoryItem.query.first():
        # Define initial items
        initial_items = [
        {"name": "Fruit Plus Orange", "stock": 20, "category": "snacks", "image_url": "Fruit_plus_orange.jpg"},
        {"name": "Chocolate Chip", "stock": 0, "category": "snacks", "image_url": "chocolate_chip.jpg"},
        {"name": "Tin Biscuits", "stock": 10, "category": "biscuits", "image_url": "tin_biscuits.jpg"},
        {"name": "Orange Juice", "stock": 15, "category": "beverages", "image_url": "orange_juice.jpg"},
        {"name": "Table Cloth", "stock": 5, "category": "decorations", "image_url": "table_cloth.jpg"},
        {"name": "Paper Plates", "stock": 30, "category": "supplies", "image_url": "plates.jpg"}
        ]

        # Insert each item into the database
        for item in initial_items:
            db.session.add(InventoryItem(**item))

        db.session.commit()  # Save the changes to the database
        print("Initial inventory items have been migrated to the database.")

    else:
        print("Existing inventory found in the database.")

    if not Order.query.first():  # Check if orders already exist
        customer = Customer(name="Jane Doe", contact="+65 1234 5678", email="jane.doe@example.com")
        db.session.add(customer)
        db.session.commit()

        order = Order(
            date="2025-01-12",
            time="14:30",
            location="123 Main St, Singapore",
            comments="No peanuts, please.",
            customer_id=customer.id,
            total=30.00
        )
        db.session.add(order)
        db.session.commit()

        order_items = [
            OrderItem(order_id=order.id, inventory_item_id=1, quantity=2, cost_per_item=5.00, total_cost=10.00),
            OrderItem(order_id=order.id, inventory_item_id=2, quantity=4, cost_per_item=5.00, total_cost=20.00),
        ]
        db.session.add_all(order_items)
        db.session.commit()
        print("Mock orders initialized in 'orders.db'.")
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
        flash("Reward created successfully!", "success")
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
        flash("Reward updated successfully!", "success")
        return redirect(url_for('rewards_index'))
    return render_template('update_rewards.html', reward=reward)


@app.route('/delete_rewards/<int:id>')
def delete_rewards(id):
    reward = Reward.query.get_or_404(id)
    db.session.delete(reward)
    db.session.commit()
    flash("Reward Deleted successfully!", "success")
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
    query = InventoryItem.query

    if search_query:
        query = query.filter(InventoryItem.name.ilike(f"%{search_query}%"))
    if category:
        query = query.filter_by(category=category)
    if filter_option == "low_stock":
        query = query.filter(InventoryItem.stock < 10)
    elif filter_option == "in_stock":
        query = query.filter(InventoryItem.stock > 0)
    elif filter_option == "out_of_stock":
        query = query.filter(InventoryItem.stock == 0)

    inventory_items = query.all()
    return render_template("inventory.html", items=inventory_items)


@app.route("/inventory/edit/<int:item_id>", methods=["GET", "POST"])
def edit_inventory_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)

    if request.method == "POST":
        if "delete" in request.form:  # Check if the delete button was clicked
            db.session.delete(item)
            db.session.commit()
            flash(f"Item '{item.name}' has been deleted successfully!", "success")
            return redirect(url_for("inventory_page"))


        # Update item stock and details
        item.stock = int(request.form['stock'])
        if 'image_url' in request.files:
            image = request.files['image_url']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)  # Sanitize filename
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)  # Save the image to the static folder
                item.image_url = f'{filename}'  # Update the item with the new image path

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for("inventory_page"))

    return render_template("edit_item.html", item=item)

@app.route('/inventory/new', methods=['GET', 'POST'])
def add_new_item():
    if request.method == 'POST':
        name = request.form['name']
        stock = int(request.form['stock'])
        category = request.form['category']
        picture = request.files['picture']



        # Validate file upload
        if picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture.save(picture_path)
            image_url = f'{filename}'
        else:
            flash('Invalid file format. Only .jpg, .jpeg, .png allowed.')
            return redirect(request.url)

        # Add item to inventory
        new_item = InventoryItem(name=name, stock=stock, category=category, image_url=image_url)
        db.session.add(new_item)
        db.session.commit()

        flash('Item successfully added!')
        return redirect(url_for('inventory_page'))

    return render_template('add_item.html')

@app.route("/inventory/delete/<int:item_id>", methods=["POST"])
def delete_inventory_item(item_id):
    # Fetch the item from the database
    item = InventoryItem.query.get_or_404(item_id)

    # Delete the item
    db.session.delete(item)
    db.session.commit()

    # Flash a success message
    flash(f"Item '{item.name}' has been deleted successfully!", "success")
    return redirect(url_for("inventory_page"))


@app.route("/order_summary_staff/<int:order_id>", methods=["GET"])
def order_summary_staff(order_id):
    order = Order.query.get_or_404(order_id)

    items = [
        {
            "id": item.id,
            "name": item.get_inventory_item().name if item.get_inventory_item() else "Unknown Item",
            "quantity": item.quantity,
            "cost_per_item": item.cost_per_item,
            "total_cost": item.total_cost,
        }
        for item in order.order_items
    ]

    return render_template("order_summary_staff.html", order=order, items=items)


if __name__ == '__main__':
    app.run(debug=True)


