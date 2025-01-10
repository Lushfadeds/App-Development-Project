class Inventory:
    count_id = 6

    def __init__(self):
        self.items = [
        {"id": 1, "name": "Fruit Plus Orange", "stock": 20, "category": "snacks", "image_url": "Fruit_plus_orange.jpg" },
        {"id": 2, "name": "Chocolate Chip", "stock": 0, "category": "snacks", "image_url": "chocolate_chip.jpg"},
        {"id": 3, "name": "Tin Biscuits", "stock": 10, "category": "biscuits","image_url": "tin_biscuits.jpg"},
        {"id": 4, "name": "Orange Juice", "stock": 15, "category": "beverages","image_url": "orange_juice.jpg"},
        {"id": 5, "name": "Table Cloth", "stock": 5, "category": "decorations","image_url": "table_cloth.jpg"},
        {"id": 6, "name": "Paper Plates", "stock": 30, "category": "supplies","image_url": "plates.jpg"}
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

    def add_item(self, name, stock, category, image_url="" ):
        self.count_id += 1
        new_item = ({
            "id": self.count_id,
            "name": name,
            "stock": stock,
            "category": category,
            "image_url": image_url
        })

        self.items.append(new_item)
        return new_item

    def remove_item(self, item_id):
        self.items = [item for item in self.items if item['id'] != item_id]

    def update_quantity(self, item_id, quantity):
        for item in self.items:
            if item['id'] == item_id:
                item['quantity'] = quantity
                break