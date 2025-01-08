class Inventory:
    count_id = 0

    def __init__(self):
        self.items = []

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