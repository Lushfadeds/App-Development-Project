class Inventory:
    count_id = 0

    def __init__(self):
        self.items = [
        {"id": 1, "name": "Candy", "stock": 20, "category": "snacks" },
        {"id": 2, "name": "Cookies", "stock": 0, "category": "snacks"},
        {"id": 3, "name": "Biscuits", "stock": 10, "category": "biscuits"},
        {"id": 4, "name": "Juice", "stock": 15, "category": "beverages"},
        {"id": 5, "name": "Decorations", "stock": 5, "category": "decorations"},
        {"id": 6, "name": "Plates", "stock": 30, "category": "supplies"}
        ]

    def get_items(self, search_query="", filter_option="", category=""):
        filtered_items = self.items

        if search_query:
            filtered_items = [ item for item in filtered_items if search_query.lower() in item["name"].lower()]

        elif filter_option == "low_stock":
            filtered_items = [item for item in filtered_items if item["stock"] < 10]
        elif filter_option == "in_stock":
            filtered_items = [item for item in filtered_items if item["stock"] > 0]
        elif filter_option == "out_of_stock":
            filtered_items = [item for item in filtered_items if item["stock"] == 0]

        if category:
            filtered_items = [item for item in filtered_items if item["category"] == category]

        return filtered_items

    def add_item(self, name, quantity, price):
        Inventory.count_id += 1
        self.items.append({
            "id": Inventory.count_id,
            "name": name,
            "quantity": quantity,
            "price": price
        })

    def remove_item(self, item_id):
        self.items = [item for item in self.items if item['id'] != item_id]

    def update_quantity(self, item_id, quantity):
        for item in self.items:
            if item['id'] == item_id:
                item['quantity'] = quantity
                break