from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'KSBK_FRONT_20260324')

# URL de votre API backend déjà existante
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://10.126.232.244:3000')

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/check-balance', methods=['POST'])
def check_balance():
    """Vérifier le solde d'un compte"""
    try:
        account_number = request.form.get('accountNumber')
        bank_code = request.form.get('bankCode')
        
        if not account_number or not bank_code:
            return jsonify({'error': 'Veuillez fournir le numéro de compte et le code banque'}), 400
        
        # Appel à votre API backend existante
        response = requests.post(
            f'{BACKEND_URL}/accounts/check-balance',
            json={
                'accountNumber': account_number,
                'bankCode': bank_code
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'balance': data.get('balance'),
                'message': data.get('message')
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Erreur {response.status_code}: {response.text}"
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f"Erreur de connexion: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/withdraw', methods=['POST'])
def withdraw():
    """Effectuer un retrait"""
    try:
        account_number = request.form.get('accountNumber')
        bank_code = request.form.get('bankCode')
        amount = request.form.get('amount')
        
        if not all([account_number, bank_code, amount]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400
        
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({'error': 'Le montant doit être supérieur à 0'}), 400
        except ValueError:
            return jsonify({'error': 'Montant invalide'}), 400
        
        # Appel à votre API backend existante
        response = requests.post(
            f'{BACKEND_URL}/accounts/withdraw',
            json={
                'accountNumber': account_number,
                'bankCode': bank_code,
                'amount': amount
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'message': data.get('message'),
                'newBalance': data.get('newBalance')
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Erreur {response.status_code}: {response.text}"
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f"Erreur de connexion: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
