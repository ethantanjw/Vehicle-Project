-- Create the Vehicle table
CREATE TABLE IF NOT EXISTS Vehicle (
    vin VARCHAR(17) PRIMARY KEY,
    manufacturer_name VARCHAR(255) NOT NULL,
    description TEXT,
    horse_power INT NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_year INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    fuel_type VARCHAR(50) NOT NULL
);

-- Drop the trigger if it exists
DROP TRIGGER IF EXISTS vin_lowercase_trigger ON Vehicle;

-- Create the trigger for the Vehicle table
CREATE TRIGGER vin_lowercase_trigger
BEFORE INSERT OR UPDATE ON Vehicle
FOR EACH ROW EXECUTE FUNCTION vin_case_insensitive();
