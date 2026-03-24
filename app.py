from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'KSBK_FRONT_20260324')

# URL de votre API backend (à adapter selon votre configuration)
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://10.126.232.244:3000')

# Décorateur pour vérifier si l'utilisateur est authentifié
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Page d'accueil - redirige vers la page de connexion"""
    if 'access_token' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Appel à l'API d'authentification
            response = requests.post(
                f'{BACKEND_URL}/auth/login',
                json={
                    'username': username,
                    'password': password
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                session['access_token'] = data.get('access_token')
                session['username'] = data.get('username')
                session['role'] = data.get('role')
                return redirect(url_for('dashboard'))
            else:
                error = "Nom d'utilisateur ou mot de passe incorrect"
                return render_template('login.html', error=error)
                
        except requests.exceptions.RequestException as e:
            error = f"Erreur de connexion au serveur: {str(e)}"
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord après connexion"""
    return render_template('dashboard.html', 
                         username=session.get('username'),
                         role=session.get('role'))

@app.route('/check-balance', methods=['POST'])
@login_required
def check_balance():
    """Vérifier le solde d'un compte"""
    try:
        account_number = request.form.get('accountNumber')
        bank_code = request.form.get('bankCode')
        
        if not account_number or not bank_code:
            return jsonify({'error': 'Veuillez fournir le numéro de compte et le code banque'}), 400
        
        # Appel à l'API backend avec le token
        response = requests.post(
            f'{BACKEND_URL}/accounts/check-balance',
            json={
                'accountNumber': account_number,
                'bankCode': bank_code
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {session.get("access_token")}'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'balance': data.get('balance'),
                'message': data.get('message')
            })
        elif response.status_code == 401:
            # Token expiré ou invalide
            session.clear()
            return jsonify({'error': 'Session expirée, veuillez vous reconnecter', 'redirect': '/login'}), 401
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
@login_required
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
        
        # Appel à l'API backend avec le token
        response = requests.post(
            f'{BACKEND_URL}/accounts/withdraw',
            json={
                'accountNumber': account_number,
                'bankCode': bank_code,
                'amount': amount
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {session.get("access_token")}'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'message': data.get('message'),
                'newBalance': data.get('newBalance')
            })
        elif response.status_code == 401:
            # Token expiré ou invalide
            session.clear()
            return jsonify({'error': 'Session expirée, veuillez vous reconnecter', 'redirect': '/login'}), 401
        else:
            return jsonify({
                'success': False,
                'error': f"Erreur {response.status_code}: {response.text}"
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f"Erreur de connexion: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)