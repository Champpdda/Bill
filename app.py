import streamlit as st
import requests
import os
from dotenv import load_dotenv
from firebase_config import initialize_firebase
from firebase_admin import firestore
from datetime import datetime

# ใส่ API Key ที่ได้รับ
api_key = '21766d7c69822a4e7d815c4f'

# เรียกใช้ฟังก์ชันเพื่อเชื่อมต่อกับ Firestore
db = initialize_firebase()

# ฟังก์ชันสำหรับแปลงสกุลเงิน
def convert_currency(api_key, from_currency, to_currency, amount):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)
    
    if response.status_code == 200:
        rates = response.json().get("rates", {})
        if to_currency in rates:
            return amount * rates[to_currency]
    return 0

# ฟังก์ชันสำหรับบันทึกใบเสร็จลง Firebase
def save_receipt_to_firestore(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, currency):
    try:
        receipt_data = {
            'bill_amount': bill_amount,
            'tax': tax,
            'tip': tip,
            'total_bill': total_bill_converted,
            'price_per_person': price_per_person_converted,
            'paid_amount': paid_amount,
            'change': change,
            'currency': currency,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        db.collection('receipts').add(receipt_data)
        st.success("Receipt successfully saved to the cloud.")
    except Exception as e:
        st.error(f"Error saving receipt to cloud: {e}")

# รายการของ denominations ตามสกุลเงิน
denominations = {
    "EUR": {
        "500 euro": 500,
        "200 euro": 200,
        "100 euro": 100,
        "50 euro": 50,
        "20 euro": 20,
        "10 euro": 10,
        "5 euro": 5,
        "2 euro": 2,
        "1 euro": 1,
        "50 cent": 0.50,
        "20 cent": 0.20,
        "10 cent": 0.10,
        "5 cent": 0.05,
        "2 cent": 0.02,
        "1 cent": 0.01,
    },
    "THB": {
        "1000 THB": 1000,
        "500 THB": 500,
        "100 THB": 100,
        "50 THB": 50,
        "20 THB": 20,
        "10 THB": 10,
        "5 THB": 5,
        "1 THB": 1,
    },
    "USD": {
        "100 USD": 100,
        "50 USD": 50,
        "20 USD": 20,
        "10 USD": 10,
        "5 USD": 5,
        "1 USD": 1,
    },
    "JPY": {
        "10000 JPY": 10000,
        "5000 JPY": 5000,
        "2000 JPY": 2000,
        "1000 JPY": 1000,
        "500 JPY": 500,
        "100 JPY": 100,
        "50 JPY": 50,
        "10 JPY": 10,
        "5 JPY": 5,
        "1 JPY": 1,
    },
    "GBP": {
        "50 GBP": 50,
        "20 GBP": 20,
        "10 GBP": 10,
        "5 GBP": 5,
        "1 GBP": 1,
    },
    "CNY": {
        "100 CNY": 100,
        "50 CNY": 50,
        "20 CNY": 20,
        "10 CNY": 10,
        "5 CNY": 5,
        "1 CNY": 1,
    },
    "LAK": {
        "10000 LAK": 10000,
        "5000 LAK": 5000,
        "2000 LAK": 2000,
        "1000 LAK": 1000,
        "500 LAK": 500,
        "100 LAK": 100,
        "50 LAK": 50,
        "20 LAK": 20,
        "10 LAK": 10,
        "5 LAK": 5,
        "1 LAK": 1,
    }
}

# ฟังก์ชันคำนวณบิล
def calculate_bill(bill_amount, tax_rate, tip_percentage, num_people):
    if bill_amount < 0:
        st.error("Bill amount must be non-negative.")
        return None, None, None, None
    if tax_rate < 0 or tip_percentage < 0:
        st.error("Tax and tip percentages must be non-negative.")
        return None, None, None, None
    if num_people <= 0:
        st.error("Number of people must be greater than zero.")
        return None, None, None, None
    
    tax = bill_amount * (tax_rate / 100)
    tip = bill_amount * (tip_percentage / 100)
    total_bill = bill_amount + tax + tip
    price_per_person = total_bill / num_people
    return tax, tip, total_bill, price_per_person


# ฟังก์ชันแปลงสกุลเงิน
def display_receipt(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, currency):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        receipt = f"""
        <div style="border: 1px solid #ccc; border-radius: 10px; padding: 20px; width: 400px; margin: auto; font-family: Arial, sans-serif;">
            <h2 style="text-align: center; color: #007BFF;">Receipt</h2>
            <p><strong>Date:</strong> {current_time}</p>
            <p><strong>Bill Amount:</strong> €{bill_amount:.2f}</p>
            <p><strong>Tax:</strong> {tax:.2f} {currency}</p>
            <p><strong>Tip:</strong> {tip:.2f} {currency}</p>
            <p><strong>Total Bill:</strong> {total_bill_converted:.2f} {currency}</p>
            <p><strong>Price per Person:</strong> {price_per_person_converted:.2f} {currency}</p>
            <p><strong>Paid Amount:</strong> {paid_amount:.2f} {currency}</p>
            <p><strong>Change:</strong> {change:.2f} {currency}</p>
            <p style="text-align: center; color: #28a745;">Thank you for your payment!</p>
        </div>
        """
        st.markdown(receipt, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying receipt: {e}")


# ฟังก์ชันแสดงใบเสร็จ
def display_receipt(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, currency):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        receipt = f"""
        <div style="border: 1px solid #ccc; border-radius: 10px; padding: 20px; width: 400px; margin: auto; font-family: Arial, sans-serif; background-color: #f9f9f9;">
            <h2 style="text-align: center; color: #007BFF;">Receipt</h2>
            <img src="path/to/logo.png" style="display: block; margin: auto; width: 100px;"/>
            <p><strong>Date:</strong> {current_time}</p>
            <p><strong>Bill Amount:</strong> €{bill_amount:.2f}</p>
            <p><strong>Tax:</strong> {tax:.2f} {currency}</p>
            <p><strong>Tip:</strong> {tip:.2f} {currency}</p>
            <p><strong>Total Bill:</strong> {total_bill_converted:.2f} {currency}</p>
            <p><strong>Price per Person:</strong> {price_per_person_converted:.2f} {currency}</p>
            <p><strong>Paid Amount:</strong> {paid_amount:.2f} {currency}</p>
            <p><strong>Change:</strong> {change:.2f} {currency}</p>
            <p style="text-align: center; color: #28a745;">Thank you for your payment!</p>
        </div>
        """
        st.markdown(receipt, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying receipt: {e}")


# ฟังก์ชันเปลี่ยนภาษา
def change_language(language):
    if language == 'Thai':
        return {
            'title': "เครื่องคิดเลขบิล",
            'bill_amount': "จำนวนบิล (EUR):",
            'tax_rate': "อัตราภาษี (%):",
            'tip_percentage': "เปอร์เซ็นต์ทิป (%):",
            'num_people': "จำนวนคน:",
            'currency_label': "เลือกสกุลเงินสำหรับการชำระเงิน:",
            'calculation_result': "ผลการคำนวณ",
            'payment': "การชำระเงิน",
            'download_receipt': "ดาวน์โหลดใบเสร็จ",
            'not_enough_money': "เงินที่ให้ไม่เพียงพอ."
        }
    elif language == 'Lao':  # เพิ่มการสนับสนุนภาษาลาว
        return {
            'title': "ຄະແນນບິນ",
            'bill_amount': "ຈຳນວນບິນ (EUR):",
            'tax_rate': "ອະດີດສາດ (%):",
            'tip_percentage': "ສ່ວນເພີ່ມ (%):",
            'num_people': "ຈຳນວນຄົນ:",
            'currency_label': "ເລືອກສະກຸນເງິນສໍາລັບການຈ່າຍ:",
            'calculation_result': "ຜົນການຄຳນວນ",
            'payment': "ການຈ່າຍ",
            'download_receipt': "ດາວໂหลດໃບເສຕະຕິ",
            'not_enough_money': "ເງິນທີ່ໃຫ້ບໍ່ພຽງພໍ."
        }
    else:  # Default to English
        return {
            'title': "Bill Calculator",
            'bill_amount': "Bill Amount (EUR):",
            'tax_rate': "Tax Rate (%):",
            'tip_percentage': "Tip Percentage (%):",
            'num_people': "Number of People:",
            'currency_label': "Select currency for payment:",
            'calculation_result': "Calculation Result",
            'payment': "Payment",
            'download_receipt': "Download Receipt",
            'not_enough_money': "Not enough money provided."
        }

# เปลี่ยน selectbox ในส่วนของการเลือกภาษา
language = st.sidebar.selectbox("Select Language:", ["English", "Thai", "Lao"])
labels = change_language(language)

st.title(labels['title'])
st.sidebar.header(labels['payment'])

# อินพุตข้อมูลบิล
bill_amount = st.sidebar.number_input(labels['bill_amount'], min_value=0.0, format="%.2f")
tax_rate = st.sidebar.number_input(labels['tax_rate'], min_value=0.0, format="%.2f")
tip_percentage = st.sidebar.number_input(labels['tip_percentage'], min_value=0.0, format="%.2f")
num_people = st.sidebar.number_input(labels['num_people'], min_value=1)

# ตัวเลือกสกุลเงินสำหรับการจ่าย
to_currency = st.sidebar.selectbox(labels['currency_label'], ["USD", "THB", "JPY", "GBP", "CNY", "LAK", "EUR"])
tax, tip, total_bill, price_per_person = calculate_bill(bill_amount, tax_rate, tip_percentage, num_people)

# แปลงผลลัพธ์ไปยังสกุลเงินที่เลือก
tax_converted = convert_currency(api_key, "EUR", to_currency, tax)
tip_converted = convert_currency(api_key, "EUR", to_currency, tip)
total_bill_converted = convert_currency(api_key, "EUR", to_currency, total_bill)
price_per_person_converted = convert_currency(api_key, "EUR", to_currency, price_per_person)

# Always display the "Calculation Result"
if total_bill_converted is not None and price_per_person_converted is not None:
    st.subheader(labels['calculation_result'])
    st.write(f"Tax: {tax_converted:.2f} {to_currency}")
    st.write(f"Tip: {tip_converted:.2f} {to_currency}")
    st.write(f"Total Bill: {total_bill_converted:.2f} {to_currency}")
    st.write(f"Price per Person: {price_per_person_converted:.2f} {to_currency}")

# ส่วนสำหรับการชำระเงิน
st.subheader(labels['payment'])

# ดึง denominations จากสกุลเงินที่เลือก
selected_denominations = denominations[to_currency]

paid_amount = 0
payment_details = {}

for denomination in selected_denominations:
    count = st.number_input(f"{denomination}:", min_value=0, step=1, key=denomination)
    payment_details[denomination] = count
    paid_amount += count * selected_denominations[denomination]

# Pay button logic
if st.button("Pay"):
    if paid_amount >= total_bill_converted:
        change = paid_amount - total_bill_converted
        
        # แสดงใบเสร็จ
        display_receipt(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, to_currency)

        # บันทึกข้อมูลใบเสร็จไปยัง Firestore
        save_receipt_to_firestore(bill_amount, tax, tip, total_bill_converted, price_per_person_converted, paid_amount, change, to_currency)

        # สร้างข้อความใบเสร็จ
        receipt_text = f"""
        Bill Amount: €{bill_amount:.2f}
        Tax: {tax_converted:.2f} {to_currency}
        Tip: {tip_converted:.2f} {to_currency}
        Total Bill: {total_bill_converted:.2f} {to_currency}
        Price per Person: {price_per_person_converted:.2f} {to_currency}
        Paid Amount: {paid_amount:.2f} {to_currency}
        Change: {change:.2f} {to_currency}
        Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """

        # ปุ่มพิมพ์ใบเสร็จ
        st.markdown(f"""
        <button onclick="printReceipt()">Print Receipt</button>
        <script>
            function printReceipt() {{
                var receipt = `{receipt_text}`;
                var win = window.open('', '', 'width=600,height=400');
                win.document.write('<pre>' + receipt + '</pre>');
                win.document.close();
                win.print();
            }}
        </script>
        """, unsafe_allow_html=True)

    else:
        shortfall = total_bill_converted - paid_amount
        st.error(f"{labels['not_enough_money']} You need to add {shortfall:.2f} {to_currency}.")
