from flask import Flask, render_template, request, redirect, url_for, flash , session
from datetime import datetime
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
    'orders': 'sqlite:///orders.db',
    'statistics': 'sqlite:///statistics.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    points_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)


class Stats(db.Model):
    __bind_key__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True)
    products_sold = db.Column(db.Integer, nullable=False)
    daily_sale = db.Column(db.Integer, nullable=False)
    daily_customers = db.Column(db.Integer, nullable=False)
    daily_unique_customers = db.Column(db.Integer, nullable=False)
    money_spent_customer = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()

class InventoryItem(db.Model):
    __bind_key__ = 'inventory'
    __tablename__ = 'inventory_item'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)



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
    customer_name = db.Column(db.String(100), nullable=True)
    customer_email = db.Column(db.String(100), nullable=True)
    customer_contact = db.Column(db.String(15), nullable=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    total = db.Column(db.Float, nullable=True)
    shop_name = db.Column(db.String(100), nullable=True)
    shop_email = db.Column(db.String(100), nullable=True)
    shop_contact = db.Column(db.String(15), nullable=True)
    status = db.Column(db.String(20), default="Pending")




class OrderItem(db.Model):
    __bind_key__ = 'orders'
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    order = db.relationship('Order', backref='order_items')



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




@app.route('/add_graph', methods=['POST'])
def add_graph():
    product = request.form['products_sold']
    sales_today = request.form['sales_today']
    customers_today = request.form['customers_today']
    unique_customers_today = request.form['unique_customers_today']
    money_spent_customer = request.form['money_spent_customer']

    lowest_id = get_lowest_unused_id()

    new_graph = Stats(id=lowest_id,
                      products_sold=product,
                      daily_sale=sales_today,
                      daily_customers=customers_today,
                      daily_unique_customers=unique_customers_today,
                      money_spent_customer=money_spent_customer)
    db.session.add(new_graph)
    db.session.commit()
    flash('Statistics Added Successfully!')
    return redirect(url_for('graph'))


def get_lowest_unused_id():
    existing_ids = [stat.id for stat in Stats.query.with_entities(Stats.id).all()]
    if not existing_ids:
        return 1

    for i in range(1, max(existing_ids) + 2):
        if i not in existing_ids:
            return i

@app.route('/graph')
def graph():
    graph = Stats.query.all()
    for i in graph:
        print(i)
    return render_template('analytics.html', graph_data=graph)

@app.route('/update_analytics/<int:id>', methods=['GET', 'POST'])
def update(id:int):
    stat = Stats.query.get_or_404(id)
    if request.method == "POST":
        stat.products_sold = request.form['products_sold']
        stat.daily_sale = request.form['daily_sale']
        stat.daily_customers = request.form['daily_customers']
        stat.daily_unique_customers = request.form['daily_unique_customers']
        stat.money_spent_customer = request.form['money_spent_customer']

        db.session.commit()
        flash("Analytic updated successfully!", "success")
        return redirect(url_for('graph'))

    graph = Stats.query.all()
    return render_template('update_analytics.html', graph_data=graph, stat=stat)

@app.route('/delete_analytics/<int:id>', methods=['POST'])
def delete(id):
    stat = Stats.query.get_or_404(id)
    db.session.delete(stat)
    db.session.commit()
    flash('Analytic deleted successfully', 'success')

    return redirect(url_for('graph'))


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

    return render_template("staff_order_summary.html", order=order, items=items)

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
    total_price = sum(item['price'] * item['quantity'] for item in cart)

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
            "price": float(item.price) if item.price else 0,
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

# Helper function to validate expiry date
def validate_expiry_date(expiry_date):
    try:
        # Parse expiry date as MM/YY
        exp_month, exp_year = map(int, expiry_date.split('/'))
        current_date = datetime.now()
        expiry_date = datetime(year=2000 + exp_year, month=exp_month, day=1)
        # Ensure the date is valid and in the future
        return expiry_date > current_date
    except (ValueError, IndexError):
        return False
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        flash("Your cart is empty. Add items before proceeding to checkout.", "danger")
        return redirect(url_for('shopping_page'))

    errors = {}  # Initialize an empty errors dictionary

    if request.method == 'POST':
        # Retrieve form data
        card_number = request.form.get('card_number', '')
        expiry_date = request.form.get('expiry_date', '')
        cvc = request.form.get('cvc', '')
        name = request.form.get('name', '')
        date = request.form.get('date', '')
        time = request.form.get('time', '')
        location = request.form.get('location', '')
        comment = request.form.get('comment', '')

        # Validation
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            errors['card_number'] = "Card number must be 16 digits."
        if not expiry_date or not validate_expiry_date(expiry_date):
            errors['expiry_date'] = "Invalid expiry date. Use MM/YY format and ensure it is in the future."
        if not cvc or len(cvc) != 3 or not cvc.isdigit():
            errors['cvc'] = "CVC must be 3 digits."
        if not name.isalpha():
            errors['name'] = "Name must contain only letters."
        if not date or not time or not location:
            errors['order'] = "Order date, time, and location are required."

        # If there are errors, render the template with the errors
        if errors:
            total_cost = sum(item['price'] * item['quantity'] for item in cart)
            return render_template(
                'checkout.html',
                errors=errors,
                card_number=card_number,
                expiry_date=expiry_date,
                cvc=cvc,
                name=name,
                date=date,
                time=time,
                location=location,
                comment=comment,
                items=cart,
                total_cost=total_cost
            )

        # Process Order and Save to Database
        order = Order(
            customer_name=None,  # Placeholder for now
            customer_email=None,
            customer_contact=None,
            date=date,
            time=time,
            location=location,
            comments=comment
        )
        db.session.add(order)
        db.session.commit()

        # Save items to the order
        for cart_item in cart:
            order_item = OrderItem(
                order_id=order.id,
                inventory_item_id=cart_item['item_id'],
                quantity=cart_item['quantity'],
                price=cart_item['price']
            )
            db.session.add(order_item)
        db.session.commit()

        # Clear the cart
        session.pop('cart', None)
        flash("Checkout successful!", "success")
        return redirect(url_for('order_summary', order_id=order.id))

    # Handle GET request
    total_cost = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', items=cart, total_cost=total_cost, errors=errors)


def get_order_details(order_id):
    """
    Retrieve order details, including inventory details for each order item.
    """
    # Fetch the order
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    # Calculate total price and add inventory details
    items_with_inventory = []
    total_price = 0

    for item in order_items:
        inventory_item = InventoryItem.query.get(item.inventory_item_id)
        price = item.price  # Use price stored in OrderItem
        total_cost = item.quantity * price
        total_price += total_cost

        items_with_inventory.append({
            "order_item": item,
            "inventory_name": inventory_item.name if inventory_item else "Unknown Item",
            "total_cost": total_cost,
        })

    return order, items_with_inventory, total_price

@app.route('/order_summary/<int:order_id>')
def order_summary(order_id):
    # Retrieve shared order details
    order, items_with_inventory, total_price = get_order_details(order_id)

    return render_template(
        'order_summary.html',
        order=order,
        items_with_inventory=items_with_inventory,
        total_price=total_price
    )

@app.route("/staff_order_summary/<int:order_id>", methods=["GET"])
def staff_order_summary(order_id):
    # Retrieve shared order details
    order, items_with_inventory, total_price = get_order_details(order_id)

    # Add staff-specific features
    staff_notes = "Confidential staff notes can go here."

    return render_template(
        "staff_order_summary.html",
        order=order,
        items_with_inventory=items_with_inventory,
        total_price=total_price,
        staff_notes=staff_notes  # Pass additional data for staff
    )

@app.route("/order/<int:order_id>/edit_item", methods=["POST"])
def edit_order_item(order_id):
    item_id = request.form.get("item_id")
    new_quantity = request.form.get("new_quantity", None)
    reason = request.form.get("reason")

    if not item_id or not reason:
        flash("Item ID and reason are required.", "danger")
        return redirect(url_for("staff_order_summary", order_id=order_id))

    # Fetch the order item
    order_item = OrderItem.query.get(item_id)
    if not order_item:
        flash("Order item not found.", "danger")
        return redirect(url_for("staff_order_summary", order_id=order_id))

    current_quantity = order_item.quantity

    if new_quantity:
        new_quantity = int(new_quantity)
        if new_quantity > current_quantity:
            flash("New quantity cannot exceed the current quantity.", "danger")
            return redirect(url_for("staff_order_summary", order_id=order_id))
        if new_quantity < 1:
            flash("Quantity must be at least 1.", "danger")
            return redirect(url_for("staff_order_summary", order_id=order_id))

        # Update quantity
        order_item.quantity = new_quantity
    else:
        flash("Invalid quantity provided.", "danger")
        return redirect(url_for("staff_order_summary", order_id=order_id))

    # Commit changes
    db.session.commit()

    flash("Quantity updated successfully.", "success")
    return redirect(url_for("staff_order_summary", order_id=order_id))


if __name__ == '__main__':
    app.run(debug=True)
