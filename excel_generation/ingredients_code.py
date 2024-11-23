# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 16:09:37 2024

@author: mikeg
"""

import numpy as np
import json
import matplotlib.pyplot as plt

class Ingredient:
    def __init__(self, name, ingredient_id, price_data_raw=None):
        self.name = name
        self.unique_id = ingredient_id
        self.base_unit = ''
        self.price_data_raw = price_data_raw
        self.price_data_converted = []
        self.price_mean = ''
        self.price_median = ''
        self.price_mstd_dev = ''
        if self.price_data_raw:
            self.standardize_raw_price_data()
    
    def __repr__(self):
        return f"Ingredient(name={self.name}, unique ID={self.unique_id}, price={self.get_price()})"
        
    def get_price(self):
        """Return the first available price or a placeholder if not available."""
        if self.price_data_raw:
            return self.price_data_raw[0].get('price', "10.00")  # Return first price
        else:
            return "10.00"  # Default placeholder price
    
    def auto_assign_base_unit(self):
        if len(self.price_data_raw) > 0:
            unit_freq_dict = {}
    
            # Count frequency of each unit in price_data_raw
            for price_data in self.price_data_raw:
                unit = price_data['unit']
                unit_freq_dict[unit] = unit_freq_dict.get(unit, 0) + 1
    
            # Find the most frequent unit
            self.base_unit = max(unit_freq_dict, key=unit_freq_dict.get)
        else:
            print("Error. Cannot auto assign base unit. Ingredient has no price data.")

    def standardize_raw_price_data(self):
        if not self.base_unit:
            self.auto_assign_base_unit()

        conversion_factors = {
            'lb': {'kg': 0.453592, 'unit': 'kg'},
            'oz': {'g': 28.3495, 'unit': 'g'}
        }

        wrong_unit_base_one_list = []

        for item in self.price_data_raw:
            cleaned_item = item.copy()
            try:
                cleaned_item['price'] /= float(cleaned_item['selling_quantity'])
                cleaned_item['selling_quantity'] = 1
            except (KeyError, ValueError, TypeError):
                print(f"Error processing item: {item}")
                continue

            unit = cleaned_item.get('unit')
            if unit in conversion_factors and self.base_unit in conversion_factors[unit]:
                cleaned_item['unit'] = conversion_factors[unit]['unit']
            elif unit != self.base_unit:
                print(f"Cannot convert from {unit} to {self.base_unit}. No conversion rule defined.")
                continue

            wrong_unit_base_one_list.append(cleaned_item)

        self.price_data_converted = wrong_unit_base_one_list

    def print_converted_data(self):
        if not self.price_data_converted:
            print("No converted data available.")
            return

        try:
            for item in self.price_data_converted:
                print(f"Name: {item.get('name', 'Unknown name')}, Price: {item.get('price', 0.00):.2f}, Quantity: {item.get('selling_quantity', 'N/A')}, Unit: {item.get('unit', 'Unknown unit')}, Company: {item.get('company', 'Unknown company')}, Source: {item.get('source', 'Unknown source')}")
        except Exception as e:
            print(f"Error printing converted data: {e}")



