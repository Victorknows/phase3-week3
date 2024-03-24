import sqlite3

conn = sqlite3.connect('restaurant_reviews.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                restaurant_id INTEGER,
                customer_id INTEGER,
                star_rating INTEGER,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id))''')

conn.commit()


class Restaurant:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.id = None 


    def reviews(self):
        c.execute("SELECT * FROM reviews WHERE restaurant_id = ?", (self.id,))
        return c.fetchall()

    def customers(self):
        c.execute("SELECT c.* FROM customers c JOIN reviews r ON c.id = r.customer_id WHERE r.restaurant_id = ?", (self.id,))
        return c.fetchall()

    @classmethod
    def fanciest(cls):
        c.execute("SELECT * FROM restaurants ORDER BY price DESC LIMIT 1")
        row = c.fetchone()
        return cls(row[1], row[2])

    def all_reviews(self):
        reviews = self.reviews()
        review_strings = []
        for review in reviews:
            c.execute("SELECT first_name, last_name FROM customers WHERE id = ?", (review[2],))
            customer_name = c.fetchone()
            review_strings.append(f"Review for {self.name} by {customer_name[0]} {customer_name[1]}: {review[3]} stars.")
        return review_strings


class Customer:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def reviews(self):
        c.execute("SELECT * FROM reviews WHERE customer_id = ?", (self.id,))
        return c.fetchall()

    def restaurants(self):
        c.execute("SELECT r.* FROM restaurants r JOIN reviews rev ON r.id = rev.restaurant_id WHERE rev.customer_id = ?", (self.id,))
        return c.fetchall()

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        c.execute("SELECT r.* FROM restaurants r JOIN reviews rev ON r.id = rev.restaurant_id WHERE rev.customer_id = ? ORDER BY rev.star_rating DESC LIMIT 1", (self.id,))
        row = c.fetchone()
        return Restaurant(row[1], row[2])

    def add_review(self, restaurant, rating):
        c.execute("INSERT INTO reviews (restaurant_id, customer_id, star_rating) VALUES (?, ?, ?)", (restaurant.id, self.id, rating))
        conn.commit()

    def delete_reviews(self, restaurant):
        c.execute("DELETE FROM reviews WHERE restaurant_id = ? AND customer_id = ?", (restaurant.id, self.id))
        conn.commit()


class Review:
    def __init__(self, restaurant, customer, star_rating):
        self.restaurant = restaurant
        self.customer = customer
        self.star_rating = star_rating

    def customer(self):
        c.execute("SELECT * FROM customers WHERE id = ?", (self.customer_id,))
        return c.fetchone()

    def restaurant(self):
        c.execute("SELECT * FROM restaurants WHERE id = ?", (self.restaurant_id,))
        return c.fetchone()

    def full_review(self):
        c.execute("SELECT name FROM restaurants WHERE id = ?", (self.restaurant_id,))
        restaurant_name = c.fetchone()[0]
        c.execute("SELECT first_name, last_name FROM customers WHERE id = ?", (self.customer_id,))
        customer_name = c.fetchone()
        return f"Review for {restaurant_name} by {customer_name[0]} {customer_name[1]}: {self.star_rating} stars."


if __name__ == "__main__":
    c1 = Customer("John", "Doe")
    c2 = Customer("Alice", "Smith")

    r1 = Restaurant("Restaurant A", 4)
    r2 = Restaurant("Restaurant B", 3)

    c1.add_review(r1, 5)
    c1.add_review(r2, 4)
    c2.add_review(r1, 3)

    restaurant_a = Restaurant.fanciest()
    print(f"All reviews for {restaurant_a.name}:")
    print(restaurant_a.all_reviews())

    print(f"Customers who reviewed {restaurant_a.name}:")
    print(restaurant_a.customers())

    print(f"All reviews by {c1.full_name()}:")
    for review in c1.reviews():
        print(Review(*review).full_review())

    print(f"{c1.full_name()}'s favorite restaurant is {c1.favorite_restaurant().name}")

    c1.delete_reviews(r1)

    print(f"Reviews by {c1.full_name()} after deletion:")
    print(c1.reviews())

    conn.close()
