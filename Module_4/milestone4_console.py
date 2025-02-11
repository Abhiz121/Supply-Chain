# -*- coding: utf-8 -*-
"""milestone4_console.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1smsuZX1zIvYtx2koqUaFTXU_2RHiPpe1
"""

import pandas as pd
import requests

file_path = "/content/Sugarcane_Supply_Chain_2021_2024.csv"
data = pd.read_csv(file_path)

class InventoryManagementSystem:
    def __init__(self, locations, default_warehouse_size, slack_webhook_url):
        self.locations = locations
        self.default_warehouse_size = default_warehouse_size
        self.slack_webhook_url = slack_webhook_url
        self.inventory = {
            location: {
                'warehouse_size': default_warehouse_size,
                'available_space': default_warehouse_size,
                'materials': [],
                'total_cost': 0
            }
            for location in locations
        }

    def send_slack_notification(self, message):
        """
        Sends a message to Slack using the webhook URL.
        """
        payload = {
            "text": message
        }
        response = requests.post(self.slack_webhook_url, json=payload)

        if response.status_code == 200:
            print("Slack notification sent successfully.")
        else:
            print(f"Failed to send Slack notification. Status code: {response.status_code}")

    def monthly_incoming(self):
        """
        Handle the stocking of materials (incoming supplies from suppliers).
        """
        location = input("Enter location name: ")
        if location not in self.inventory:
            print(f"Location '{location}' not found.")
            return

        material_name = input("Enter material name: ")
        size = float(input("Enter material size (in tons): "))
        cost = float(input("Enter material cost: "))

        if size > self.inventory[location]['available_space']:
            print(f"Not enough space in the warehouse for location '{location}'. Risk: Stock Overflow.")
            return

        self.inventory[location]['materials'].append({'name': material_name, 'size': size, 'cost': cost})
        self.inventory[location]['available_space'] -= size
        self.inventory[location]['total_cost'] += cost
        print(f"Stocked up {material_name} in {location}. Available space: {self.inventory[location]['available_space']} tons.")

    def monthly_outgoing(self):
        """
        Handle the supply of materials (outgoing supplies to customers).
        """
        location = input("Enter location name: ")
        if location not in self.inventory:
            print(f"Location '{location}' not found.")
            return

        material_name = input("Enter material name to supply: ")
        material_found = False
        for material in self.inventory[location]['materials']:
            if material['name'] == material_name:
                self.inventory[location]['available_space'] += material['size']
                self.inventory[location]['total_cost'] -= material['cost']
                self.inventory[location]['materials'].remove(material)
                material_found = True
                print(
                    f"Supplied {material_name} from {location}. Available space: {self.inventory[location]['available_space']} tons."
                )
                break

        if not material_found:
            print(f"Material '{material_name}' not found in location '{location}'.")

    def display_inventory(self):
        """
        Display the current inventory status for a specific location.
        """
        location = input("Enter the location name to display inventory: ")
        if location not in self.inventory:
            print(f"Location '{location}' not found.")
            return

        print(f"Location: {location}")
        print(f"  Warehouse Size: {self.inventory[location]['warehouse_size']} tons")
        print(f"  Available Space: {self.inventory[location]['available_space']} tons")
        print(f"  Materials:")
        for material in self.inventory[location]['materials']:
            print(f"    - {material['name']}: Size={material['size']} tons, Cost=${material['cost']}")
        print(f"  Total Cost of Materials: ${self.inventory[location]['total_cost']}")
        print("-" * 40)

    def generate_risk_alerts(self, location_filter=None, date_filter=None):
        """
        Generate alerts for supply chain risks based on weather and warehouse capacity.
        Filters can be applied for specific locations and dates.
        """
        print("Generating Risk Alerts:")
        for _, row in data.iterrows():
            location = row['Location']
            date = row['Date']
            weather = row['Weather Conditions']
            export_volume = row['Export Volume(tons)']
            available_space = self.inventory[location]['available_space']
            warehouse_size = self.inventory[location]['warehouse_size']

            if (location_filter and location != location_filter) or (date_filter and date != date_filter):
                continue

            alert_message = f"Location: {location}\nDate: {date}\nWeather: {weather}\nExport Volume: {export_volume} tons\n"

            if available_space <= 0.1 * warehouse_size and available_space > 0:
                alert_message += f"\n⚠️ Alert: Critical space available in {location}."
            elif available_space == 0:
                alert_message += f"\n🚨 Alert: High Risk! Warehouse in {location} is empty. Immediate restocking required."
            elif available_space < 0:
                alert_message += f"\n⚠️ Alert: Stock Overflow! Exceeded space capacity in {location}."
            elif available_space == warehouse_size:
                alert_message += f"\n⚠️ Risk: Empty warehouse in {location}. No stock available!"


            if weather in ['Rainy', 'Stormy']:
                alert_message += f"\n⚠️ Weather Alert: {weather} conditions may impact operations in {location}."

            self.send_slack_notification(alert_message)

            print("-" * 40)

    def save_inventory_to_csv(self):
        """
        Save the current inventory status to a CSV file.
        """
        inventory_data = []
        for location, details in self.inventory.items():
            for material in details['materials']:
                inventory_data.append({
                    'Location': location,
                    'Material Name': material['name'],
                    'Size (tons)': material['size'],
                    'Cost ($)': material['cost'],
                    'Available Space (tons)': details['available_space'],
                    'Total Cost ($)': details['total_cost']
                })

        df = pd.DataFrame(inventory_data)
        df.to_csv('inventory_status.csv', index=False)
        print("Inventory saved to 'inventory_status.csv'.")


slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
locations = data['Location'].unique()
ims = InventoryManagementSystem(locations=locations, default_warehouse_size=1000, slack_webhook_url=slack_webhook_url)

while True:
    print("\n1. Monthly incoming")
    print("2. Monthly outgoing")
    print("3. Display inventory")
    print("4. Generate risk alerts")
    print("5. Save and Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        ims.monthly_incoming()
    elif choice == '2':
        ims.monthly_outgoing()
    elif choice == '3':
        ims.display_inventory()
    elif choice == '4':
        location_filter = input("Enter location to filter alerts (leave blank for no filter): ")
        date_filter = input("Enter date to filter alerts (leave blank for no filter): ")
        if not location_filter:
            location_filter = None
        if not date_filter:
            date_filter = None
        ims.generate_risk_alerts(location_filter=location_filter, date_filter=date_filter)
    elif choice == '5':
        ims.save_inventory_to_csv()
        print("Exiting the system.")
        break
    else:
        print("Invalid choice. Please try again.")