import time
import random
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

USER_STATUS = {
    "user_123": {
        "status": "Basic",
        "limit": 2000000,
        "can_transfer_bank": False
    }
}

@app.route('/')
def index():
    """Menyajikan halaman UI utama (index.html)"""
    return render_template('index.html')

@app.route('/api/v1/pay-qris', methods=['POST'])
def handle_qris_payment():
    """
    Simulasi API untuk QRIS Payment.
    Ini memanggil KYC Context (cek limit) lalu Payment & Transfer Context.
    """
    data = request.json
    try:
        amount = int(data.get('amount', 0))
    except ValueError:
        return jsonify({"error": "Jumlah tidak valid"}), 400

    current_user_id = "user_123"
    user_data = USER_STATUS.get(current_user_id)
    
    app.logger.info(f"QRIS: Cek limit untuk {current_user_id} (Status: {user_data['status']})")

    if amount > user_data['limit']:
        time.sleep(0.5) # Simulasi latensi cek
        return jsonify({
            "error_code": "LIMIT_EXCEEDED",
            "message": f"Transaksi gagal. Akun {user_data['status']} tidak dapat bertransaksi di atas Rp {user_data['limit']:,}."
        }), 400 # 400 Bad Request

    app.logger.info(f"QRIS: Limit OK. Memproses pembayaran {amount}...")
    time.sleep(1) # Simulasi latensi transaksi

    response_data = {
        "payment_id": f"PAY-QRIS-{int(time.time())}",
        "merchant_name": data.get('merchant', 'Warung Kopi'),
        "amount": {
            "value": amount,
            "currency": "IDR"
        },
        "status": "Success",
        "message": "Payment Context & Transfer Context (Wallet) dipanggil."
    }
    return jsonify(response_data), 200


@app.route('/api/v1/webhook/bank-va', methods=['POST'])
def handle_va_webhook():
    """
    Simulasi Webhook yang diterima dari Bank (misal: BCA).
    Ini memanggil Funding Context lalu Transfer Context (Wallet).
    """
    data = request.json
    try:
        amount = int(data.get('amount', 0))
    except ValueError:
        return jsonify({"error": "Jumlah tidak valid"}), 400
        
    app.logger.info(f"VA Webhook: Diterima {amount} dari Bank.")
    
    time.sleep(1.0)

    response_data = {
        "topup_id": f"VA-BCA-{int(time.time())}",
        "source": "Bank BCA (via Webhook)",
        "amount": {
            "value": amount,
            "currency": "IDR"
        },
        "status": "Success",
        "message": "Funding Context & Transfer Context (Wallet) dipanggil."
    }
    return jsonify(response_data), 200


@app.route('/api/v1/start-kyc', methods=['POST'])
def handle_kyc_verification():
    """
    Simulasi API untuk eKYC.
    Ini memanggil KYC Context (memanggil Dukcapil) lalu Auth Context.
    """
    data = request.json
    nik = data.get('nik')
    name = data.get('name')

    if not nik or not name:
        return jsonify({"error": "NIK dan Nama harus diisi"}), 400

    app.logger.info(f"KYC: Memulai verifikasi untuk NIK {nik}...")

    time.sleep(1.5)

    current_user_id = "user_123"
    USER_STATUS[current_user_id] = {
        "status": "Verified",
        "limit": 20000000,
        "can_transfer_bank": True
    }
    app.logger.info(f"KYC: Sukses. Status {current_user_id} di-upgrade ke 'Verified'")

    response_data = {
        "submission_id": f"KYC-{int(time.time())}",
        "nik": nik,
        "status": "Approved",
        "dukcapil_match": True,
        "message": "KYC Context memanggil Dukcapil API. Akun di-upgrade ke Verified."
    }
    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)