import firebase_admin
from firebase_admin import credentials, firestore

# ฟังก์ชันสำหรับการเชื่อมต่อ Firebase
def initialize_firebase():
    # ตรวจสอบว่ามีการ initialize Firebase ไปแล้วหรือไม่
    if not firebase_admin._apps:
        # โหลดไฟล์ service account key ที่คุณดาวน์โหลดมา
        cred = credentials.Certificate("bill-calculator-24e60-firebase-adminsdk-xugz0-3dcb949801.json")  # ใส่ path ที่ถูกต้อง
        firebase_admin.initialize_app(cred)

    # สร้างการเชื่อมต่อไปยัง Firestore
    return firestore.client()


