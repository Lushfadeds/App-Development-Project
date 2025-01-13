from flask import Flask, render_template, request, redirect, url_for, flash , session

import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from Inventory import Inventory

app = Flask(__name__)
app.secret_key = 'App_Dev'
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = 'static'
inventory_manager = Inventory()
items = []
print('gf')

Allowed_Extensions = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):  #Split the file from the dot Eg: Image1.png
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_Extensions


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
    price = db.Column(db.Float, nullable=False)  # Added price column


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  # Full name
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)  # Phone number
    role = db.Column(db.String(20), nullable=False)  # Role name, e.g., "staff" or "customer"
    role_id = db.Column(db.Integer, unique=True, nullable=False)  # Incremented role ID

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
            {"name": "Fruit Plus Orange", "stock": 20, "category": "snacks", "image_url": "Fruit_plus_orange.jpg",
             "price": 1.50},
            {"name": "Chocolate Chip", "stock": 0, "category": "snacks", "image_url": "chocolate_chip.jpg",
             "price": 2.00},
            {"name": "Tin Biscuits", "stock": 10, "category": "biscuits", "image_url": "tin_biscuits.jpg",
             "price": 3.50},
            {"name": "Orange Juice", "stock": 15, "category": "beverages", "image_url": "orange_juice.jpg",
             "price": 4.00},
            {"name": "Table Cloth", "stock": 5, "category": "decorations", "image_url": "table_cloth.jpg",
             "price": 10.00},
            {"name": "Paper Plates", "stock": 30, "category": "supplies", "image_url": "plates.jpg", "price": 0.50}
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
    if not User.query.first():
        # Create default staff and customer
        default_staff = User(
            name="Default Staff",
            email="staff@example.com",
            contact_number="1234567890",
            role="staff",
            role_id=1  # First role ID
        )
        default_staff.set_password("staff123")

        default_customer = User(
            name="Default Customer",
            email="customer@example.com",
            contact_number="0987654321",
            role="customer",
            role_id=2  # Second role ID
        )
        default_customer.set_password("customer123")

        db.session.add(default_staff)
        db.session.add(default_customer)
        db.session.commit()

        print("Default staff and customer added to the database.")


@app.route('/')
def home():
    products = [
        {"name": "Fruit Plus Orange", "image_url": "Fruit_plus_orange.jpg"},
        {"name": "Chocolate Chip", "image_url": "chocolate_chip.jpg"},
        {"name": "Tin Biscuits", "image_url": "plates.jpg"}
    ]
    our_story_image = "our_story.jpg"
    motto = "motto.jpg"
    return render_template('home_page.html', products=products, our_story_image=our_story_image, motto=motto)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact_number = request.form['contact_number']
        role = request.form['role']  # "staff" or "customer"

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.')
            return redirect(url_for('register'))

        # Increment the role_id
        max_role_id = db.session.query(db.func.max(User.role_id)).scalar() or 0
        new_role_id = max_role_id + 1

        # Create a new user
        new_user = User(
            name=name,
            email=email,
            contact_number=contact_number,
            role=role,
            role_id=new_role_id
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


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



user_points = 8888


@app.route('/rewards', methods=['GET', 'POST'])
def rewards_page():
    global user_points
    message = None
    if request.method == 'POST':
        reward_id = request.form.get('reward_id')
        reward = Reward.query.get(reward_id)

        if reward and user_points >= reward.points_required:
            user_points -= reward.points_required
            message = f"Successfully redeemed {reward.name}!"
        else:
            message = "You don't have enough points to redeem this reward."

    rewards = Reward.query.all()

    return render_template(
        'rewards.html',
        rewards=rewards,
        user_points=user_points,
        message=message
    )


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
        if "delete" in request.form:
            db.session.delete(item)
            db.session.commit()
            flash(f"Item '{item.name}' has been deleted successfully!", "success")
            return redirect(url_for("inventory_page"))

        # Update item details
        item.stock = int(request.form['stock'])
        price = request.form.get('price')  # Get the price input
        if not price or float(price) <= 0:
            flash('Please provide a valid price greater than 0.')
            return redirect(request.url)
        item.price = float(price)

        if 'image_url' in request.files:
            image = request.files['image_url']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                item.image_url = filename

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for("inventory_page"))

    return render_template("edit_item.html", item=item)

@app.route('/inventory/new', methods=['GET', 'POST'])
def add_new_item():
    if request.method == 'POST':
        name = request.form.get('name')
        stock = request.form.get('stock')
        category = request.form.get('category')
        price = request.form.get('price')  # Use .get() to avoid KeyError
        picture = request.files.get('picture')

        # Validate required fields
        if not name or not stock or not category or not price:
            flash('All fields are required, including price.')
            return redirect(request.url)

        # Validate price
        try:
            price = float(price)
            if price <= 0:
                flash('Price must be greater than 0.')
                return redirect(request.url)
        except ValueError:
            flash('Invalid price value. Please enter a valid number.')
            return redirect(request.url)

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
        new_item = InventoryItem(name=name, stock=int(stock), category=category, image_url=image_url, price=price)
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

@app.route("/shopping", methods=["GET", "POST"])
def shopping_page():
    # Retrieve query parameters
    category = request.args.get("category", "all")  # Default to "all"
    search_query = request.args.get("search", "")
    sort_option = request.args.get("sort", "")
    query = InventoryItem.query

    # Filter by search query
    if search_query:
        query = query.filter(InventoryItem.name.ilike(f"%{search_query}%"))

    # Filter by category (exclude "all" to fetch everything)
    if category and category != "all":
        query = query.filter_by(category=category)

    # Apply sorting options
    if sort_option == "a-z":
        query = query.order_by(InventoryItem.name.asc())
    elif sort_option == "low-high":
        query = query.order_by(InventoryItem.price.asc())
    elif sort_option == "high-low":
        query = query.order_by(InventoryItem.price.desc())

    # Fetch items from the database
    items = query.all()

    # Retrieve cart from session
    cart = session.get("cart", [])
    cart_count = session.get("cart_count", 0)  # Retrieve cart count

    # Precompute max stock for each cart item
    for cart_item in cart:
        item = InventoryItem.query.get(cart_item["item_id"])
        if item:
            cart_item["max_quantity"] = item.stock + cart_item["quantity"]  # Available stock + currently in cart
        else:
            cart_item["max_quantity"] = cart_item["quantity"]  # Fallback to the current quantity

    # Calculate total price
    total_price = sum(cart_item["price"] * cart_item["quantity"] for cart_item in cart) if cart else 0

    # Render the shopping page
    return render_template(
        "shopping_page.html",
        items=items,
        cart=cart,
        total_price=total_price,
        cart_count=cart_count
    )

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item_id = int(request.form.get("item_id"))
    quantity = int(request.form.get("quantity"))

    # Fetch the item from the database
    item = InventoryItem.query.get(item_id)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("shopping_page"))

    # Fetch the cart from session or initialize it
    cart = session.get("cart", [])

    # Get the total quantity of this item in the cart
    current_cart_quantity = sum(cart_item["quantity"] for cart_item in cart if cart_item["item_id"] == item_id)

    # Validate stock availability
    if current_cart_quantity + quantity > item.stock:
        flash(f"Cannot add more than {item.stock} of {item.name} to the cart!", "danger")
        return redirect(url_for("shopping_page"))

    # Check if item is already in the cart
    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            cart_item["quantity"] += quantity
            break
    else:
        # Add a new item to the cart
        cart.append({
            "item_id": item_id,
            "name": item.name,
            "price": item.price,
            "quantity": quantity
        })

    # Update the cart in the session
    session["cart"] = cart
    session["cart_count"] = sum(cart_item["quantity"] for cart_item in cart)  # Update cart count
    session.modified = True

    flash(f"Added {quantity} of {item.name} to cart!", "success")
    return redirect(url_for("shopping_page"))
@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    item_id = int(request.form.get("item_id"))

    # Fetch the cart from the session
    cart = session.get("cart", [])

    # Filter out the item with the given item_id
    updated_cart = [item for item in cart if item["item_id"] != item_id]

    # Update the session
    session["cart"] = updated_cart
    session["cart_count"] = sum(item["quantity"] for item in updated_cart)  # Recalculate cart count
    session.modified = True

    flash("Item removed from the cart!", "success")
    return redirect(url_for("shopping_page"))
@app.route("/update_cart", methods=["POST"])
def update_cart():
    item_id = request.form.get("item_id")
    quantity = request.form.get("quantity")

    # Validate form inputs
    if item_id is None or quantity is None:
        flash("Invalid input. Please try again.", "danger")
        return redirect(url_for("shopping_page"))

    item_id = int(item_id)
    quantity = int(quantity)

    # Fetch the item from the database
    item = InventoryItem.query.get(item_id)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("shopping_page"))

    # Fetch the cart from the session
    cart = session.get("cart", [])

    # Update the quantity in the cart
    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            if quantity == 0:
                cart.remove(cart_item)  # Remove item if quantity is set to 0
            elif quantity <= item.stock:
                cart_item["quantity"] = quantity
            else:
                flash(f"Cannot add more than {item.stock} of {item.name}.", "danger")
                return redirect(url_for("shopping_page"))
            break
    else:
        flash("Item not found in cart.", "danger")
        return redirect(url_for("shopping_page"))

    session["cart"] = cart
    session["cart_count"] = sum(item["quantity"] for item in cart)  # Recalculate cart count
    session.modified = True

    flash("Cart updated successfully.", "success")
    return redirect(url_for("shopping_page"))

if __name__ == '__main__':
    app.run(debug=True)
