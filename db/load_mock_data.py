import csv

def load_csv_to_database(conn, csv_file_path):
    """
    Loads sample vehicle data from a CSV file into the Vehicle table.
    """
    try:
        cursor = conn.cursor()

        with open(csv_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                cursor.execute("""
                    INSERT INTO Vehicle (vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['vin'],
                    row['manufacturer_name'],
                    row['description'],
                    int(row['horse_power']),
                    row['model_name'],
                    int(row['model_year']),
                    float(row['purchase_price']),
                    row['fuel_type']
                ))

        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error loading CSV data into the database: {e}")