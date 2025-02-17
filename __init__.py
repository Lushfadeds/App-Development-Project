from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, flash, session
from datetime import datetime
import re
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from Inventory import Inventory
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, date
import random
import json  # ✅ Add this at the top of your script


app = Flask(__name__)
app.secret_key = 'App_Dev'
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = 'static'
inventory_manager = Inventory()
items = []
print("yo")

Allowed_Extensions = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):  # Split the file from the dot Eg: Image1.png
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_Extensions


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_BINDS'] = {
    'inventory': 'sqlite:///inventory.db',
    'orders': 'sqlite:///orders.db',
    'statistics': 'sqlite:///statistics.db',
    'user': 'sqlite:///user.db',
    'rewards': 'sqlite:///rewards.db',
    'feedback': 'sqlite:///feedback.db',
    'replies': 'sqlite:///replies.db',
    'redeemed_rewards': 'sqlite:///redeemed_rewards.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class AnalyticsLayout(db.Model):
    __bind_key__ = 'statistics'  # Using the same database as Stats
    id = db.Column(db.Integer, primary_key=True)
    layout_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<AnalyticsLayout {self.id}>'

    # Define Feedback model


class Feedback(db.Model):
    __bind_key__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    feedback_type = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    replied = db.Column(db.Boolean, default=False)


# Define Reply model
class Reply(db.Model):
    __bind_key__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    reply_message = db.Column(db.Text, nullable=False)
    date_replied = db.Column(db.DateTime, default=datetime.utcnow)


class Reward(db.Model):
    __bind_key__ = 'rewards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    points_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    discount_value = db.Column(db.Float, nullable=False)  # New field to store actual discount

    # the Reward class defines a db model for the rewards table, for a unique id
    # , a required name, the points_required to claim the reward, and an optional description.


class Stats(db.Model):
    __bind_key__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Manually linking to User.id
    day = db.Column(db.Integer, nullable=True)
    products_sold = db.Column(db.Integer, nullable=False)
    daily_sale = db.Column(db.Integer, nullable=False)
    daily_customers = db.Column(db.Integer, nullable=False)
    daily_unique_customers = db.Column(db.Integer, nullable=False)
    money_spent_customer = db.Column(db.Integer, nullable=False)
    expenses = db.Column(db.Integer, nullable=False)
    labor_costs = db.Column(db.Float, nullable=False)
    energy_costs = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Stats(id={self.id}, user_id={self.user_id}, day={self.day}, products_sold={self.products_sold}, daily_sale={self.daily_sale}, daily_customers={self.daily_customers}, daily_unique_customers={self.daily_unique_customers}, money_spent_customer={self.money_spent_customer}, expenses={self.expenses}, labor_costs={self.labor_costs}, energy_costs={self.energy_costs})>"

with app.app_context():
    if not os.path.exists('rewards.db'):
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
    __bind_key__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.Date, nullable=True, default=None)
    streak_data = db.Column(db.Text, default=json.dumps({}))  # ✅ Empty JSON by default
    last_wheel_spin = db.Column(db.Date, nullable=True, default=None)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # hashes the user's password using generate_password_hash and stores it in the password_hash field.

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    # returns True if the password is correct, False otherwise.


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
    discount_applied = db.Column(db.Float, nullable=True, default=0.00)  # New field for discount
    shipping_cost = db.Column(db.Float, nullable=True, default=13.50)  # New field for shipping
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


class RedeemedReward(db.Model):
    __bind_key__ = 'redeemed_rewards'  # Ensure correct DB binding
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Store user ID
    reward_name = db.Column(db.String(100), nullable=False)
    points_used = db.Column(db.Integer, nullable=False, default=0)  # ✅ Add points_used column
    discount_value = db.Column(db.Float, nullable=False, default=0.0)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), default="Unused")  # New field to track usage

# Create the database table
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role='admin').first():
        admin_user = User(
            name='admin',
            email='admin@mamaks.com',
            contact_number='11111111',
            role='admin',
            profile_picture='unknown.png',
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print('Admin has been created')
    else:
        print('Existing Admin Found')

    if not Reward.query.first():
        default_rewards = [
            {"name": "Free Shipping", "points_required": 1350, "description": "Get free shipping on your order.",
             "discount_value": 13.50},
            {"name": "$5 Voucher", "points_required": 500, "description": "Redeem a $5 shopping voucher.",
             "discount_value": 5.00},
            {"name": "20% Discount", "points_required": 2000, "description": "Get 20% off your next order.",
             "discount_value": -1},  # -1 to dynamically calculate 20% later
            {"name": "$20 Voucher", "points_required": 2000, "description": "Redeem a $20 shopping voucher.",
             "discount_value": 20.00},
            {"name": "$2 Voucher", "points_required": 200, "description": "Redeem a $2 shopping voucher.",
             "discount_value": 2.00},
            {"name": "$15 Voucher", "points_required": 1500, "description": "Redeem a $15 shopping voucher.",
             "discount_value": 15.00},
            {"name": "$50 Voucher", "points_required": 1000, "description": "Redeem a $50 shopping voucher.",
             "discount_value": 50.00},
        ]

        # Insert default rewards into the database
        for reward in default_rewards:
            db.session.add(Reward(**reward))

        db.session.commit()
        print("✅ Default rewards added to the rewards database.")
    else:
        print("✅ Rewards database already populated.")
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


@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    return {'userid': user_id}


def create_dash_app(app):
    dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

    # Query the database for days and sales
    with app.app_context():
        stats = Stats.query.all()
        days = [stat.day for stat in stats]
        sales = [stat.daily_sale for stat in stats]

    # Create the DataFrame using the queried data
    data = pd.DataFrame({
        'X': days,  # Day values for the X axis
        'Y': sales,  # Sales values for the Y axis
    })

    data = data.sort_values(by="X")

    # Create the figure for the line graph
    fig = px.line(
        data,
        x='X',
        y='Y',
        labels={'X': 'Days', 'Y': 'Sales'},
    )

    fig.update_layout(height=300)

    # Set the layout for the Dash app
    dash_app.layout = html.Div([
        dcc.Graph(id='line-graph', figure=fig)
    ])

    return dash_app


create_dash_app(app)


@app.route('/save_layout', methods=['POST'])
def save_layout():
    try:
        layout_data = request.json
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

        # Get existing layout or create new one
        layout = AnalyticsLayout.query.filter_by(user_id=user_id).first()
        if not layout:
            layout = AnalyticsLayout(user_id=user_id)

        layout.layout_data = layout_data
        layout.updated_at = datetime.utcnow()

        db.session.add(layout)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Layout saved successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error saving layout: {str(e)}")  # For debugging
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/get_layout', methods=['GET'])
def get_layout():
    try:
        user_id = session.get('user_id')

        if not user_id:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

        # Get latest stats
        latest_stats = Stats.query.order_by(Stats.day.desc()).first()

        # Get saved layout
        layout = AnalyticsLayout.query.filter_by(user_id=user_id).first()

        if layout and layout.layout_data:
            # Update dynamic content in the layout
            layout_data = layout.layout_data
            for row in layout_data:
                for card in row['cards']:
                    if card['type'] == "Today's Earnings":
                        card[
                            'content'] = f'<div class="fw-bold fs-1">${latest_stats.daily_sale if latest_stats else 0}</div>'
                    elif card['type'] == "Products Sold":
                        card[
                            'content'] = f'<div class="fw-bold fs-1">{latest_stats.products_sold if latest_stats else 0}</div>'
                    elif card['type'] == "New Customers":
                        card[
                            'content'] = f'<div class="fw-bold fs-1">{latest_stats.daily_customers if latest_stats else 0}</div>'
                    # Add other dynamic content updates as needed

            return jsonify({'status': 'success', 'layout': layout_data})

        return jsonify({'status': 'success', 'layout': None})
    except Exception as e:
        print(f"Error getting layout: {str(e)}")  # For debugging
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/staff_analytics')
def staff_analytics():
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture
        stats_data = Stats.query.filter_by(user_id=user_id).all()
        max_day_entry = Stats.query.order_by(Stats.day.desc()).first()

        data = [{
            'day': stat.day,
            'products_sold': stat.products_sold,
            'daily_sale': stat.daily_sale,
            'daily_customers': stat.daily_customers,
            'daily_unique_customers': stat.daily_unique_customers,
            'money_spent_customer': stat.money_spent_customer,
            'expenses': stat.expenses,
            'labor_costs': stat.labor_costs,
            'energy_costs': stat.energy_costs
        } for stat in stats_data]

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Provide extremely concise business insights and recommendations in bullet points. Keep responses under 30 words per sentence and under 100 words total. Separate each point with a |"
                    },
                    {
                        "role": "user",
                        "content": f"""Provide 3 brief insights and recommendations about the following business data:
                        - {data}
                        """
                    }
                ]
            })
        )

        response_json = response.json()
        insights = response_json['choices'][0]['message']['content']
        print(insights)
        insights = insights.split('|')

        return render_template('staffanalytics.html', insights=insights, active_page='staffanalytics',
                               user_stats=max_day_entry, profile_picture=profile_picture, userid=user_id)



@app.route('/analytics_add', methods=['POST'])
def add_graph():
    day = request.form['day']
    products_sold = request.form['products_sold']
    daily_sale = request.form['daily_sale']
    daily_customers = request.form['daily_customers']
    daily_unique_customers = request.form['daily_unique_customers']
    money_spent_customer = request.form['money_spent_customer']
    expenses = request.form['expenses']
    labor_costs = request.form['labor_costs']
    energy_costs = request.form['energy_costs']

    # Check if the day already exists in the database
    if Stats.query.filter_by(day=day).first():
        flash("Day already exists. Please use a different day.", "warning")
        return redirect(url_for('analytics'))

    user_id = session['user_id']

    # Create a new Stats entry
    new_stat = Stats(
        day=day,
        user_id = user_id,
        products_sold=products_sold,
        daily_sale=daily_sale,
        daily_customers=daily_customers,
        daily_unique_customers=daily_unique_customers,
        money_spent_customer=money_spent_customer,
        expenses=expenses,
        labor_costs=labor_costs,
        energy_costs=energy_costs
    )

    # Add the new entry to the database and commit
    db.session.add(new_stat)
    db.session.commit()

    # Flash a success message and redirect to the analytics page
    flash('Statistics Added Successfully!', 'success')
    return redirect(url_for('analytics'))


@app.route('/analytics')
def analytics():
    user_id = session['user_id']
    stat = Stats.query.filter_by(user_id=user_id).all()
    print(stat)
    return render_template('analytics.html', i=stat)


@app.route('/update_analytics/<int:id>', methods=['GET', 'POST'])
def update(id: int):
    stat = Stats.query.get_or_404(id)

    if request.method == "POST":
        day = request.form['day']
        products_sold = request.form['products_sold']
        daily_sale = request.form['daily_sale']
        daily_customers = request.form['daily_customers']
        daily_unique_customers = request.form['daily_unique_customers']
        money_spent_customer = request.form['money_spent_customer']
        expenses = request.form['expenses']
        labor_costs = request.form['labor_costs']
        energy_costs = request.form['energy_costs']

        # Check if the day already exists in the database for another record
        if Stats.query.filter(Stats.day == day, Stats.id != id).first():
            flash("Day already exists. Please use a different day.", "error")
            return redirect(url_for('update', id=id))

        # Update the stat entry
        stat.day = day
        stat.products_sold = products_sold
        stat.daily_sale = daily_sale
        stat.daily_customers = daily_customers
        stat.daily_unique_customers = daily_unique_customers
        stat.money_spent_customer = money_spent_customer
        stat.expenses = expenses
        stat.labor_costs = labor_costs
        stat.energy_costs = energy_costs

        # Commit the changes to the database
        db.session.commit()

        # Flash a success message and redirect to the analytics page
        flash("Analytics updated successfully!", "success")
        return redirect(url_for('analytics'))

    return redirect(url_for('analytics'))


@app.route('/delete_analytics/<int:id>', methods=['POST'])
def delete(id):
    stat = Stats.query.get_or_404(id)
    db.session.delete(stat)
    db.session.commit()
    flash('Analytic deleted successfully', 'success')

    return redirect(url_for('analytics'))


@app.route('/aboutus')
def aboutus():
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    return render_template('aboutus.html', profile_picture=profile_picture, userid=user_id)


@app.route('/admin')
def admin():
    if 'role' in session and session['role'] == 'admin':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    print(request.path)
    users = User.query.with_entities(User.id, User.profile_picture, User.name, User.role, User.email, User.contact_number).all()
    return render_template('admin.html', user=users, profile_picture=profile_picture, userid=user_id)


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)

    # Delete all orders associated with this user
    orders = Order.query.filter_by(customer_email=user.email).all()
    for order in orders:
        # Delete order items first to maintain integrity
        OrderItem.query.filter_by(order_id=order.id).delete()
        db.session.delete(order)

    # Delete all redeemed rewards associated with this user
    RedeemedReward.query.filter_by(user_id=user.id).delete()

    # Finally, delete the user
    db.session.delete(user)
    db.session.commit()

    flash('User and all associated orders and rewards have been deleted successfully!', 'success')
    return redirect(url_for('admin'))


@app.route('/admin_edit/<int:id>', methods=['GET', 'POST'])
def admin_edit(id):
    if request.method == 'POST':
        # Retrieve updated data from the form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact_number = request.form['contact_number']
        profile_picture = request.files['profile']
        role = request.form['role']

        user = User.query.get(id)

        # Validate and process data
        if name:
            user.name = name
        if email:
            user.email = email
        if contact_number:
            user.contact_number = contact_number
        if role:
            user.role = role
        if profile_picture:
            # Save the file, generate the file path, and update the user profile picture
            filename = secure_filename(profile_picture.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(filepath)
            user.profile_picture = filename

        # Commit the changes to the database
        user.set_password(password)
        db.session.commit()

        flash('User updated successfully!', 'success')

    return redirect(url_for('admin'))


@app.route('/admin_add', methods=['GET', 'POST'])
def admin_add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact_number = request.form['contact_number']
        profile_picture = request.files['profile']
        role = request.form['role']

        # Secure the filename and save it in the 'pfp' folder
        filename = secure_filename(profile_picture.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture.save(filepath)

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.')
            return redirect(url_for('register'))

        new_id = get_lowest_available_id()

        # Create a new user
        new_user = User(
            id=new_id,
            name=name,
            email=email,
            contact_number=contact_number,
            role=role,
            profile_picture=filename,
        )

        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        flash('Successfully created user!', 'success')
    return redirect(url_for('admin'))


@app.route('/')
def home():
    if 'role' in session:
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture
        user_role = session['role']  # Get role from session

    else:
        user_id = None
        profile_picture = "unknown.png"
        user_role = 'public'

    best_products = [
        {"name": "Fruit Plus Orange", "image_url": "Fruit_plus_orange.jpg"}
    ]
    team = "team.jpg"
    community = "community_event.jpg"
    our_story_image = "our_story.jpg"
    motto = "motto.jpg"
    return render_template('home_page.html', products=best_products, our_story_image=our_story_image, motto=motto, team=team, community=community, profile_picture=profile_picture, userid=user_id, user_role=user_role )


def get_lowest_available_id():
    ids = [user.id for user in User.query.with_entities(User.id).all()]
    max_id = max(ids, default=0)
    return max_id + 1


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact_number = request.form['contact_number']
        profile_picture = request.files['profile']

        # Secure the filename and save it
        filename = secure_filename(profile_picture.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_picture.save(filepath)

        # **Force New Users to Start Fresh**
        session.clear()  # ✅ Clears any old session data

        # **Check if email is already registered**
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.')
            return redirect(url_for('register'))

        # **Create a new user with a fresh streak & login**
        new_user = User(
            name=name,
            email=email,
            contact_number=contact_number,
            role='Customer',
            profile_picture=filename,
            streak=0,  # ✅ Start fresh
            last_login=None,  # ✅ Ensure last login is empty
            streak_data=json.dumps({})  # ✅ Ensure no previous streaks
        )

        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/rewards_index')
def rewards_index():
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    rewards = Reward.query.all()
    return render_template('rewards_index.html', rewards=rewards, active_page='rewards', profile_picture=profile_picture, userid=user_id)


@app.route('/create_rewards', methods=['GET', 'POST'])
def create_rewards():
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    if request.method == 'POST':
        name = request.form['name']
        points_required = request.form['points_required']
        description = request.form['description']
        discount_value = 0
        new_reward = Reward(name=name, points_required=points_required, description=description, discount_value=discount_value)
        db.session.add(new_reward)
        db.session.commit()
        flash("Reward created successfully!", "success")
        return redirect(url_for('rewards_index'))

    return render_template('create_rewards.html', profile_picture=profile_picture, userid=user_id)


@app.route('/update_rewards/<int:id>', methods=['GET', 'POST'])
def update_rewards(id):
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    reward = Reward.query.get_or_404(id)
    if request.method == 'POST':
        reward.name = request.form['name']
        reward.points_required = request.form['points_required']
        reward.description = request.form['description']
        db.session.commit()
        flash("Reward updated successfully!", "success")
        return redirect(url_for('rewards_index'))
    return render_template('update_rewards.html', reward=reward, profile_picture=profile_picture, userid=user_id)


@app.route('/delete_rewards/<int:id>')
def delete_rewards(id):
    reward = Reward.query.get_or_404(id)
    db.session.delete(reward)
    db.session.commit()
    flash("Reward Deleted successfully!", "success")
    return redirect(url_for('rewards_index'))





@app.route('/rewards', methods=['GET', 'POST'])
def rewards_page():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    # ✅ Keep your role check and fetch user details
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture
        actual_user_points = user.points  # ✅ Fetch actual user points
    else:
        user_id = None
        profile_picture = "unknown.png"
        actual_user_points = 0  # Default if no user

    message = None

    if request.method == 'POST':
        reward_id = request.form.get('reward_id')
        reward = Reward.query.get(reward_id)

        if reward and actual_user_points >= reward.points_required:
            user.points -= reward.points_required  # Deduct points
            db.session.commit()  # ✅ Save updated points

            # ✅ Correctly determine discount value
            discount_value = reward.discount_value
            if reward.name == "20% Discount":
                discount_value = -1  # Placeholder for percentage-based discount

            # ✅ Store redeemed reward
            redeemed_reward = RedeemedReward(
                user_id=user_id,
                reward_name=reward.name,
                points_used=reward.points_required,
                discount_value=discount_value,
                status="Unused"
            )
            db.session.add(redeemed_reward)
            db.session.commit()

            message = f"Successfully redeemed {reward.name}! Apply the discount at checkout."
        else:
            message = "You don't have enough points to redeem this reward."

    rewards = Reward.query.all()

    return render_template(
        'rewards.html',
        rewards=rewards,
        user_points=actual_user_points,  # ✅ Use actual user points
        message=message,
        profile_picture=profile_picture,
        userid=user_id
    )



@app.route("/inventory", methods=["GET"])
def inventory_page():
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    category = request.args.get("category", "all")
    search_query = request.args.get("search", "")
    filter_option = request.args.get("filter", "")
    query = InventoryItem.query

    if search_query:
        query = query.filter(InventoryItem.name.ilike(f"%{search_query}%"))
    if category and category != "all":
        query = query.filter_by(category=category)
    if filter_option == "low_stock":
        query = query.filter(InventoryItem.stock < 10)
    elif filter_option == "in_stock":
        query = query.filter(InventoryItem.stock > 0)
    elif filter_option == "out_of_stock":
        query = query.filter(InventoryItem.stock == 0)

    inventory_items = query.all()
    return render_template("inventory.html", items=inventory_items, profile_picture=profile_picture, userid=user_id)


@app.route("/inventory/edit/<int:item_id>", methods=["GET", "POST"])
def edit_inventory_item(item_id):
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    item = InventoryItem.query.get_or_404(item_id)

    if request.method == "POST":
        if "delete" in request.form:
            db.session.delete(item)
            db.session.commit()
            flash(f"Item '{item.name}' has been deleted successfully!")
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
        flash('Item updated successfully!')
        return redirect(url_for("inventory_page"))

    return render_template("edit_item.html", item=item, profile_picture=profile_picture, userid=user_id)


@app.route('/inventory/new', methods=['GET', 'POST'])
def add_new_item():
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

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

    return render_template('add_item.html', profile_picture=profile_picture, userid=user_id)


@app.route("/shopping", methods=["GET"])
def shopping_page():
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    # Redirect staff users to staff dashboard
    if 'role' in session and session['role'] == 'staff':
        flash("Staff members cannot access the shopping page.", "warning")
        return redirect(url_for("staff_dashboard"))

    # Retrieve query parameters
    category = request.args.get("category", "all")
    search_query = request.args.get("search", "")
    sort_option = request.args.get("sort", "")

    # Query for inventory items while filtering out out-of-stock items
    query = InventoryItem.query.filter(InventoryItem.stock > 0)  # Exclude items with 0 stock

    # Apply search filter
    if search_query:
        query = query.filter(InventoryItem.name.ilike(f"%{search_query}%"))

    # Apply category filter
    if category and category != "all":
        query = query.filter_by(category=category)

    # Apply sorting options
    if sort_option == "a-z":
        query = query.order_by(InventoryItem.name.asc())
    elif sort_option == "low-high":
        query = query.order_by(InventoryItem.price.asc())
    elif sort_option == "high-low":
        query = query.order_by(InventoryItem.price.desc())

    # Fetch available items (only those with stock > 0)
    items = query.all()

    # Retrieve cart details
    cart = session.get("cart", [])
    cart_count = sum(item["quantity"] for item in cart)
    total_price = sum(item["price"] * item["quantity"] for item in cart)

    return render_template(
        "shopping_page.html",
        items=items,  # Only in-stock items are displayed
        cart=cart,
        cart_count=cart_count,
        total_price=total_price,
        profile_picture=profile_picture,
        userid=user_id    )


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
    if 'role' not in session or session['role'] != 'Customer':
        flash("Please create an account.", "danger")
        return redirect(url_for('staff_dashboard'))

    user_id = session['user_id']
    cart = session.get('cart', [])

    if not cart:
        flash("Your cart is empty. Add items before proceeding to checkout.")
        return redirect(url_for('shopping_page'))

    total_cost = sum(item['price'] * item['quantity'] for item in cart)
    shipping_cost = 13.50
    final_total = total_cost + shipping_cost  # Initial total

    # ✅ Fetch all unused rewards for the dropdown
    unused_rewards = RedeemedReward.query.filter_by(user_id=user_id, status="Unused").all()

    # ✅ Get selected reward
    selected_reward_id = request.form.get('reward_id', session.get('applied_reward'))
    selected_reward = None
    discount_amount = 0

    if selected_reward_id:
        selected_reward = RedeemedReward.query.get(int(selected_reward_id))
        if selected_reward and selected_reward.user_id == user_id and selected_reward.status == "Unused":
            if selected_reward.discount_value == -1:
                discount_amount = total_cost * 0.2
            else:
                discount_amount = selected_reward.discount_value

            final_total = max(final_total - discount_amount, 0)  # Ensure total isn't negative
            session['applied_reward'] = selected_reward.id
            session['applied_discount'] = discount_amount  # Store correct discount value
        else:
            session.pop('applied_reward', None)
            session.pop('applied_discount', None)

    errors = {}

    if request.method == 'POST':
        card_number = request.form.get('card_number', '')
        expiry_date = request.form.get('expiry_date', '')
        cvc = request.form.get('cvc', '')
        name = request.form.get('name', '')
        date = request.form.get('date', '')
        time = request.form.get('time', '')
        location = request.form.get('location', '')
        comment = request.form.get('comment', '')

        if not card_number.isdigit() or len(card_number) != 16:
            errors['card_number'] = "Card number must be 16 digits."
        if not expiry_date or not validate_expiry_date(expiry_date):
            errors['expiry_date'] = "Invalid expiry date."
        if not cvc.isdigit() or len(cvc) != 3:
            errors['cvc'] = "CVC must be 3 digits."
        if not name.replace(" ", "").isalpha():
            errors['name'] = "Name must contain only letters."
        if not date or not time or not location:
            errors['order'] = "Order date, time, and location are required."

        if errors:
            return render_template('checkout.html', errors=errors,
                                   card_number=card_number, expiry_date=expiry_date, cvc=cvc,
                                   name=name, date=date, time=time, location=location, comment=comment,
                                   items=cart, total_cost=total_cost, shipping_cost=shipping_cost,
                                   final_total=final_total, unused_rewards=unused_rewards,
                                   selected_reward_id=selected_reward_id, selected_reward=selected_reward)

        user = User.query.get(user_id)
        if not user:
            flash("User not found. Please log in again.", "danger")
            return redirect(url_for('login'))

        # ✅ Store final order details
        order = Order(
            customer_name=user.name,
            customer_email=user.email,
            customer_contact=user.contact_number,
            date=date,
            time=time,
            location=location,
            comments=comment,
            total=final_total,
            discount_applied=discount_amount,  # Store discount amount
            shipping_cost=shipping_cost  # Store shipping cost

        )
        db.session.add(order)
        db.session.commit()

        # ✅ Deduct stock for purchased items
        for cart_item in cart:
            db.session.add(OrderItem(order_id=order.id, inventory_item_id=cart_item['item_id'],
                                     quantity=cart_item['quantity'], price=cart_item['price']))
            inventory_item = InventoryItem.query.get(cart_item['item_id'])
            if inventory_item:
                inventory_item.stock = max(inventory_item.stock - cart_item['quantity'], 0)

        # ✅ Mark reward as used
        if selected_reward:
            selected_reward.status = "Used"
            db.session.commit()

        db.session.commit()
        session.pop('cart', None)
        flash("Checkout successful!", "success")
        return redirect(url_for('order_summary', order_id=order.id))

    return render_template('checkout.html', items=cart, total_cost=total_cost,
                           shipping_cost=shipping_cost, final_total=final_total,
                           unused_rewards=unused_rewards, selected_reward_id=selected_reward_id,
                           selected_reward=selected_reward)


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
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    # Retrieve shared order details
    order, items_with_inventory, total_price = get_order_details(order_id)

    return render_template(
        'order_summary.html',
        order=order,
        items_with_inventory=items_with_inventory,
        total_price=total_price,
        profile_picture=profile_picture,
        userid=user_id
    )


@app.route("/staff_order_summary/<int:order_id>", methods=["GET"])
def staff_order_summary(order_id):
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    # Retrieve shared order details
    order, items_with_inventory, total_price = get_order_details(order_id)

    # Add staff-specific features
    staff_notes = "Confidential staff notes can go here."

    return render_template(
        "staff_order_summary.html",
        order=order,
        items_with_inventory=items_with_inventory,
        total_price=total_price,
        staff_notes=staff_notes,  # Pass additional data for staff
        profile_picture=profile_picture,
        userid=user_id
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

    # Check if new_quantity was provided and validate
    if new_quantity is not None:
        new_quantity = int(new_quantity)

        # Allow the quantity to be set to 0 (zero)
        if new_quantity < 0:
            flash("Quantity cannot be less than 0.", "danger")
            return redirect(url_for("staff_order_summary", order_id=order_id))

        # Update the quantity, increase or decrease based on new value
        order_item.quantity = new_quantity

        # Optionally handle logic for when quantity is set to 0 (e.g., mark as deleted or grayed out)
        if new_quantity == 0:
            order_item.status = "Removed"  # Optionally mark as 'Removed'
            flash("Item quantity set to 0 and marked as removed.", "success")
        else:
            flash("Quantity updated successfully.", "success")

        db.session.commit()
    else:
        flash("Invalid quantity provided.", "danger")
        return redirect(url_for("staff_order_summary", order_id=order_id))

    return redirect(url_for("staff_order_summary", order_id=order_id))


@app.route('/staff_dashboard')
def staff_dashboard():
    if 'role' in session and session['role'] == 'staff':
        userid = session['user_id']
        user = User.query.get_or_404(userid)
        name = user.name
        filename = user.profile_picture

        # ✅ Fetch pending orders count dynamically
        pending_orders_count = Order.query.filter_by(status="Pending").count()

        # ✅ Fetch accepted orders for display
        accepted_orders = Order.query.filter(Order.status == "Accepted").all()

        # ✅ Fetch revenue and low-stock items
        event_revenue = 784  # Placeholder, replace with dynamic value if needed
        low_stock_items = InventoryItem.query.filter(InventoryItem.stock < 10).count()

        return render_template(
            'staff_dashboard.html',
            accepted_orders=accepted_orders,
            pending_orders_count=pending_orders_count,  # ✅ Pass dynamic count
            notifications=pending_orders_count,  # ✅ Notifications = pending orders count
            event_revenue=event_revenue,
            low_stock_items=low_stock_items,
            name=name,
            profile_picture=filename
        )
    else:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

@app.route('/customer_account')
def customer_account():
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)

        # ✅ Fetch actual user points
        actual_user_points = user.points

        # ✅ Fetch only pending orders for this customer
        pending_orders = Order.query.filter_by(customer_email=user.email).all()

        # ✅ Fetch only unused rewards
        redeemed_rewards = RedeemedReward.query.filter_by(user_id=user_id, status="Unused").all()

        return render_template(
            'customer_account.html',
            profile_picture=user.profile_picture,
            name=user.name,
            user_points=actual_user_points,  # ✅ Use actual points instead of static value
            redeemed_rewards=redeemed_rewards,
            pending_orders=pending_orders
        )
    else:
        flash('Please log in to access your account.', 'warning')
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in
    if 'role' in session:
        if session['role'] == 'staff':
            return redirect(url_for('staff_dashboard'))  # Redirect to staffdashboard if the user is logged in as staff
        elif session['role'] == 'Customer':
            return redirect(url_for('customer_account'))  # Redirect to customeraccount if the user is logged in as customer
        elif session['role'] == 'admin':
            return redirect(url_for('admin'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Set session variables
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email  # Ensure this is set

            # Redirect based on role
            if user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            elif user.role == 'Customer':
                return redirect(url_for('customer_account'))
            elif user.role == 'admin':
                return redirect(url_for('admin'))
        else:
            session.clear()
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()  # This will remove all session data

    # Flash message (optional)
    flash("You have been logged out successfully.", "success")

    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/forgot_password')
def forgot_password():
    # Implement forgot password logic here
    return 'Forgot Password Page...'


def is_valid_email(email):
    if "@" in email and "." in email.split("@")[-1]:
        return True
    return False


@app.route('/contact_us')
def contact_us_page():
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture
    else:
        user_id = None
        profile_picture = "unknown.png"

    return render_template('contact_us.html', profile_picture=profile_picture, userid=user_id)


@app.route('/submit_contact_us', methods=['POST'])
def submit_contact_us():
    if 'role' in session and session['role'] == 'Customer':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    feedback_type = request.form.get('feedback_type')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not feedback_type:
        flash('Please select a feedback type.', 'danger')
    elif not full_name or len(full_name) < 3:
        flash('Full name must be at least 3 characters long.', 'danger')
    elif not email or not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
    elif not message or len(message) < 10:
        flash('Message must be at least 10 characters long.', 'danger')
    else:
        # Save feedback to the database
        feedback = Feedback(
            feedback_type=feedback_type,
            full_name=full_name,
            email=email,
            message=message,
            replied=False
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect('/contact_us')

    return redirect('/contact_us', profile_picture=profile_picture, userid=user_id)
# Route to view feedback and replies
@app.route('/contact_us_data')
def contact_us_data():
    if 'role' in session and session['role'] == 'staff':
        user_id = session['user_id']
        user = User.query.get_or_404(user_id)
        profile_picture = user.profile_picture

    else:
        user_id = None
        profile_picture = "unknown.png"

    feedback_list = Feedback.query.all()
    reply_list = Reply.query.all()
    return render_template('contact_us_data.html', feedback_list=feedback_list, reply_list=reply_list, profile_picture=profile_picture, userid=user_id)

# Route to reply to feedback
@app.route('/reply_to_feedback', methods=['POST'])
def reply_to_feedback():
    email = request.form.get('email')
    reply_message = request.form.get('reply_message')

    # Update the feedback to mark it as replied
    feedback = Feedback.query.filter_by(email=email, replied=False).first()
    if feedback:
        feedback.replied = True
        db.session.add(feedback)
        db.session.commit()

        # Save the reply to the database
        reply = Reply(email=email, reply_message=reply_message)
        db.session.add(reply)
        db.session.commit()
        flash('Reply sent successfully!', 'success')

    return redirect('/contact_us_data')


@app.route('/points_system')
def points_system():
    if 'user_id' not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for('login'))

    # ✅ Fetch user details
    user = User.query.get(session['user_id'])
    if not user or user.role.lower() != "customer":
        flash("Only customers can access this page.", "danger")
        return redirect(url_for('customer_account' if user.role == "customer" else 'staff_dashboard'))

    # ✅ Fetch actual user points & streak
    actual_user_points = user.points
    actual_streak = user.streak

    # ✅ Profile Picture Handling
    profile_picture = user.profile_picture if user.profile_picture else "unknown.png"

    return render_template(
        'points_system.html',
        points=actual_user_points,  # ✅ Use actual points from the database
        streak=actual_streak,  # ✅ Use actual streak from the database
        profile_picture=profile_picture,
        userid=user.id
    )


@app.route('/spin', methods=['POST'])
def spin():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized - Please log in'}), 403

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.role != 'Customer':
        return jsonify({'error': 'Only Customers can spin the wheel'}), 403

    today = datetime.utcnow().date()

    # ✅ Ensure the spin does NOT reset the streak
    if user.last_wheel_spin == today:
        return jsonify({'error': 'You have already spun the wheel today!', 'points': user.points})

    # ✅ Generate a random point reward
    outcomes = [2, 3, 5, 10, 0]
    result = random.choice(outcomes)

    # ✅ Update only the points, NOT the streak
    user.points += result
    user.last_wheel_spin = today  # ✅ Store the last spin date separately
    db.session.commit()

    return jsonify({
        'message': f'You won {result} points!',
        'result': result,
        'points': user.points
    })


@app.route('/download_receipt/<int:order_id>')
def download_receipt(order_id):
    # Generate receipt (this can be a PDF or text file)
    receipt_file = generate_receipt(order_id)

    # Send the receipt file for download
    return send_file(receipt_file, as_attachment=True)


def generate_receipt(order_id):
    # Retrieve the order details
    order = Order.query.get_or_404(order_id)

    # Retrieve the items in the order, including inventory details
    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    # Calculate total price and prepare the receipt content
    receipt_content = f"Receipt for Order {order_id}\n\n"
    receipt_content += f"Date: {order.date}\n"
    receipt_content += f"Time: {order.time}\n"
    receipt_content += f"Location: {order.location}\n"
    receipt_content += "\nItems Ordered:\n"

    total_price = 0  # Initialize total price

    # Loop through each order item and fetch the associated inventory item
    for item in order_items:
        inventory_item = InventoryItem.query.get(item.inventory_item_id)
        if inventory_item:
            item_total_cost = item.quantity * item.price
            total_price += item_total_cost  # Add to the total cost

            # Add item details to the receipt content
            receipt_content += f"{inventory_item.name} - {item.quantity} x ${item.price:.2f} = ${item_total_cost:.2f}\n"
        else:
            receipt_content += f"Unknown Item - {item.quantity} x ${item.price:.2f} = ${item.quantity * item.price:.2f}\n"

    # Add Shipping Cost
    receipt_content += f"\nShipping Cost: ${order.shipping_cost:.2f}\n"

    # Add Discount Applied
    discount_applied = order.discount_applied if order.discount_applied else 0
    receipt_content += f"Discount Applied: -${discount_applied:.2f}\n"

    # Calculate Final Total
    final_total = total_price + order.shipping_cost - discount_applied
    receipt_content += f"\nFinal Total (After Shipping & Discount): ${final_total:.2f}"

    # Save the receipt content to a text file
    receipt_file = f"receipt_{order_id}.txt"
    with open(receipt_file, 'w') as f:
        f.write(receipt_content)

    return receipt_file


@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    # Check if the user is logged in and has a 'staff' role
    if 'role' not in session or session['role'] != 'staff':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))

    # Fetch all orders with status 'Pending' for staff to accept
    pending_orders = Order.query.filter_by(status="Pending").all()

    return render_template('notifications.html', orders=pending_orders)


@app.route('/accept_order/<int:order_id>', methods=['POST'])
def accept_order(order_id):
    # Fetch the order from the database
    order = Order.query.get_or_404(order_id)

    # Fetch the staff member's details from the session
    staff_user = User.query.get(session.get('user_id'))  # Get the staff member by their session ID

    if not staff_user or staff_user.role != 'staff':
        flash("You are not authorized to accept orders.", 'danger')
        return redirect(url_for('notifications'))

    # Update the order status to "Accepted"
    order.status = "Accepted"

    # Assign the shop details from the staff user to the order
    order.shop_name = staff_user.name  # Assuming the staff member's name is used as the shop name
    order.shop_email = staff_user.email
    order.shop_contact = staff_user.contact_number  # Assuming contact_number is the shop contact

    db.session.commit()  # Save the changes to the database

    flash(f"Order {order.id} has been accepted!", 'success')
    return redirect(url_for('notifications'))  # Redirect to the notifications page


@app.route('/view_order_details/<int:order_id>', methods=['GET'])
def view_order_details(order_id):
    order = Order.query.get_or_404(order_id)

    # Retrieve the items for the order, including inventory details
    items_with_inventory = []
    total_price = 0
    for item in order.order_items:
        inventory_item = InventoryItem.query.get(item.inventory_item_id)
        total_cost = item.quantity * item.price
        total_price += total_cost

        items_with_inventory.append({
            "order_item": item,
            "inventory_name": inventory_item.name if inventory_item else "Unknown Item",
            "total_cost": total_cost,
        })

    return render_template('order_details.html', order=order, items=items_with_inventory, total_price=total_price)


@app.route('/use_reward/<int:reward_id>', methods=['POST'])
def use_reward(reward_id):
    if 'user_id' not in session:
        flash("Please log in to use a reward.", "danger")
        return redirect(url_for('login'))

    reward = RedeemedReward.query.filter_by(id=reward_id, user_id=session['user_id'], status="Unused").first()

    if not reward:
        flash("Invalid or already used reward.", "danger")
        return redirect(url_for('customer_account'))

    # ✅ Store the correct discount amount in session
    session['applied_reward'] = reward.id

    if "20% Discount" in reward.reward_name:
        session['applied_discount'] = -1  # Placeholder (this will be calculated dynamically in checkout)
    else:
        session['applied_discount'] = reward.discount_value  # ✅ Use `discount_value`, not `points_used`

    flash(f"{reward.reward_name} applied! Discount of ${session['applied_discount']} will be deducted at checkout.",
          "success")
    return redirect(url_for('checkout'))


@app.route('/collect_points', methods=['POST'])
def collect_points():
    if 'user_id' not in session:
        print("❌ User not logged in.")
        return jsonify({'error': 'User not logged in'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        print("❌ User not found.")
        return jsonify({'error': 'User not found'}), 404

    today = datetime.utcnow().date()
    today_name = today.strftime('%A')

    # Load user's existing streak data
    streak_data = json.loads(user.streak_data) if user.streak_data else {}

    # **Check if the user already collected points today**
    if today_name in streak_data:
        print(f"⚠️ {user.name} already collected points today.")
        return jsonify({'error': 'Points already collected today'}), 400

    # **NEW: Handle Streak Logic Correctly**
    days_since_last_login = (today - user.last_login).days if user.last_login else None

    if user.last_login is None:
        print(f"✅ First-time login for {user.name}. Setting streak to 1.")
        user.streak = 1  # ✅ Ensure streak starts at 1
    elif days_since_last_login == 1:
        # ✅ Increase streak if logged in the next day
        user.streak += 1
    elif days_since_last_login > 1:
        # ✅ Reset streak if a day is missed
        user.streak = 1
        streak_data = {}  # Clear past streak data

    # ✅ If a new week starts, reset the streak
    if 'Sunday' in streak_data and today_name == 'Monday':
        streak_data = {}
        user.streak = 1

    # ✅ Calculate Points Earned Based on Streak
    points_earned = min(user.streak * 10, 100)  # ✅ Cap at 100 points per day
    user.points += points_earned

    # ✅ Mark Today as Collected
    streak_data[today_name] = True
    user.streak_data = json.dumps(streak_data)

    # ✅ Update Last Login & Ensure Streak is Saved
    user.last_login = today

    try:
        db.session.commit()  # ✅ Force database update
        print(f"✅ Streak Updated for {user.name}: {user.streak}, Last Login: {user.last_login}, Points Earned: {points_earned}, Total Points: {user.points}")
    except Exception as e:
        db.session.rollback()  # ❌ Rollback in case of failure
        print(f"❌ Error updating streak: {e}")

    return jsonify({
        'points': user.points,
        'streak': user.streak,
        'message': f'+{points_earned} points',
        'streakData': streak_data
    })


@app.route('/get_user_data')
def get_user_data():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    today = datetime.utcnow().date()
    is_new_user = False  # ✅ Flag to track first login
    spun_today = user.last_wheel_spin == today  # ✅ Check if user spun the wheel today

    # ✅ First-Time User: Award 500 Points
    if user.last_login is None:
        print(f"🎉 First-Time User Detected: {user.name} - Awarding 500 Points!")
        user.streak = 1  # ✅ Start fresh streak
        user.points += 500  # ✅ Award 500 points
        user.streak_data = json.dumps({})  # ✅ Reset streak data
        is_new_user = True  # ✅ Mark user as new

    # ✅ Load existing streak data
    streak_data = json.loads(user.streak_data) if user.streak_data else {}

    today_name = today.strftime('%A')

    # ✅ Do NOT auto-assign streak data here!
    # (We only update this when `collect_points` is pressed)

    # ✅ Reset streak if over 7 days
    if user.last_login and (today - user.last_login).days > 7:
        user.streak = 1  # Reset streak
        streak_data = {}  # Clear past streaks

    # ✅ Reset streak on Monday if Sunday was collected
    if 'Sunday' in streak_data and today_name == 'Monday':
        streak_data = {}

    # ✅ Only update last login date (DO NOT modify streak here)
    if user.last_login != today:
        user.last_login = today
        db.session.commit()

    print(f"DEBUG: User {user.name} - Points: {user.points}, Streak: {user.streak}, Spun Today: {spun_today}")

    return jsonify({
        'points': user.points,
        'streak': user.streak,
        'streakData': streak_data,  # ✅ Does NOT pre-mark today's streak
        'newUser': is_new_user,
        'spunToday': spun_today
    })
@app.route('/complete_order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    # Ensure the user is a staff member
    if 'role' not in session or session['role'] != 'staff':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    # Retrieve the order from the database
    order = Order.query.get_or_404(order_id)

    # Ensure the order is in the 'Accepted' state
    if order.status != 'Accepted':
        flash("Only accepted orders can be completed.", "warning")
        return redirect(url_for('staff_dashboard'))

    # Update the order status to 'Completed'
    order.status = 'Completed'
    db.session.commit()

    flash(f"Order {order.id} has been marked as completed!", "success")
    return redirect(url_for('staff_dashboard'))  # Redirect back to staff dashboard

if __name__ == '__main__':
    app.run(debug=True)
