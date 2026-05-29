class TodoItem:
    def __init__(self, id, description):
        self.id = id
        self.description = description
        self.completed = False

class TodoList:
    def __init__(self):
        self.items = []

    def add_item(self, description):
        id = len(self.items) + 1
        item = TodoItem(id, description)
        self.items.append(item)
        print(f"Added item {id}: {description}")

    def view_items(self):
        for item in self.items:
            status = "Completed" if item.completed else "Not completed"
            print(f"{item.id}: {item.description} ({status})")

    def mark_completed(self, id):
        for item in self.items:
            if item.id == id:
                item.completed = True
                print(f"Marked item {id} as completed")
                return
        print(f"Item {id} not found")

    def delete_item(self, id):
        for item in self.items:
            if item.id == id:
                self.items.remove(item)
                print(f"Deleted item {id}")
                return
        print(f"Item {id} not found")

def main():
    todo_list = TodoList()

    while True:
        print("\nOptions:")
        print("1. Add item")
        print("2. View items")
        print("3. Mark completed")
        print("4. Delete item")
        print("5. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            description = input("Enter item description: ")
            todo_list.add_item(description)
        elif choice == "2":
            todo_list.view_items()
        elif choice == "3":
            id = int(input("Enter item ID: "))
            todo_list.mark_completed(id)
        elif choice == "4":
            id = int(input("Enter item ID: "))
            todo_list.delete_item(id)
        elif choice == "5":
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()