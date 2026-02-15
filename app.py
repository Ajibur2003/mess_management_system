from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import bcrypt
import json
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = '9a4a5e2f4b123ca81b83f7cfb6c5a8d8e64db3dd564f5a2f137e6d2f3cc60cda'

def get_db():
    try:
        return mysql.connector.connect(
        host='sql12.freesqldatabase.com',
        user='sql12817134',
        password='hncPv6SSlu',
        database='sql12817134'
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def update_guest_meal_types(cursor, conn, meals, user_id, month_start, today, marketing):
    count = 0
    
    def update_guest(update_morning, update_night):
        try:
            cursor.execute(
                f"UPDATE `{meals}` SET guest_morning = %s, guest_night = %s WHERE id = %s AND date = %s",
                (update_morning, update_night, user_id, today_guest_meal)
            )
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error updating guest meals: {e}")
            conn.rollback()
    
    today_guest_meal = month_start
    previous_day_guest_meal = month_start - timedelta(days=1)
    
    while today_guest_meal <= today:
        try:
            cursor.execute(
                f"SELECT guest_morning, guest_night FROM `{meals}` WHERE id = %s AND date = %s",
                (user_id, today_guest_meal)
            )
            guest_meal_data = cursor.fetchone()
            
            cursor.execute(
                f"SELECT morning, night FROM `{marketing}` WHERE date = %s",
                (today_guest_meal,)
            )
            marketing_datas = cursor.fetchall()
            
            if not guest_meal_data:
                today_guest_meal += timedelta(days=1)
                previous_day_guest_meal += timedelta(days=1)
                continue
                
            guest_morning = guest_meal_data['guest_morning'] if isinstance(guest_meal_data, dict) else guest_meal_data[0]
            guest_night = guest_meal_data['guest_night'] if isinstance(guest_meal_data, dict) else guest_meal_data[1]
            
            guest_morning = str(guest_morning or '0').strip()
            guest_night = str(guest_night or '0').strip()
            
            guest_morning_parts = guest_morning.split()
            guest_night_parts = guest_night.split()
            
            try:
                guest_morning_count = int(guest_morning_parts[0]) if guest_morning_parts else 0
                guest_night_count = int(guest_night_parts[0]) if guest_night_parts else 0
            except (ValueError, IndexError):
                guest_morning_count = 0
                guest_night_count = 0
            
            if guest_morning_count == 0 and guest_night_count == 0:
                pass
            elif guest_morning_count == 0 and guest_night_count != 0:
                if marketing_datas:
                    for marketing_data in marketing_datas:
                        count += 1
                        if count == len(marketing_datas):
                            marketing_night = marketing_data['night'] if isinstance(marketing_data, dict) else marketing_data[1]
                            marketing_night = str(marketing_night).strip()
                            
                            if marketing_night in ['chicken', 'egg', 'fish', 'beef', 'other']:
                                current_type = guest_night_parts[1] if len(guest_night_parts) > 1 else ''
                                if current_type != marketing_night:
                                    update_night = f"{guest_night_count} {marketing_night}"
                                    update_guest(guest_morning, update_night)
                            elif marketing_night == 'veg':
                                current_type = guest_night_parts[1] if len(guest_night_parts) > 1 else ''
                                if current_type != 'veg':
                                    update_night = f"{guest_night_count} veg"
                                    update_guest(guest_morning, update_night)
                    count = 0
                    
            elif guest_morning_count != 0 and guest_night_count == 0:
                if marketing_datas:
                    for marketing_data in marketing_datas:
                        count += 1
                        if count == len(marketing_datas):
                            marketing_morning = marketing_data['morning'] if isinstance(marketing_data, dict) else marketing_data[0]
                            marketing_morning = str(marketing_morning).strip()
                            
                            if marketing_morning in ['chicken', 'egg', 'fish', 'beef', 'other']:
                                current_type = guest_morning_parts[1] if len(guest_morning_parts) > 1 else ''
                                if current_type != marketing_morning:
                                    update_morning = f"{guest_morning_count} {marketing_morning}"
                                    update_guest(update_morning, guest_night)
                            elif marketing_morning == 'veg':
                                current_type = guest_morning_parts[1] if len(guest_morning_parts) > 1 else ''
                                if current_type != 'veg':
                                    update_morning = f"{guest_morning_count} veg"
                                    update_guest(update_morning, guest_night)
                    count = 0
                    
            elif guest_morning_count != 0 and guest_night_count != 0:
                if marketing_datas:
                    for marketing_data in marketing_datas:
                        count += 1
                        if count == len(marketing_datas):
                            marketing_morning = marketing_data['morning'] if isinstance(marketing_data, dict) else marketing_data[0]
                            marketing_night = marketing_data['night'] if isinstance(marketing_data, dict) else marketing_data[1]
                            
                            marketing_morning = str(marketing_morning).strip()
                            marketing_night = str(marketing_night).strip()
                            
                            update_guest_morning = None
                            update_guest_night = None
                            
                            if marketing_morning in ['chicken', 'egg', 'fish', 'beef', 'other']:
                                current_type = guest_morning_parts[1] if len(guest_morning_parts) > 1 else ''
                                if current_type != marketing_morning:
                                    update_guest_morning = f"{guest_morning_count} {marketing_morning}"
                            elif marketing_morning == 'veg':
                                current_type = guest_morning_parts[1] if len(guest_morning_parts) > 1 else ''
                                if current_type != 'veg':
                                    update_guest_morning = f"{guest_morning_count} veg"
                            
                            if marketing_night in ['chicken', 'egg', 'fish', 'beef', 'other']:
                                current_type = guest_night_parts[1] if len(guest_night_parts) > 1 else ''
                                if current_type != marketing_night:
                                    update_guest_night = f"{guest_night_count} {marketing_night}"
                            elif marketing_night == 'veg':
                                current_type = guest_night_parts[1] if len(guest_night_parts) > 1 else ''
                                if current_type != 'veg':
                                    update_guest_night = f"{guest_night_count} veg"
                            
                            if update_guest_morning or update_guest_night:
                                final_morning = update_guest_morning if update_guest_morning else guest_morning
                                final_night = update_guest_night if update_guest_night else guest_night
                                update_guest(final_morning, final_night)
                    count = 0
                    
        except Exception as e:
            print(f"Error processing guest meals for {today_guest_meal}: {e}")
        
        today_guest_meal += timedelta(days=1)
        previous_day_guest_meal += timedelta(days=1)


@app.route('/', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        try:
            mess_code = request.form.get('mess_code', '').strip().lower()
            phone_number = request.form.get('phone_number', '').strip()
            password = request.form.get('password', '')
            
            if not phone_number or not password:
                message = "All fields are required"
                return render_template('login.html', message=message)
            
            try:
                phone_number = int(phone_number)
            except ValueError:
                message = "Invalid phone number"
                return render_template('login.html', message=message)
            
            conn = get_db()
            if not conn:
                message = "Database connection error"
                return render_template('login.html', message=message)
                
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM owners WHERE phone_number = %s", (phone_number,))
            owner = cursor.fetchone()
            
            user = None
            blocked = None
            if mess_code:
                cursor.execute("SELECT mess_code, blocked FROM messes WHERE mess_code = %s", (mess_code,))
                mess_details = cursor.fetchone()
                mess_code = mess_details['mess_code'] if mess_details else None
                blocked = int(mess_details['blocked']) if mess_details else None
            if mess_code:
                users = f"{mess_code}_users"
                cursor.execute(f"SELECT * FROM `{users}` WHERE phone_number = %s", (phone_number,))
                user = cursor.fetchone()
            
            conn.close()
            
            if user and blocked == 0:
                if bcrypt.checkpw(password.encode(), user['password'].encode()):
                    session['user_id'] = user['id']
                    session['name'] = user['name']
                    session['phone_number'] = user['phone_number']
                    session['role'] = user['role']
                    session['mess_code'] = user['mess_code']
                    session['blocked'] = user['blocked']
                    session['mess_blocked'] = blocked
                    return redirect(url_for('portal'))
                else:
                    message = "Invalid login credentials"
            elif owner:
                if bcrypt.checkpw(password.encode(), owner['password'].encode()):
                    session['owner_id'] = owner['id']
                    session['owner_phone_number'] = owner['phone_number']
                    session['role'] = 'owner'
                    return redirect(url_for('owner_dashboard'))
                else:
                    message = "Invalid login credentials"
            else:
                message = "Invalid login credentials"
                
        except Exception as e:
            print(f"Login error: {e}")
            message = "An error occurred during login"
    
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = None
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        mess_code = request.form.get('mess_code', '').strip().lower()
        if not phone_number or not mess_code:
            message = "Phone number and mess code are required"
        else:
            try:
                phone_number = int(phone_number)
                users = str(mess_code + "_users")
            except ValueError:
                message = "Invalid phone number"
            else:
                conn = get_db()
                if not conn:
                    message = "Database connection error"
                else:
                    try:
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute(f"SELECT * FROM `{users}` WHERE phone_number = %s", (phone_number,))
                        user = cursor.fetchone()
                        if user:
                            session['reset_phone'] = phone_number
                            session['users'] = users
                            return redirect(url_for('reset_password'))
                        else:
                            cursor.execute("SELECT * FROM messes WHERE phone_number = %s", (phone_number,))
                            mess_details = cursor.fetchone()
                            if mess_details and mess_details['blocked'] == 0:
                                session['reset_phone'] = phone_number
                                return redirect(url_for('reset_password'))
                            else:
                                message = "Phone number not found or blocked"
                    except Exception as e:
                        print(f"Error during password reset: {e}")
                        message = "An error occurred during password reset"
                    conn.close()
    return render_template('forgot_password.html', message=message)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_phone' not in session:
        return redirect('/')
    
    users = session.get('users')
    message = None
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            message = "Both password fields are required"
        elif new_password != confirm_password:
            message = "Passwords do not match"
        else:
            conn = get_db()
            if not conn:
                message = "Database connection error"
            else:
                cursor = conn.cursor()
                try:
                    hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                    cursor.execute(f"UPDATE `{users}` SET password=%s WHERE phone_number=%s", (hashed_new_password, session['reset_phone']))
                    conn.commit()
                    session.pop('reset_phone', None)
                    flash("Password reset successfully", "success")
                except Exception as e:
                    print(f"Error resetting password: {e}")
                    message = "An error occurred while resetting password"
                finally:
                    conn.close()

    return render_template('reset_password.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' not in session or session.get('role') != 'head_manager' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')
    
    message = None
    
    if request.method == 'POST':
        try:
            registration_date = request.form.get('registration_date')
            name = request.form.get('name')
            father_name = request.form.get('father_name', 'none')
            father_number = request.form.get('father_number', 0)
            phone_number = request.form.get('phone_number')
            whatsapp_number = request.form.get('whatsapp_number', 0)
            insta_id = request.form.get('insta_id', 'none')
            address = request.form.get('address', 'none')
            occupation = request.form.get('occupation', 'none')
            university_name = request.form.get('university_name', 'none')
            department_name = request.form.get('department_name', 'none')
            university_id = request.form.get('university_id', 'none')
            instrument_amount = request.form.get('instrument_amount', 0)
            paid = request.form.get('paid', 'unpaid')
            payment_method = request.form.get('payment_method', 'none')
            payment_by = request.form.get('payment_by', 'none')
            refund_amount = request.form.get('refund_amount', 0)
            note = request.form.get('note', 'nothing')
            password = request.form.get('password')
            
            if not password or not name or not phone_number:
                message = "Name, phone number and password are required"
                return render_template('register.html', message=message)
            
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            mess_code = session.get('mess_code')
            users = f"{mess_code}_users"
            
            conn = get_db()
            if not conn:
                message = "Database connection error"
                return render_template('register.html', message=message)
                
            cursor = conn.cursor()
            
            cursor.execute(
                f"""INSERT INTO `{users}` 
                (registration_date, name, father_name, father_number, phone_number, whatsapp_number, 
                insta_id, address, occupation, university_name, department_name, university_id, 
                instrument_amount, paid, payment_method, payment_by, refund_amount, note, password, 
                mess_code, role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (registration_date, name, father_name, father_number, phone_number, whatsapp_number,
                 insta_id, address, occupation, university_name, department_name, university_id,
                 instrument_amount, paid, payment_method, payment_by, refund_amount, note,
                 hashed_password, mess_code, 'user')
            )
            
            conn.commit()
            conn.close()
            
            flash('Registration successful!', 'success')
            message = "Registration successful!"
            session['message'] = message
            return redirect(url_for('register'))
            
        except Exception as e:
            print(f"Registration error: {e}")
            message = f"An error occurred: {str(e)}"
    
    return render_template('register.html', message=message)

@app.route('/show_user_details', methods=['GET', 'POST'])
def show_user_details():
    if 'user_id' not in session or session.get('role') != 'head_manager' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')
    
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect('/')
        
    cursor = conn.cursor(dictionary=True)
    mess_code = str(session.get('mess_code'))
    users = f"{mess_code}_users"
    
    cursor.execute(f"SELECT * FROM `{users}`")
    user_details = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        unpaid = request.form.get('new_status')
        user_id = request.form.get('user_id')

        conn = get_db()
        if not conn:
            flash('Database connection error', 'error')
            return redirect('/show_user_details')

        cursor = conn.cursor()
        cursor.execute(f"UPDATE `{users}` SET paid=%s WHERE id=%s", (unpaid, user_id))
        conn.commit()
        conn.close()
        return redirect('/show_user_details')

    
    return render_template('show_user_details.html', user_details=user_details)


@app.route('/blocked', methods=['GET', 'POST'])
def blocked():
    if 'user_id' not in session or session.get('role') != 'head_manager' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')
    
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect('/')
        
    cursor = conn.cursor(dictionary=True)
    mess_code = str(session.get('mess_code'))
    users = f"{mess_code}_users"
    
    if request.method == 'POST':
        try:
            if 'action' in request.form:
                action = request.form.get('action')
                user_id = int(request.form.get('user_id'))
                
                if action not in ['block', 'unblock']:
                    flash('Invalid action.', 'error')
                else:
                    new_val = 1 if action == 'block' else 0
                    cursor.execute(f"UPDATE `{users}` SET blocked=%s WHERE id=%s", (new_val, user_id))
                    conn.commit()
                    flash(f"User {'blocked' if new_val else 'unblocked'} successfully.", 'success')
                    
            if 'new_role' in request.form:
                new_role = request.form.get('new_role')
                user_id = int(request.form.get('user_id'))
                
                if new_role not in ['user', 'manager', 'head_manager']:
                    flash('Invalid role.', 'error')
                else:
                    cursor.execute(f"UPDATE `{users}` SET role=%s WHERE id=%s", (new_role, user_id))
                    conn.commit()
                    flash(f"User role updated to {new_role} successfully.", 'success')
                    
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}", 'error')
        
        return redirect('/blocked')
    
    cursor.execute(f"SELECT id, name, role, blocked FROM `{users}`")
    user = cursor.fetchall()
    conn.close()
    
    return render_template('blocked.html', users=user)


@app.route('/owner_dashboard', methods=['GET', 'POST'])
def owner_dashboard():
    if session.get('role') != 'owner':
        return redirect('/')
    
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect('/')
        
    cursor = conn.cursor(dictionary=True, buffered=True)

    today = datetime.today().date()
    month_start = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day_of_month = next_month - timedelta(days=1)

    def all_messes():
        try:
            cursor.execute("SELECT * FROM messes")
            mess = cursor.fetchall()
        except mysql.connector.IntegrityError:
            flash('Mess code already exists!', 'error')
            mess = None
            return redirect('/owner_dashboar')
        return mess

    mess = all_messes()
    
    if request.method == 'POST':
        if 'mess_name' in request.form:
            registration_date = request.form.get('registration_date')
            mess_code = request.form.get('mess_code')
            mess_name = request.form.get('mess_name')
            mess_address = request.form.get('mess_address', 'none')
            address_link = request.form.get('address_link', 'none')
            first_person_name = request.form.get('first_person_name', 'none')
            first_person_phone_number = request.form.get('first_person_phone_number', 0)
            first_person_whatsapp_number = request.form.get('first_person_whatsapp_number', 0)
            first_person_insta_id = request.form.get('first_person_insta_id', 'none')
            second_person_name = request.form.get('second_person_name', 'none')
            second_person_phone_number = request.form.get('second_person_phone_number', 0)
            second_person_whatsapp_number = request.form.get('second_person_whatsapp_number', 0)
            second_person_insta_id = request.form.get('second_person_insta_id', 'none')
            start_date = request.form.get('start_date', 'none')
            end_date = request.form.get('end_date', 'none')
            mess_password = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt()).decode()
            
            try:
                cursor.execute(
                    """INSERT INTO messes 
                    (registration_date, mess_code, mess_name, mess_address, address_link, 
                    manager_name, phone_number, whatsapp_number, insta_id, 
                    manager_name2, phone_number2, whatsapp_number2, insta_id2, 
                    start_date, end_date, password) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (registration_date, mess_code, mess_name, mess_address, address_link,
                        first_person_name, first_person_phone_number, first_person_whatsapp_number, first_person_insta_id,
                        second_person_name, second_person_phone_number, second_person_whatsapp_number, second_person_insta_id,
                        start_date, end_date, mess_password)
                )
                conn.commit()
            except Exception as e:
                print("error:",e)
                flash('Mess code already exists!', 'error')
                return redirect('/owner_dashboard')

        elif 'create_table' in request.form:
            mess_code_input = request.form.get('mess_code')
            number_input = request.form.get('number')

            if not mess_code_input and not number_input:
                return redirect('/owner_dashboard', messes=messes)
            
            try:
                cursor.execute("SELECT mess_code FROM messes WHERE mess_code = %s and phone_number = %s",(mess_code_input, int(number_input)))
                mess_code_output = cursor.fetchone()
                mess_code_output = mess_code_output['mess_code']
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            
            if not mess_code_output:
                flash(f'Not found mess code in messes')
                return redirect('/owner_dashboard', messes=messes)

            users = f"{str(mess_code_output)}_users"
            meals = f"{str(mess_code_output)}_meals"
            marketing = f"{str(mess_code_output)}_marketing"
            marketing_pending = f"{str(mess_code_output)}_marketing_pending"
            deposit = f"{str(mess_code_output)}_deposit"
            deposit_pending = f"{str(mess_code_output)}_deposit_pending"
            variables = f"{str(mess_code_output)}_variables"
            meal_charge = f"{str(mess_code_output)}_meal_charge"

            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{users}` (
                    id BIGINT PRIMARY KEY AUTO_INCREMENT,
                    registration_date DATE,
                    name VARCHAR(100) NOT NULL,
                    phone_number BIGINT DEFAULT 0,
                    occupation VARCHAR(100) DEFAULT 'none',
                    instrument_amount int DEFAULT 0,
                    paid varchar(20) DEFAULT 'unpaid',
                    payment_method VARCHAR(50) DEFAULT 'none',
                    payment_by VARCHAR(50) DEFAULT 'none',
                    refund_amount int DEFAULT 0,
                    password VARCHAR(255) NOT NULL,
                    mess_code VARCHAR(20) NOT NULL,
                    role varchar(20) DEFAULT 'user',
                    blocked TINYINT(1) NOT NULL DEFAULT 0,
                    note VARCHAR(255) DEFAULT 'nothing'
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            
            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{meals}` (
                    id BIGINT,
                    name varchar(20),
                    date DATE,
                    morning INT DEFAULT 0,
                    night INT DEFAULT 0,
                    guest_morning varchar(50) DEFAULT '0',
                    guest_night varchar(50) DEFAULT '0',
                    note VARCHAR(255) DEFAULT 'nothing',
                    UNIQUE (id,date)
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            
            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{marketing}` (
                    sl_no BIGINT UNIQUE,
                    id BIGINT,
                    username VARCHAR(60),
                    date DATE,
                    morning VARCHAR(20),
                    night VARCHAR(20),
                    shop_money DECIMAL(10,2) DEFAULT 0,
                    veg_money DECIMAL(10,2) DEFAULT 0,
                    non_veg_money DECIMAL(10,2) DEFAULT 0,
                    other_money DECIMAL(10,2) DEFAULT 0,
                    common_money DECIMAL(10,2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    note VARCHAR(255) DEFAULT 'nothing'
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')

            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{marketing_pending}` (
                    sl_no BIGINT UNIQUE AUTO_INCREMENT,
                    id BIGINT,
                    username VARCHAR(60),
                    date DATE,
                    morning VARCHAR(50),
                    night VARCHAR(50),
                    shop_money DECIMAL(10,2) DEFAULT 0,
                    veg_money DECIMAL(10,2) DEFAULT 0,
                    non_veg_money DECIMAL(10,2) DEFAULT 0,
                    other_money DECIMAL(10,2) DEFAULT 0,
                    common_money DECIMAL(10,2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    note VARCHAR(255) DEFAULT 'nothing'
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            
            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{deposit}` (
                    SL_no BIGINT UNIQUE,
                    id BIGINT,
                    name VARCHAR(100),
                    date DATE,
                    money DECIMAL(10, 2),
                    payment_by VARCHAR(50),
                    note VARCHAR(100) DEFAULT 'nothing',
                    status VARCHAR(20) DEFAULT 'pending'
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')

            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{deposit_pending}` (
                    SL_no BIGINT UNIQUE AUTO_INCREMENT,
                    id BIGINT,
                    name VARCHAR(100),
                    date DATE,
                    money DECIMAL(10, 2),
                    payment_by VARCHAR(50),
                    note VARCHAR(100) DEFAULT 'nothing',
                    status VARCHAR(20) DEFAULT 'pending'
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')

            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{variables}` (
                    id BIGINT UNIQUE AUTO_INCREMENT,
                    manager_name VARCHAR(100) DEFAULT NULL,
                    date DATE UNIQUE,
                    meal_charge DECIMAL(10,2) DEFAULT 0,
                    no_of_members INT DEFAULT 0,
                    common_charge DECIMAL(10,2) DEFAULT 0,
                    guest_meal_range INT DEFAULT 0,
                    common_meal INT DEFAULT 0,
                    total_morning_meal INT DEFAULT 0,
                    total_night_meal INT DEFAULT 0,
                    total_meal INT DEFAULT 0,
                    total_guest_veg_meal INT DEFAULT 0,
                    total_guest_egg_meal INT DEFAULT 0,
                    total_guest_fish_meal INT DEFAULT 0,
                    total_guest_chicken_meal INT DEFAULT 0,
                    total_guest_beef_meal INT DEFAULT 0,
                    total_guest_other_meal INT DEFAULT 0,
                    total_guest_meal INT DEFAULT 0,
                    total_guest_amount DECIMAL(10,2) DEFAULT 0,
                    veg_guest_charge DECIMAL(10,2) DEFAULT 0,
                    egg_guest_charge DECIMAL(10,2) DEFAULT 0,
                    fish_guest_charge DECIMAL(10,2) DEFAULT 0,
                    chicken_guest_charge DECIMAL(10,2) DEFAULT 0,
                    beef_guest_charge DECIMAL(10,2) DEFAULT 0,
                    other_guest_charge DECIMAL(10,2) DEFAULT 0,
                    masi_M_on_off varchar(10) DEFAULT 'per_head',
                    masi_charge DECIMAL(10,2) DEFAULT 0,
                    Market_shop_money DECIMAL(10,2) DEFAULT 0,
                    Market_veg_money DECIMAL(10,2) DEFAULT 0,
                    Market_non_veg_money DECIMAL(10,2) DEFAULT 0,
                    Market_other_money DECIMAL(10,2) DEFAULT 0,
                    total_marketing_money DECIMAL(10,2) DEFAULT 0,
                    total_deposit_amount DECIMAL(10,2) DEFAULT 0,
                    message VARCHAR(255) DEFAULT NULL,
                    one_time_meal_charge_update INT DEFAULT 0,
                    meal_calculation_date DATE DEFAULT NULL
                )""")
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            try:
                cursor.execute(f"INSERT INTO `{variables}` (date) VALUES (%s)", (last_day_of_month,))
                conn.commit()
            except Exception as e:
                pass
            
            try:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{meal_charge}` (
                    id BIGINT NOT NULL,
                    date DATE,
                    name VARCHAR(100),
                    total_meal INT DEFAULT 0,
                    meal_charge DECIMAL(10,2) DEFAULT 0,
                    T_veg_guest_meal INT DEFAULT 0,
                    T_egg_guest_meal INT DEFAULT 0,
                    T_fish_guest_meal INT DEFAULT 0,
                    T_chicken_guest_meal INT DEFAULT 0,
                    T_beef_guest_meal INT DEFAULT 0,
                    T_other_guest_meal INT DEFAULT 0,
                    T_guest_amount INT DEFAULT 0,
                    common_charge DECIMAL(10,2) DEFAULT 0,
                    deposit DECIMAL(10,2) DEFAULT 0,
                    amount DECIMAL(10,2) DEFAULT 0,
                    UNIQUE (id,date)
                )""")
                conn.commit()
            except Exception as e:
                print("error:",e)
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            
            flash('Mess registered successfully!', 'success')

        elif 'manager_name' in request.form:
            
            manager_name = request.form.get('manager_name')
            phone_number = request.form.get('phone_number')
            password = bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt()).decode()
            mess_code = request.form.get('mess_code')

            users = f"{str(mess_code)}_users"

            try:
                cursor.execute(
                    f"""INSERT INTO `{users}` 
                    (registration_date, name, phone_number, password, mess_code, role) 
                    VALUES (%s, %s, %s, %s, %s, 'head_manager')""",
                    (today, manager_name, phone_number, password, mess_code)
                )
                conn.commit()
            except Exception as e:
                flash(f'Error: {e}', 'error')
                return redirect('/owner_dashboard')
            flash('Assign Head Manager successfully!', 'success')
                

        elif 'action' in request.form:
            action = request.form.get('action')
            mess_code = str(request.form.get('mess_code'))
            
            if action not in ['block', 'unblock']:
                flash('Invalid action.', 'error')
            else:
                try:
                    new_val = 1 if action == 'block' else 0
                    cursor.execute("UPDATE messes SET blocked=%s WHERE mess_code=%s", (new_val, mess_code))
                    conn.commit()
                    flash(f"User {'blocked' if new_val else 'unblocked'} successfully.", 'success')
                except Exception as e:

                    flash(f"Error updating dates: {e}", 'error')
                
        elif 'new_start_date' in request.form:
            mess_code = request.form.get('mess_code')
            new_start_date = request.form.get('new_start_date')
            new_end_date = request.form.get('new_end_date')
            
            try:
                cursor.execute("UPDATE messes SET start_date=%s, end_date=%s WHERE mess_code=%s", (new_start_date, new_end_date, mess_code))
                conn.commit()
                flash('Mess dates updated successfully.', 'success')
            except Exception as e:
                flash(f"Error updating dates: {e}", 'error')

    mess = all_messes()
    conn.close()
    return render_template('owner_dashboard.html', messes=mess)


@app.route('/portal', methods=['GET', 'POST'])
def portal():
    if 'user_id' not in session:
        return redirect('/')
    
    return render_template('portal.html', role=session['role'])


@app.route('/set_values', methods=['GET', 'POST'])
def set_values():
    if 'user_id' not in session or session.get('role') != 'head_manager' or session.get('mess_blocked') == 1:
        flash('You must be a manager to access this page.', 'error')
        return redirect('/')
    
    mess_code = str(session.get('mess_code'))
    variables = f"{mess_code}_variables"
    
    conn = get_db()
    if not conn:
        flash('Database connection error', 'error')
        return redirect('/')
    
    cursor = conn.cursor(dictionary=True)
    
    today = datetime.today().date()
    month_start = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day_of_month = next_month - timedelta(days=1)
    
    if request.method == 'POST':
        try:
            masi_M_on_off = request.form.get('masi_M_on_off')
            masi_charge = request.form.get('masi_charge')
            guest_meal_range = request.form.get('guest_meal_range')
            common_meal = request.form.get('common_meal')
            veg_guest_charge = request.form.get('veg_guest_charge')
            egg_guest_charge = request.form.get('egg_guest_charge')
            fish_guest_charge = request.form.get('fish_guest_charge')
            chicken_guest_charge = request.form.get('chicken_guest_charge')
            beef_guest_charge = request.form.get('beef_guest_charge')
            other_guest_charge = request.form.get('other_guest_charge')
            calculation_date = request.form.get('calculation_date')
            if not calculation_date:
                calculation_date = last_day_of_month
            
            cursor.execute(
                f"""UPDATE `{variables}` SET 
                masi_M_on_off=%s, masi_charge=%s, guest_meal_range=%s, common_meal=%s,
                veg_guest_charge=%s, egg_guest_charge=%s, fish_guest_charge=%s,
                chicken_guest_charge=%s, beef_guest_charge=%s, other_guest_charge=%s, meal_calculation_date=%s
                WHERE date=%s""",
                (masi_M_on_off, masi_charge, guest_meal_range, common_meal,
                 veg_guest_charge, egg_guest_charge, fish_guest_charge,
                 chicken_guest_charge, beef_guest_charge, other_guest_charge, calculation_date,last_day_of_month)
            )
            conn.commit()
            flash('Values updated successfully!', 'success')
            return redirect('set_values')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error: {e}', 'error')
    
    cursor.execute(f"SELECT * FROM `{variables}` WHERE date=%s", (last_day_of_month,))
    variables_data = cursor.fetchone()
    conn.close()
    
    return render_template('set_values.html', variables=variables_data)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    User dashboard for managing daily meals.
    Handles meal updates, guest meals, and data fetching.
    """
    try:
        # Session validation
        if 'user_id' not in session or session.get('role') != 'user' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
            flash('Unauthorized access. Please login.', 'danger')
            return redirect('/')

        # Get session data with validation
        mess_code = session.get('mess_code')
        username = session.get('name')
        user_id = session.get('user_id')
        
        if not mess_code or not username or not user_id:
            flash('Session data missing. Please login again.', 'danger')
            return redirect('/')

        # Convert to string for table names
        mess_code = str(mess_code)
        users = str(mess_code + "_users")
        meals = str(mess_code + "_meals")
        marketing = str(mess_code + "_marketing")
        marketing_pending = str(mess_code + "_marketing_pending")
        deposit = str(mess_code + "_deposit")
        deposit_pending = str(mess_code + "_deposit_pending")

        message = None
        meals_data = []

        # Get today's date and month boundaries
        today = datetime.today().date()
        privious_day = today - timedelta(days=1)
        now = datetime.now().time()
        month_start = today.replace(day=1)
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_of_month = next_month - timedelta(days=1)

        # Database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'danger')
            return redirect('/')

        try:
            cursor = conn.cursor(dictionary=True, buffered=True)

            def update_global_meals_table(username, date_obj, morning, night, guest_morning, guest_night, user_id):
                """
                Update global meals table with error handling.
                """
                try:
                    # Validate inputs
                    if not username or not date_obj or user_id is None:
                        raise ValueError("Missing required parameters for meal update")
                    
                    # Convert to appropriate types
                    morning = int(morning) if morning is not None else 0
                    night = int(night) if night is not None else 0
                    guest_morning = int(guest_morning) if guest_morning else 0
                    guest_night = int(guest_night) if guest_night else 0
                    
                    cursor.execute("""
                        INSERT INTO `{meals}` (name, date, morning, night, guest_morning, guest_night, id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            morning=VALUES(morning), 
                            night=VALUES(night), 
                            guest_morning=VALUES(guest_morning), 
                            guest_night=VALUES(guest_night)
                    """.format(meals=meals), (username, date_obj, morning, night, guest_morning, guest_night, user_id))
                    
                    conn.commit()
                    
                except ValueError as ve:
                    conn.rollback()
                    raise ValueError(f"Invalid data for meal update: {str(ve)}")
                except Exception as e:
                    conn.rollback()
                    raise Exception(f"Failed to update meals: {str(e)}")

            # Handle POST requests
            if request.method == 'POST':
                try:
                    mode = request.form.get('meal_mode')
                    toggle_value = request.form.get('toggle')
                    toggle = 1 if toggle_value == 'on' else 0 if toggle_value == 'off' else None
                    guest = request.form.get('guest')

                    if not mode and not guest:
                        flash('Please select a meal update mode.', 'danger')
                        return redirect(url_for('dashboard'))

                    # CONTINUE MODE
                    if mode == 'continue':
                        selected_option = request.form.get('continue_option')
                        
                        if not selected_option:
                            flash('Please select a continue option.', 'danger')
                            return redirect(url_for('dashboard'))

                        # Time boundaries
                        tonight_start = datetime.strptime('00:00', '%H:%M').time()
                        tonight_end = datetime.strptime('16:00', '%H:%M').time()
                        tomorrow_morning_start = datetime.strptime('00:00', '%H:%M').time()
                        tomorrow_morning_day_end = datetime.strptime('23:59', '%H:%M').time()
                        tomorrow_morning_day_start = datetime.strptime('00:00', '%H:%M').time()
                        tomorrow_morning_end = datetime.strptime('04:00', '%H:%M').time()

                        # TONIGHT OPTION
                        if selected_option == 'tonight' and toggle is not None and tonight_start <= now <= tonight_end:
                            try:
                                cursor.execute(
                                    "SELECT morning FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals), 
                                    (today, user_id)
                                )
                                result = cursor.fetchone()
                                preserved_morning = result['morning'] if result else 0

                                current_day = today
                                while current_day <= last_day_of_month:
                                    morning = preserved_morning if current_day == today else toggle
                                    night = toggle
                                    
                                    cursor.execute(
                                        "SELECT guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                        (current_day, user_id)
                                    )
                                    result = cursor.fetchone()
                                    guest_morning = result['guest_morning'] if result else 0
                                    guest_night = result['guest_night'] if result else 0
                                    
                                    update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                    current_day += timedelta(days=1)
                                
                                message = f"Today's morning preserved. Meals updated from tonight to {last_day_of_month}."
                                flash(message, 'success')
                            except Exception as e:
                                flash(f"Error updating tonight meals: {str(e)}", 'danger')
                                conn.rollback()

                        # TOMORROW MORNING OPTION
                        elif selected_option == 'tomorrow_morning' and toggle is not None:
                            try:
                                if tomorrow_morning_start <= now <= tomorrow_morning_day_end:
                                    current_day = today + timedelta(days=1)
                                    while current_day <= last_day_of_month:
                                        morning = toggle
                                        night = toggle
                                        
                                        cursor.execute(
                                            "SELECT guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                            (current_day, user_id)
                                        )
                                        result = cursor.fetchone()
                                        guest_morning = result['guest_morning'] if result else 0
                                        guest_night = result['guest_night'] if result else 0
                                        
                                        update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                        current_day += timedelta(days=1)
                                    
                                    message = f"Meals updated from tomorrow morning to {last_day_of_month}."
                                    flash(message, 'success')
                                    
                                elif tomorrow_morning_day_start <= now <= tomorrow_morning_end:
                                    current_day = today
                                    while current_day <= last_day_of_month:
                                        morning = toggle
                                        night = toggle
                                        
                                        cursor.execute(
                                            "SELECT guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                            (current_day, user_id)
                                        )
                                        result = cursor.fetchone()
                                        guest_morning = result['guest_morning'] if result else 0
                                        guest_night = result['guest_night'] if result else 0
                                        
                                        update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                        current_day += timedelta(days=1)
                                    
                                    message = f"Meals updated from tomorrow morning to {last_day_of_month}."
                                    flash(message, 'success')
                                else:
                                    message = "Time out. Cannot update meals at this time."
                                    flash(message, 'danger')
                            except Exception as e:
                                flash(f"Error updating tomorrow morning meals: {str(e)}", 'danger')
                                conn.rollback()

                        # TOMORROW NIGHT OPTION
                        elif selected_option == 'tomorrow_night' and toggle is not None:
                            try:
                                cursor.execute(
                                    "SELECT morning FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                    (today + timedelta(days=1), user_id)
                                )
                                result = cursor.fetchone()
                                preserved_morning = result['morning'] if result else 0
                                
                                current_day = today + timedelta(days=1)
                                while current_day <= last_day_of_month:
                                    morning = preserved_morning if current_day == today + timedelta(days=1) else toggle
                                    night = toggle
                                    
                                    cursor.execute(
                                        "SELECT guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                        (current_day, user_id)
                                    )
                                    result = cursor.fetchone()
                                    guest_morning = result['guest_morning'] if result else 0
                                    guest_night = result['guest_night'] if result else 0
                                    
                                    update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                    current_day += timedelta(days=1)
                                
                                message = f"Tomorrow's morning preserved. Meals updated from tomorrow night to {last_day_of_month}."
                                flash(message, 'success')
                            except Exception as e:
                                flash(f"Error updating tomorrow night meals: {str(e)}", 'danger')
                                conn.rollback()
                        else:
                            message = "Invalid time or selection for Continue option."
                            flash(message, 'danger')

                    # JUST NIGHT MODE OR GUEST NIGHT
                    elif mode == 'just_night' or guest == 'guest_night':
                        try:
                            if datetime.strptime('00:00', '%H:%M').time() <= now <= datetime.strptime('23:59', '%H:%M').time(): #need change
                                cursor.execute(
                                    "SELECT morning, night, guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id= %s".format(meals=meals),
                                    (today, user_id)
                                )
                                result = cursor.fetchone()

                                morning = result['morning'] if result else 0
                                current_night = result['night'] if result else 0
                                guest_morning = result['guest_morning'] if result else 0
                                guest_night = result['guest_night'] if result else 0
                                new_night = current_night

                                if guest == 'guest_night':
                                    guest_night_input = request.form.get('guest_night_count', 0)
                                    try:
                                        guest_night = int(guest_night_input)
                                        if guest_night < 0:
                                            guest_night = 0
                                    except (ValueError, TypeError):
                                        guest_night = 0
                                
                                if mode == 'just_night':
                                    new_night = 0 if current_night == 1 else 1

                                update_global_meals_table(username, today, morning, new_night, guest_morning, guest_night, user_id)

                                message = f"Night meal {'ON' if new_night else 'OFF'} for today." if mode == 'just_night' else f"Today night {guest_night} guest meal added"
                                flash(message, 'success')
                            else:
                                flash("Time out. Night meal updates allowed only between 12:00 AM and 5:00 PM.", 'danger')
                        except Exception as e:
                            flash(f"Error updating night meal: {str(e)}", 'danger')
                            conn.rollback()
                        
                        return redirect(url_for('dashboard'))

                    # JUST MORNING MODE OR GUEST MORNING
                    elif mode == 'just_morning' or guest == 'guest_morning':
                        try:
                            six_am = datetime.strptime('06:00', '%H:%M').time()
                            end_day = datetime.strptime('23:59', '%H:%M').time()
                            midnight = datetime.strptime('00:00', '%H:%M').time()
                            three_am = datetime.strptime('03:00', '%H:%M').time()

                            if midnight <= now <= three_am:
                                # Toggle today's morning meal
                                cursor.execute(
                                    "SELECT morning, night, guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id= %s".format(meals=meals),
                                    (today, user_id)
                                )
                                result = cursor.fetchone()

                                current_morning = result['morning'] if result else 0
                                night = result['night'] if result else 0
                                guest_morning = result['guest_morning'] if result else 0
                                guest_night = result['guest_night'] if result else 0
                                new_morning = current_morning

                                if guest == 'guest_morning':
                                    guest_morning_input = request.form.get('guest_morning_count', 0)
                                    try:
                                        guest_morning = int(guest_morning_input)
                                        if guest_morning < 0:
                                            guest_morning = 0
                                    except (ValueError, TypeError):
                                        guest_morning = 0
                                
                                if mode == 'just_morning':
                                    new_morning = 0 if current_morning == 1 else 1

                                update_global_meals_table(username, today, new_morning, night, guest_morning, guest_night, user_id)

                                message = f"Today's morning meal {'ON' if new_morning else 'OFF'}." if mode == 'just_morning' else f"Today morning {guest_morning} guest meal added"
                                flash(message, 'success')

                            elif six_am <= now <= end_day:
                                # Toggle tomorrow's morning meal
                                tomorrow = today + timedelta(days=1)

                                cursor.execute(
                                    "SELECT morning, night, guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                    (tomorrow, user_id)
                                )
                                result = cursor.fetchone()

                                current_morning = result['morning'] if result else 0
                                night = result['night'] if result else 0
                                guest_morning = result['guest_morning'] if result else 0
                                guest_night = result['guest_night'] if result else 0
                                new_morning = current_morning

                                if guest == 'guest_morning':
                                    guest_morning_input = request.form.get('guest_morning_count', 0)
                                    try:
                                        guest_morning = int(guest_morning_input)
                                        if guest_morning < 0:
                                            guest_morning = 0
                                    except (ValueError, TypeError):
                                        guest_morning = 0
                                
                                if mode == 'just_morning':
                                    new_morning = 0 if current_morning == 1 else 1

                                update_global_meals_table(username, tomorrow, new_morning, night, guest_morning, guest_night, user_id)

                                message = f"Tomorrow's morning meal {'ON' if new_morning else 'OFF'}." if mode == 'just_morning' else f"Tomorrow morning {guest_morning} guest meal added"
                                flash(message, 'success')
                            else:
                                message = "Just Morning updates are allowed from 12:00 AM–3:00 AM or 6:00 AM–11:59 PM."
                                flash(message, 'danger')
                        except Exception as e:
                            flash(f"Error updating morning meal: {str(e)}", 'danger')
                            conn.rollback()
                        
                        return redirect(url_for('dashboard'))

                    # TOMORROW NIGHT MODE OR GUEST TOMORROW NIGHT
                    elif mode == 'tomorrow_night' or guest == 'guest_tomorrow_night':
                        try:
                            tomorrow = today + timedelta(days=1)

                            cursor.execute(
                                "SELECT morning, night, guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                (tomorrow, user_id)
                            )
                            result = cursor.fetchone()

                            morning = result['morning'] if result else 0
                            current_night = result['night'] if result else 0
                            guest_morning = result['guest_morning'] if result else 0
                            guest_night = result['guest_night'] if result else 0
                            new_night = current_night

                            if guest == 'guest_tomorrow_night':
                                guest_night_input = request.form.get('guest_tomorrow_night_count', 0)
                                try:
                                    guest_night = int(guest_night_input)
                                    if guest_night < 0:
                                        guest_night = 0
                                except (ValueError, TypeError):
                                    guest_night = 0
                            
                            if mode == 'tomorrow_night':
                                new_night = 0 if current_night == 1 else 1

                            update_global_meals_table(username, tomorrow, morning, new_night, guest_morning, guest_night, user_id)

                            message = f"Tomorrow's night meal {'ON' if new_night else 'OFF'}." if mode == 'tomorrow_night' else f"Tomorrow night {guest_night} guest meal added"
                            flash(message, 'success')
                        except Exception as e:
                            flash(f"Error updating tomorrow night meal: {str(e)}", 'danger')
                            conn.rollback()
                        
                        return redirect(url_for('dashboard'))

                    # ONE CONTINUE MODE
                    elif mode == 'one_continue':
                        try:
                            part = request.form.get('one_part')

                            if part not in ['morning', 'night']:
                                flash("Please select Morning or Night for one continue mode.", 'danger')
                            else:
                                current_date = today + timedelta(days=1)
                                update_count = 0
                                
                                while current_date <= last_day_of_month:
                                    try:
                                        if part == 'morning':
                                            cursor.execute(
                                                "UPDATE `{meals}` SET morning = 1, night = 0 WHERE id = %s AND date = %s".format(meals=meals),
                                                (user_id, current_date)
                                            )
                                        else:
                                            cursor.execute(
                                                "UPDATE `{meals}` SET morning = 0, night = 1 WHERE id = %s AND date = %s".format(meals=meals),
                                                (user_id, current_date)
                                            )
                                        update_count += 1
                                    except Exception as e:
                                        flash(f"Error updating date {current_date}: {str(e)}", 'danger')
                                        conn.rollback()
                                        break
                                    
                                    current_date += timedelta(days=1)

                                conn.commit()
                                message = f"{part.capitalize()} meals updated for {update_count} days from tomorrow to end of month."
                                flash(message, 'success')
                        except Exception as e:
                            flash(f"Error in one continue mode: {str(e)}", 'danger')
                            conn.rollback()

                    # DATE MODE (Specific date update)
                    elif mode == 'date':
                        try:
                            meal_date = request.form.get('date')
                            
                            if not meal_date:
                                flash("Please select a valid date.", 'danger')
                            else:
                                try:
                                    selected_date = datetime.strptime(meal_date, '%Y-%m-%d').date()
                                except ValueError:
                                    flash("Invalid date format. Please use YYYY-MM-DD.", 'danger')
                                    return redirect(url_for('dashboard'))
                                
                                if month_start <= selected_date <= last_day_of_month and selected_date > today:
                                    morning = 1 if 'morning' in request.form else 0
                                    night = 1 if 'night' in request.form else 0
                                    
                                    cursor.execute(
                                        "UPDATE `{meals}` SET morning=%s, night=%s WHERE date=%s AND id=%s".format(meals=meals),
                                        (morning, night, selected_date, user_id)
                                    )
                                    conn.commit()
                                    flash("Meal updated successfully for selected date.", 'success')
                                else:
                                    flash("Please select a future date within this month.", 'danger')
                        except Exception as e:
                            flash(f"Error updating meal for specific date: {str(e)}", 'danger')
                            conn.rollback()

                    # FETCH DATA MODE
                    elif mode == 'fatch_data':
                        try:
                            start_date = request.form.get('start_date')
                            end_date = request.form.get('end_date')
                            
                            if not start_date or not end_date:
                                flash("Please select both start and end dates.", 'danger')
                            else:
                                try:
                                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                                except ValueError:
                                    flash("Invalid date format. Please use YYYY-MM-DD.", 'danger')
                                    return redirect(url_for('dashboard'))

                                if start_date_obj <= end_date_obj and end_date_obj <= last_day_of_month:
                                    cursor.execute("""
                                        SELECT date, morning, night, guest_morning, guest_night 
                                        FROM `{meals}`
                                        WHERE date BETWEEN %s AND %s AND id = %s
                                        ORDER BY date
                                    """.format(meals=meals), (start_date_obj, end_date_obj, user_id))
                                    
                                    meals_data = cursor.fetchall()
                                    
                                    if meals_data:
                                        message = f"Data fetched from {start_date} to {end_date}."
                                        flash(message, 'info')
                                    else:
                                        flash(f"No meal data found between {start_date} and {end_date}.", 'info')
                                else:
                                    flash("Please select valid start and end dates within this month.", 'danger')
                        except Exception as e:
                            flash(f"Error fetching meal data: {str(e)}", 'danger')
                    
                    else:
                        flash("Invalid meal mode selected.", 'danger')

                except Exception as e:
                    flash(f"Error processing meal update: {str(e)}", 'danger')
                    conn.rollback()

            # Update guest meal types (veg/non-veg)
            try:
                update_guest_meal_types(cursor, conn, meals, user_id, month_start, today, marketing)
            except Exception as e:
                flash(f"Warning: Could not update guest meal types: {str(e)}", 'info')

            # Calculate totals
            try:
                cursor.execute("""
                    SELECT 
                        SUM(morning) AS total_morning, 
                        SUM(night) AS total_night 
                    FROM `{meals}` 
                    WHERE date BETWEEN %s AND %s AND id = %s
                """.format(meals=meals), (month_start, today, user_id))

                totals = cursor.fetchone()
                total_morning = totals['total_morning'] if totals and totals['total_morning'] is not None else 0
                total_night = totals['total_night'] if totals and totals['total_night'] is not None else 0
                total = total_morning + total_night
            except Exception as e:
                flash(f"Error calculating meal totals: {str(e)}", 'danger')
                total_morning = 0
                total_night = 0
                total = 0

            # Get message from session if exists
            message = session.pop('message', None)

            # Load meals data for display
            if request.method == 'GET' or (request.method == 'POST' and request.form.get('meal_mode') != 'fatch_data'):
                try:
                    cursor.execute("""
                        SELECT * FROM `{meals}` 
                        WHERE date BETWEEN %s AND %s AND id = %s 
                        ORDER BY date
                    """.format(meals=meals), (month_start, last_day_of_month, user_id))
                    
                    meals_data = cursor.fetchall()
                    
                    if not meals_data:
                        flash("No meal data found for this month.", 'info')
                except Exception as e:
                    flash(f"Error loading meal data: {str(e)}", 'danger')
                    meals_data = []

        except Exception as e:
            flash(f"Database error: {str(e)}", 'danger')
            if conn:
                conn.rollback()
            total_morning = 0
            total_night = 0
            total = 0
            meals_data = []
        
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

        return render_template(
            'dashboard.html', 
            meals=meals_data, 
            username=username, 
            message=message, 
            total_morning=total_morning,
            total_night=total_night, 
            total=total, 
            today=today
        )

    except Exception as e:
        flash(f"Unexpected error: {str(e)}", 'danger')
        return redirect('/')

@app.route('/manager', methods=['GET', 'POST'])
def manager_dashboard():
    """
    Manager dashboard for managing meals for all users.
    Handles various meal update modes with comprehensive error handling.
    """
    try:
        # Session validation
        if 'user_id' not in session or (session.get('role') not in ['manager', 'head_manager']) or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
            flash('Unauthorized access. Please login as manager.', 'danger')
            return redirect('/')

        # Get session data with validation
        mess_code = session.get('mess_code')
        if not mess_code:
            flash('Session data missing. Please login again.', 'danger')
            return redirect('/')

        # Table names
        mess_code = str(mess_code)
        users = str(mess_code) + "_users"
        meals = str(mess_code) + "_meals"
        marketing = str(mess_code) + "_marketing"
        marketing_pending = str(mess_code) + "_marketing_pending"
        deposit = str(mess_code) + "_deposit"
        deposit_pending = str(mess_code) + "_deposit_pending"

        # Date calculations
        today = datetime.today().date()
        now = datetime.now().time()
        month_start = today.replace(day=1)
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_of_month = next_month - timedelta(days=1)

        # Database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'danger')
            return redirect('/')

        try:
            cursor = conn.cursor(dictionary=True, buffered=True)

            # Fetch active users
            try:
                cursor.execute("SELECT id, name FROM `{users}` WHERE blocked = 0".format(users=users))
                users_data = cursor.fetchall()
                
                if not users_data:
                    flash('No active users found in the system.', 'info')
                    users_data = []
                
                session['users'] = users_data
            except Exception as e:
                flash(f'Error loading users: {str(e)}', 'danger')
                users_data = []

            def update_global_meals_table(username, date_obj, morning, night, guest_morning, guest_night, user_id):
                """Update global meals table with error handling."""
                try:
                    if not username or not date_obj or user_id is None:
                        raise ValueError("Missing required parameters for meal update")
                    
                    # Safe type conversion
                    morning = int(morning) if morning is not None else 0
                    night = int(night) if night is not None else 0
                    guest_morning = guest_morning if guest_morning else 0
                    guest_night = guest_night if guest_night else 0
                    
                    cursor.execute("""
                        INSERT INTO `{meals}` (name, date, morning, night, guest_morning, guest_night, id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            morning=VALUES(morning), 
                            night=VALUES(night), 
                            guest_morning=VALUES(guest_morning), 
                            guest_night=VALUES(guest_night)
                    """.format(meals=meals), (username, date_obj, morning, night, guest_morning, guest_night, user_id))
                    
                    conn.commit()
                except ValueError as ve:
                    conn.rollback()
                    raise ValueError(f"Invalid data for meal update: {str(ve)}")
                except Exception as e:
                    conn.rollback()
                    raise Exception(f"Failed to update meals: {str(e)}")

            # Initialize variables
            selected_id = None
            username = None
            message = session.pop('message', None)
            all_user_date = session.pop('all_user_date', None)
            meals_data = session.pop('meals', [])
            mode = session.pop('mode', None)
            guest_mode = session.pop('guest_mode', None)

            # Handle GET request
            if request.method == 'GET':
                selected_id = request.args.get('id')

            # Handle POST request
            elif request.method == 'POST':
                try:
                    selected_id = request.form.get('id')
                    
                    # Validate selected_id for single user operations
                    if selected_id and selected_id != "at_a_all":
                        try:
                            user_id = int(selected_id)
                        except (ValueError, TypeError):
                            flash("Invalid user selected.", 'danger')
                            return redirect(url_for('manager_dashboard'))
                        
                        # Get username
                        try:
                            cursor.execute("SELECT name FROM `{users}` WHERE id=%s".format(users=users), (user_id,))
                            result = cursor.fetchone()
                            
                            if not result:
                                flash("Selected user does not exist.", 'danger')
                                return redirect(url_for('manager_dashboard'))
                            
                            username = result['name']
                        except Exception as e:
                            flash(f"Error fetching user details: {str(e)}", 'danger')
                            return redirect(url_for('manager_dashboard'))
                    elif selected_id != "at_a_all":
                        flash("Please select a user.", 'danger')
                        return redirect(url_for('manager_dashboard'))

                    # Get form data
                    mode = request.form.get('meal_mode')
                    session['mode'] = mode
                    guest_mode = request.form.get('guest')
                    session['guest_mode'] = guest_mode
                    
                    toggle_value = request.form.get('toggle')
                    toggle = 1 if toggle_value == 'on' else 0 if toggle_value == 'off' else None

                    # CONTINUE MODE
                    if mode == 'continue':
                        try:
                            selected_option = request.form.get('continue_option')
                            continue_guest = request.form.get('continue_guest')
                            continue_date_str = request.form.get('continue_date')
                            if continue_date_str:
                                try:
                                    continue_date = datetime.strptime(continue_date_str, '%Y-%m-%d').date()
                                except ValueError:
                                    flash("Invalid date format for continue date. Please use YYYY-MM-DD.", 'danger')
                                    return redirect(url_for('manager_dashboard'))

                            # Time boundaries
                            tonight_start = datetime.strptime('00:00', '%H:%M').time()
                            tonight_end = datetime.strptime('23:59', '%H:%M').time()
                            tomorrow_morning_start = datetime.strptime('00:00', '%H:%M').time()
                            tomorrow_morning_day_end = datetime.strptime('23:59', '%H:%M').time()
                            tomorrow_morning_day_start = datetime.strptime('00:00', '%H:%M').time()
                            tomorrow_morning_end = datetime.strptime('04:00', '%H:%M').time()

                            # TONIGHT OPTION
                            if selected_option == 'tonight' or continue_guest == 'continue_guest_night':
                                if month_start <= continue_date <= last_day_of_month:
                                    cursor.execute(
                                        "SELECT morning, guest_morning FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                        (today, user_id)
                                    )
                                    result = cursor.fetchone()
                                    preserved_morning = result['morning'] if result else 0
                                    preserved_guest_morning = result['guest_morning'] if result else 0

                                    current_day = continue_date
                                    while current_day <= last_day_of_month:
                                        if selected_option == 'tonight':
                                            if toggle is not None:
                                                morning = preserved_morning if current_day == today else toggle
                                                night = toggle
                                                
                                                cursor.execute(
                                                    "SELECT guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                                    (current_day, user_id)
                                                )
                                                result = cursor.fetchone()
                                                guest_morning = result['guest_morning'] if result else 0
                                                guest_night = result['guest_night'] if result else 0
                                                
                                                update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                            else:
                                                flash("Please select ON/OFF to continue tonight meals.", 'danger')
                                                return redirect(url_for('manager_dashboard', id=selected_id))

                                        if continue_guest == 'continue_guest_night':
                                            guest_night_input = request.form.get('continue_guest_night_count', '0')
                                            try:
                                                guest_night = int(guest_night_input) if guest_night_input else 0
                                                if guest_night < 0:
                                                    guest_night = 0
                                            except (ValueError, TypeError):
                                                guest_night = 0
                                            
                                            guest_morning = preserved_guest_morning if current_day == today else guest_night
                                            
                                            cursor.execute(
                                                "SELECT morning, night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                                (current_day, user_id)
                                            )
                                            result = cursor.fetchone()
                                            morning = result['morning'] if result else 0
                                            night = result['night'] if result else 0
                                            
                                            update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                        
                                        current_day += timedelta(days=1)
                                    
                                    message = f"{continue_date} Meals updated from tonight to {last_day_of_month}." if selected_option == 'tonight' else f"{continue_date} {guest_night} guest meal ON to {last_day_of_month}."
                                    flash(message, 'success')
                                else:
                                    flash("Invalid time or selection for Continue option.", 'danger')

                            # TOMORROW MORNING OPTION
                            elif selected_option == 'tomorrow_morning' or continue_guest == 'continue_guest_morning':
                                if month_start <= continue_date <= last_day_of_month:
                                    current_day = continue_date
                                    
                                    while current_day <= last_day_of_month:
                                        if selected_option == 'tomorrow_morning':
                                            if toggle is not None:
                                                morning = toggle
                                                night = toggle
                                                
                                                cursor.execute(
                                                    "SELECT guest_morning, guest_night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                                    (current_day, user_id)
                                                )
                                                result = cursor.fetchone()
                                                guest_morning = result['guest_morning'] if result else 0
                                                guest_night = result['guest_night'] if result else 0
                                                
                                                update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                            else:
                                                flash("Please select ON/OFF to continue tomorrow morning meals.", 'danger')
                                                return redirect(url_for('manager_dashboard', id=selected_id))
                                        
                                        if continue_guest == 'continue_guest_morning':
                                            guest_input = request.form.get('continue_guest_morning_count', '0')
                                            try:
                                                guest_morning = int(guest_input) if guest_input else 0
                                                guest_night = int(guest_input) if guest_input else 0
                                            except (ValueError, TypeError):
                                                guest_morning = 0
                                                guest_night = 0
                                            
                                            cursor.execute(
                                                "SELECT morning, night FROM `{meals}` WHERE date = %s AND id = %s".format(meals=meals),
                                                (current_day, user_id)
                                            )
                                            result = cursor.fetchone()
                                            morning = result['morning'] if result else 0
                                            night = result['night'] if result else 0
                                            
                                            update_global_meals_table(username, current_day, morning, night, guest_morning, guest_night, user_id)
                                        
                                        current_day += timedelta(days=1)
                                    
                                    message = f"Meals updated from {continue_date} morning to {last_day_of_month}." if selected_option == 'tomorrow_morning' else f"{continue_date} morning {guest_morning} guest meal ON to {last_day_of_month}."
                                    flash(message, 'success')
                                else:
                                    flash("Invalid time or selection for Continue option.", 'danger')
                        except Exception as e:
                            flash(f"Error in continue mode: {str(e)}", 'danger')
                            conn.rollback()

                    # DATE MODE
                    elif mode == 'date':
                        try:
                            date_is = request.form.get('date')
                            
                            if not date_is:
                                flash("Please select a valid date", 'danger')
                                return redirect(url_for('manager_dashboard', id=selected_id))

                            try:
                                selected_date = datetime.strptime(date_is, '%Y-%m-%d').date()
                            except ValueError:
                                flash("Invalid date format", 'danger')
                                return redirect(url_for('manager_dashboard', id=selected_id))

                            if not (month_start <= selected_date <= last_day_of_month):
                                flash("Please select a date within this month", 'danger')
                                return redirect(url_for('manager_dashboard', id=selected_id))

                            # Retrieve existing values
                            cursor.execute(
                                "SELECT * FROM `{meals}` WHERE date=%s AND id=%s".format(meals=meals),
                                (selected_date, user_id)
                            )
                            current = cursor.fetchone()

                            if not current:
                                cursor.execute(
                                    "INSERT INTO `{meals}` (id, date, morning, night, guest_morning, guest_night) VALUES (%s, %s, 0, 0, 0, 0)".format(meals=meals),
                                    (user_id, selected_date)
                                )
                                conn.commit()
                                
                                cursor.execute(
                                    "SELECT * FROM `{meals}` WHERE date=%s AND id=%s".format(meals=meals),
                                    (selected_date, user_id)
                                )
                                current = cursor.fetchone()

                            # Current values
                            morning_data = current['morning'] if current else 0
                            night_data = current['night'] if current else 0
                            morning_guest_data = current['guest_morning'] if current else 0
                            night_guest_data = current['guest_night'] if current else 0

                            # Form values
                            toggle_value = request.form.get('toggle')
                            morning_checked = 'morning' in request.form
                            night_checked = 'night' in request.form
                            M_Guest_checked = 'M_Guest' in request.form
                            N_Guest_checked = 'N_Guest' in request.form
                            M_Guest_count = request.form.get('M_Guest_count', '').strip()
                            N_Guest_count = request.form.get('N_Guest_count', '').strip()

                            toggle = 1 if toggle_value == 'on' else 0 if toggle_value == 'off' else None

                            # Update logic
                            new_morning = morning_data
                            new_night = night_data
                            new_guest_morning = morning_guest_data
                            new_guest_night = night_guest_data

                            if morning_checked and toggle is not None:
                                new_morning = toggle

                            if night_checked and toggle is not None:
                                new_night = toggle

                            if M_Guest_checked and M_Guest_count.isdigit():
                                new_guest_morning = int(M_Guest_count)

                            if N_Guest_checked and N_Guest_count.isdigit():
                                new_guest_night = int(N_Guest_count)

                            # Perform update
                            cursor.execute(
                                "UPDATE `{meals}` SET morning=%s, night=%s, guest_morning=%s, guest_night=%s WHERE date=%s AND id=%s".format(meals=meals),
                                (new_morning, new_night, new_guest_morning, new_guest_night, selected_date, user_id)
                            )
                            conn.commit()

                            flash(f"Meal data updated successfully for {selected_date}", 'success')
                            return redirect(url_for('manager_dashboard', id=selected_id))
                        except Exception as e:
                            flash(f"Error updating date-specific meal: {str(e)}", 'danger')
                            conn.rollback()

                    # ONE CONTINUE MODE
                    elif mode == 'one_continue':
                        try:
                            part = request.form.get('one_part')

                            if part not in ['morning', 'night']:
                                flash("Please select Morning or Night", 'danger')
                            else:
                                current_date = today + timedelta(days=1)
                                update_count = 0
                                
                                while current_date <= last_day_of_month:
                                    try:
                                        if part == 'morning':
                                            cursor.execute(
                                                "UPDATE `{meals}` SET morning = 1, night = 0 WHERE id = %s AND date = %s".format(meals=meals),
                                                (user_id, current_date)
                                            )
                                        else:
                                            cursor.execute(
                                                "UPDATE `{meals}` SET morning = 0, night = 1 WHERE id = %s AND date = %s".format(meals=meals),
                                                (user_id, current_date)
                                            )
                                        update_count += 1
                                    except Exception as e:
                                        flash(f"Error updating date {current_date}: {str(e)}", 'danger')
                                        conn.rollback()
                                        break
                                    
                                    current_date += timedelta(days=1)

                                conn.commit()
                                flash(f"{part.capitalize()} meals updated for {update_count} days from start to end of month.", 'success')
                        except Exception as e:
                            flash(f"Error in one continue mode: {str(e)}", 'danger')
                            conn.rollback()

                    # ALL USER MODE
                    elif mode == 'all_user' and selected_id == "at_a_all":
                        try:
                            meal_date = request.form.get('all_user_date')
                            
                            if not meal_date:
                                flash("Please select a valid date", 'danger')
                            else:
                                try:
                                    all_user_date = datetime.strptime(meal_date, '%Y-%m-%d').date()
                                    session['all_user_date'] = all_user_date
                                except ValueError:
                                    flash("Invalid date format", 'danger')
                                    return redirect(url_for('manager_dashboard', id=selected_id))
                                
                                if not (month_start <= all_user_date <= last_day_of_month):
                                    flash("Please select a date within this month", 'danger')
                                else:
                                    morning = 'morning' in request.form
                                    night = 'night' in request.form
                                    
                                    if (morning and not night):
                                        for user in users_data:
                                            try:
                                                if request.form.get('toggle') == 'on':
                                                    cursor.execute(
                                                        "UPDATE `{meals}` SET morning=%s WHERE date=%s AND id=%s".format(meals=meals),
                                                        (1, all_user_date, user['id'])
                                                    )
                                                elif request.form.get('toggle') == 'off':
                                                    cursor.execute(
                                                        "UPDATE `{meals}` SET morning=%s, guest_morning=%s WHERE date=%s AND id=%s".format(meals=meals),
                                                        (0, 0, all_user_date, user['id'])
                                                    )
                                            except Exception as e:
                                                flash(f"Error updating user {user.get('name', user['id'])}: {str(e)}", 'danger')
                                                conn.rollback()
                                                break
                                        
                                        conn.commit()
                                        message = f"Meals morning {'on' if toggle_value == 'on' else 'off'} for all users on {all_user_date}."
                                        flash(message, 'success')
                                    
                                    elif (night and not morning):
                                        for user in users_data:
                                            try:
                                                if request.form.get('toggle') == 'on':
                                                    cursor.execute(
                                                        "UPDATE `{meals}` SET night=%s WHERE date=%s AND id=%s".format(meals=meals),
                                                        (1, all_user_date, user['id'])
                                                    )
                                                elif request.form.get('toggle') == 'off':
                                                    cursor.execute(
                                                        "UPDATE `{meals}` SET night=%s, guest_night=%s WHERE date=%s AND id=%s".format(meals=meals),
                                                        (0, 0, all_user_date, user['id'])
                                                    )
                                            except Exception as e:
                                                flash(f"Error updating user {user.get('name', user['id'])}: {str(e)}", 'danger')
                                                conn.rollback()
                                                break
                                        
                                        conn.commit()
                                        message = f"Meals night {'on' if toggle_value == 'on' else 'off'} for all users on {all_user_date}."
                                        flash(message, 'success')
                                    
                                    elif morning and night:
                                        for user in users_data:
                                            try:
                                                if request.form.get('toggle') == 'on':
                                                    cursor.execute(
                                                        "UPDATE `{meals}` SET morning=%s, night=%s WHERE date=%s AND id=%s".format(meals=meals),
                                                        (1, 1, all_user_date, user['id'])
                                                    )
                                                elif request.form.get('toggle') == 'off':
                                                    cursor.execute(
                                                        "UPDATE `{meals}` SET morning=%s, night=%s, guest_morning=%s, guest_night=%s WHERE date=%s AND id=%s".format(meals=meals),
                                                        (0, 0, 0, 0, all_user_date, user['id'])
                                                    )
                                            except Exception as e:
                                                flash(f"Error updating user {user.get('name', user['id'])}: {str(e)}", 'danger')
                                                conn.rollback()
                                                break
                                        
                                        conn.commit()
                                        message = f"Meals morning and night {'on' if toggle_value == 'on' else 'off'} for all users on {all_user_date}."
                                        flash(message, 'success')
                                    else:
                                        flash("Please select Morning or Night", 'danger')
                        except Exception as e:
                            flash(f"Error in all user mode: {str(e)}", 'danger')
                            conn.rollback()

                    # FETCH DATA MODE
                    elif mode == 'fatch_data':
                        try:
                            start_date = request.form.get('start_date')
                            end_date = request.form.get('end_date')
                            
                            if not start_date or not end_date:
                                flash("Please select both start and end dates", 'danger')
                            else:
                                try:
                                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                                except ValueError:
                                    flash("Invalid date format", 'danger')
                                    return redirect(url_for('manager_dashboard', id=selected_id))
                                
                                if start_date_obj <= end_date_obj and end_date_obj <= last_day_of_month:
                                    if selected_id == "at_a_all":
                                        cursor.execute("""
                                            SELECT name, date, morning, night, guest_morning, guest_night 
                                            FROM `{meals}`
                                            WHERE date BETWEEN %s AND %s
                                            ORDER BY date
                                        """.format(meals=meals), (start_date_obj, end_date_obj))
                                    else:
                                        cursor.execute("""
                                            SELECT name, date, morning, night, guest_morning, guest_night 
                                            FROM `{meals}`
                                            WHERE date BETWEEN %s AND %s AND id = %s
                                            ORDER BY date
                                        """.format(meals=meals), (start_date_obj, end_date_obj, user_id))
                                    
                                    meals_data = cursor.fetchall()
                                    
                                    if meals_data:
                                        flash(f"Data fetched from {start_date} to {end_date}.", 'info')
                                    else:
                                        flash(f"No meal data found between {start_date} and {end_date}.", 'info')
                                else:
                                    flash("Please select valid dates within this month", 'danger')
                        except Exception as e:
                            flash(f"Error fetching meal data: {str(e)}", 'danger')
                    
                    else:
                        flash("Invalid meal mode selected.", 'danger')

                    session['meals'] = meals_data
                    session['message'] = message
                    return redirect(url_for('manager_dashboard', id=selected_id))

                except Exception as e:
                    flash(f"Error processing meal update: {str(e)}", 'danger')
                    conn.rollback()
                    return redirect(url_for('manager_dashboard'))

            # Convert all_user_date format if needed
            if all_user_date:
                try:
                    if isinstance(all_user_date, str):
                        try:
                            dt = datetime.strptime(all_user_date, '%a, %d %b %Y %H:%M:%S GMT')
                            all_user_date = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            pass
                except Exception as e:
                    pass

            # Update guest meal types
            try:
                update_guest_meal_types(cursor, conn, meals, selected_id, month_start, today, marketing)
            except Exception as e:
                flash(f"Warning: Could not update guest meal types: {str(e)}", 'info')

            # Load meals data for display
            if selected_id and selected_id != "at_a_all" and mode != 'fatch_data' and selected_id != 'register':
                try:
                    cursor.execute("""
                        SELECT * FROM `{meals}`
                        WHERE id = %s AND date BETWEEN %s AND %s
                        ORDER BY date
                    """.format(meals=meals), (selected_id, month_start, last_day_of_month))
                    
                    meals_data = cursor.fetchall()
                except Exception as e:
                    flash(f"Error loading meals data: {str(e)}", 'danger')
                    meals_data = []
            
            elif selected_id == "at_a_all" and mode == 'all_user':
                try:
                    cursor.execute("""
                        SELECT * FROM `{meals}`
                        WHERE date = %s
                        ORDER BY date
                    """.format(meals=meals), (all_user_date,))
                    
                    meals_data = cursor.fetchall()
                    session['meals'] = meals_data
                except Exception as e:
                    flash(f"Error loading meals data: {str(e)}", 'danger')
                    meals_data = []

        except Exception as e:
            flash(f"Database error: {str(e)}", 'danger')
            if conn:
                conn.rollback()
            meals_data = []
            users_data = []
        
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

        # Convert date format in meals_data
        for meal in meals_data:
            try:
                if isinstance(meal.get('date'), str):
                    try:
                        dt = datetime.strptime(meal['date'], '%a, %d %b %Y %H:%M:%S GMT')
                        meal['date'] = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        pass
            except Exception:
                pass

        # Convert selected_id to int for template
        try:
            if selected_id and selected_id != "at_a_all" and selected_id != 'register':
                selected_id = int(selected_id)
        except (ValueError, TypeError):
            selected_id = ''

        return render_template(
            'manager_dashboard.html',
            users=users_data,
            selected_id=selected_id,
            meals=meals_data,
            message=message,
            today=today
        )

    except Exception as e:
        flash(f"Unexpected error: {str(e)}", 'danger')
        return redirect('/')

@app.route('/user/marketing', methods=['GET', 'POST'])
def user_marketing_dashboard():
    """
    User marketing dashboard for submitting and viewing marketing expenses.
    Handles marketing submissions and data fetching with comprehensive error handling.
    """
    try:
        # Session validation
        if 'user_id' not in session or session.get('role') != 'user' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
            flash('Unauthorized access. Please login.', 'danger')
            return redirect('/')

        # Get session data with validation
        mess_code = session.get('mess_code')
        username = session.get('name')
        user_id = session.get('user_id')
        
        if not mess_code or not username or not user_id:
            flash('Session data missing. Please login again.', 'danger')
            return redirect('/')

        # Table names
        mess_code = str(mess_code)
        users = str(mess_code + "_users")
        meals = str(mess_code + "_meals")
        marketing = str(mess_code + "_marketing")
        marketing_pending = str(mess_code + "_marketing_pending")
        deposit = str(mess_code + "_deposit")
        deposit_pending = str(mess_code + "_deposit_pending")

        # Database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'danger')
            return redirect('/')

        try:
            cursor = conn.cursor(dictionary=True)

            # Date calculations
            today = datetime.today().date()
            month_start = today.replace(day=1)
            next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
            last_day_of_month = next_month - timedelta(days=1)

            # Get session data
            marketing_datas = session.pop('marketing_datas', [])
            meal_marketing = session.pop('meal_marketing', None)

            # Safe float conversion function
            def safe_float(value):
                """Safely convert value to float with error handling."""
                try:
                    if value is None or value == '':
                        return 0.0
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0

            # Handle POST request
            if request.method == 'POST':
                try:
                    meal_marketing = request.form.get('meal_marketing', None)
                    session['meal_marketing'] = meal_marketing

                    # SUBMIT MARKETING DATA
                    if meal_marketing != 'fetch_data':
                        date_string = request.form.get('date', '').strip()
                        
                        if not date_string:
                            flash('Please select a date.', 'danger')
                            return redirect(url_for('user_marketing_dashboard'))

                        try:
                            date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
                        except ValueError:
                            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                            return redirect(url_for('user_marketing_dashboard'))

                        if month_start <= date_obj <= last_day_of_month:
                            # Get form data with validation
                            try:
                                night = request.form.get('night', '').strip()
                                morning = request.form.get('morning', '').strip()
                                shop_money = safe_float(request.form.get('shop_money', 0))
                                veg_money = safe_float(request.form.get('veg_money', 0))
                                non_veg_money = safe_float(request.form.get('non_veg_money', 0))
                                other_money = safe_float(request.form.get('other_money', 0))
                                common_money = safe_float(request.form.get('common_money', 0))
                                note = request.form.get('note', '').strip() or 'nothing'

                                # Validate amounts
                                if shop_money < 0 or veg_money < 0 or non_veg_money < 0 or other_money < 0 or common_money < 0:
                                    flash('Amounts cannot be negative.', 'danger')
                                    return redirect(url_for('user_marketing_dashboard'))

                                # Check if at least one amount is provided
                                total_amount = shop_money + veg_money + non_veg_money + other_money + common_money
                                if total_amount <= 0:
                                    flash('Please enter at least one non-zero amount.', 'danger')
                                    return redirect(url_for('user_marketing_dashboard'))

                                # Insert into pending table
                                cursor.execute("""
                                    INSERT INTO `{marketing_pending}` 
                                    (id, username, date, morning, night, shop_money, veg_money, non_veg_money, other_money, common_money, note)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """.format(marketing_pending=marketing_pending), 
                                (user_id, username, date_obj, morning, night, shop_money, veg_money, non_veg_money, other_money, common_money, note))
                                
                                conn.commit()
                                flash('Your marketing entry has been submitted for review.', 'success')
                                
                            except Exception as e:
                                print("error:",e)
                                conn.rollback()
                                flash(f'Error submitting marketing entry: {str(e)}', 'danger')
                        else:
                            flash(f'Please select a date within this month ({month_start} to {last_day_of_month}).', 'danger')

                    # FETCH DATA MODE
                    elif meal_marketing == 'fetch_data':
                        start_date = request.form.get('start_date', '').strip()
                        end_date = request.form.get('end_date', '').strip()

                        if not start_date or not end_date:
                            flash('Please select both start and end dates.', 'danger')
                            return redirect(url_for('user_marketing_dashboard'))

                        try:
                            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                        except ValueError:
                            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                            return redirect(url_for('user_marketing_dashboard'))

                        if start_date_obj > end_date_obj:
                            flash('Start date must be before or equal to end date.', 'danger')
                            return redirect(url_for('user_marketing_dashboard'))

                        try:
                            # Fetch marketing data for the specified date range
                            cursor.execute("""
                                SELECT * FROM `{marketing}` 
                                WHERE id = %s AND date BETWEEN %s AND %s
                                ORDER BY date DESC
                            """.format(marketing=marketing), (user_id, start_date_obj, end_date_obj))
                            
                            marketing_datas = cursor.fetchall()
                            
                            if marketing_datas:
                                session['marketing_datas'] = marketing_datas
                                flash(f'Data fetched from {start_date} to {end_date}.', 'info')
                            else:
                                flash(f'No marketing data found between {start_date} and {end_date}.', 'info')
                                marketing_datas = []
                        except Exception as e:
                            flash(f'Error fetching marketing data: {str(e)}', 'danger')
                            marketing_datas = []

                    return redirect(url_for('user_marketing_dashboard'))

                except Exception as e:
                    flash(f'Error processing marketing request: {str(e)}', 'danger')
                    conn.rollback()
                    return redirect(url_for('user_marketing_dashboard'))

            # GET request - Load data
            try:
                # Fetch pending entries
                cursor.execute("""
                    SELECT * FROM `{marketing_pending}` 
                    WHERE id = %s 
                    ORDER BY date DESC
                """.format(marketing_pending=marketing_pending), (user_id,))
                
                entries = cursor.fetchall()
                
                if not entries:
                    entries = []

                # Delete accepted entries
                try:
                    cursor.execute("""
                        DELETE FROM `{marketing_pending}` 
                        WHERE status = 'accepted' AND id = %s
                    """.format(marketing_pending=marketing_pending), (user_id,))
                    
                    if cursor.rowcount > 0:
                        conn.commit()
                except Exception as e:
                    conn.rollback()
                    flash(f'Warning: Could not clean up accepted entries: {str(e)}', 'info')

                # Fetch approved marketing data if not in fetch_data mode
                if meal_marketing != 'fetch_data':
                    try:
                        cursor.execute("""
                            SELECT * FROM `{marketing}` 
                            WHERE id = %s AND date >= %s 
                            ORDER BY date DESC
                        """.format(marketing=marketing), (user_id, month_start))
                        
                        marketing_datas = cursor.fetchall()
                        
                        if not marketing_datas:
                            marketing_datas = []
                        
                        session['marketing_datas'] = marketing_datas
                    except Exception as e:
                        flash(f'Error loading marketing data: {str(e)}', 'danger')
                        marketing_datas = []

            except Exception as e:
                flash(f'Error loading marketing entries: {str(e)}', 'danger')
                entries = []
                marketing_datas = []

            # Convert date format in marketing_datas
            for marketing_data in marketing_datas:
                try:
                    if isinstance(marketing_data.get('date'), str):
                        try:
                            # Try RFC 1123 format
                            dt = datetime.strptime(marketing_data['date'], '%a, %d %b %Y %H:%M:%S GMT')
                            marketing_data['date'] = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            # Try other formats or skip
                            try:
                                dt = datetime.strptime(marketing_data['date'], '%Y-%m-%d')
                                marketing_data['date'] = dt.strftime('%Y-%m-%d')
                            except ValueError:
                                pass
                except Exception:
                    pass

            # Convert date format in entries
            for entry in entries:
                try:
                    if isinstance(entry.get('date'), str):
                        try:
                            dt = datetime.strptime(entry['date'], '%a, %d %b %Y %H:%M:%S GMT')
                            entry['date'] = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            try:
                                dt = datetime.strptime(entry['date'], '%Y-%m-%d')
                                entry['date'] = dt.strftime('%Y-%m-%d')
                            except ValueError:
                                pass
                except Exception:
                    pass

        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            if conn:
                conn.rollback()
            entries = []
            marketing_datas = []
        
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

        # Get message from session
        message = session.pop('message', None)
        print("marketing data:",marketing_datas)
        return render_template(
            'user_marketing.html', 
            entries=entries if entries else [], 
            marketing_datas=marketing_datas if marketing_datas else [], 
            username=username, 
            message=message, 
            meal_marketing=meal_marketing
        )

    except Exception as e:
        print("error:",e)
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect('/')



@app.route('/manager/marketing', methods=['GET', 'POST'])
def manager_marketing_dashboard():
    """
    Manager marketing dashboard for approving/rejecting marketing submissions.
    Handles marketing approvals and direct submissions with comprehensive error handling.
    """
    try:
        # Session validation
        if 'user_id' not in session or (session.get('role') not in ['manager', 'head_manager']) or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
            flash('Unauthorized access. Please login as manager.', 'danger')
            return redirect('/')

        # Get session data with validation
        mess_code = session.get('mess_code')
        if not mess_code:
            flash('Session data missing. Please login again.', 'danger')
            return redirect('/')

        # Table names
        mess_code = str(mess_code)
        users = str(mess_code + "_users")
        meals = str(mess_code + "_meals")
        marketing = str(mess_code + "_marketing")
        marketing_pending = str(mess_code + "_marketing_pending")
        deposit = str(mess_code + "_deposit")
        deposit_pending = str(mess_code + "_deposit_pending")

        # Date calculations
        today = datetime.today().date()
        month_start = today.replace(day=1)
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day_of_month = next_month - timedelta(days=1)

        # Get session data
        marketing_data = session.pop('marketing_data', [])
        meal_marketing = session.pop('meal_marketing', None)

        # Database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'danger')
            return redirect('/')

        try:
            cursor = conn.cursor(dictionary=True)

            # Fetch active members
            try:
                cursor.execute("SELECT id, name FROM `{users}` WHERE blocked = 0".format(users=users))
                members = cursor.fetchall()
                
                if not members:
                    flash('No active members found in the system.', 'info')
                    members = []
            except Exception as e:
                flash(f'Error fetching members: {str(e)}', 'danger')
                members = []

            # Safe float conversion function
            def safe_float(value):
                """Safely convert value to float with error handling."""
                try:
                    if value is None or value == '':
                        return 0.0
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0

            # Handle POST request
            if request.method == 'POST':
                try:
                    meal_marketing = request.form.get('meal_marketing', None) # ignor this line
                    session['meal_marketing'] = meal_marketing

                    action = request.form.get('action') #action show None value
                    entry_sl_no = request.form.get('entry_sl_no')

                    # ACCEPT/REJECT ACTIONS
                    if 'action' in request.form and 'entry_sl_no' in request.form:
                        action = request.form.get('action')
                        entry_sl_no = request.form.get('entry_sl_no')

                        if not entry_sl_no:
                            flash('Invalid entry selected.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        try:
                            entry_sl_no = int(entry_sl_no)
                        except (ValueError, TypeError):
                            flash('Invalid entry ID.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        if action == 'accept':
                            try:
                                # Fetch entry from pending table
                                cursor.execute(
                                    "SELECT * FROM `{marketing_pending}` WHERE sl_no = %s".format(marketing_pending=marketing_pending),
                                    (entry_sl_no,)
                                )
                                row = cursor.fetchone()

                                if not row:
                                    flash('Entry not found in pending list.', 'danger')
                                    return redirect(url_for('manager_marketing_dashboard'))

                                # Insert into permanent marketing table
                                cursor.execute("""
                                    INSERT INTO `{marketing}` 
                                    (sl_no, id, username, date, night, morning, shop_money, veg_money, non_veg_money, other_money, common_money, note, status)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """.format(marketing=marketing), 
                                (row['sl_no'], row['id'], row['username'], row['date'], row['night'], row['morning'], 
                                 row['shop_money'], row['veg_money'], row['non_veg_money'], row['other_money'], 
                                 row['common_money'], row.get('note', 'nothing'), 'accepted'))

                                # Update status in pending table
                                cursor.execute(
                                    "UPDATE `{marketing_pending}` SET status = 'accepted' WHERE sl_no = %s".format(marketing_pending=marketing_pending),
                                    (entry_sl_no,)
                                )

                                conn.commit()
                                flash('Marketing entry accepted successfully.', 'success')

                            except Exception as e:
                                conn.rollback()
                                flash(f'Error accepting entry: {str(e)}', 'danger')

                        elif action == 'reject':
                            try:
                                # Delete from pending table
                                cursor.execute(
                                    "DELETE FROM `{marketing_pending}` WHERE sl_no = %s".format(marketing_pending=marketing_pending),
                                    (entry_sl_no,)
                                )

                                conn.commit()
                                flash('Marketing entry rejected and removed.', 'success')

                            except Exception as e:
                                conn.rollback()
                                flash(f'Error rejecting entry: {str(e)}', 'danger')
                        else:
                            flash('Invalid action selected.', 'danger')

                        return redirect(url_for('manager_marketing_dashboard'))

                    # DIRECT MARKETING SUBMISSION
                    elif meal_marketing != 'fetch_data':
                        date_string = request.form.get('date', '').strip()

                        if not date_string:
                            flash('Please select a date.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        try:
                            date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
                        except ValueError:
                            flash('Invalid date format.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        if not (month_start <= date_obj <= last_day_of_month):
                            flash(f'Please select a date within this month ({month_start} to {last_day_of_month}).', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        user_id = request.form.get('id', '').strip()

                        if not user_id:
                            flash('Please select a user.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        try:
                            user_id = int(user_id)
                        except (ValueError, TypeError):
                            flash('Invalid user selected.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        # Fetch username
                        try:
                            cursor.execute("SELECT name FROM `{users}` WHERE id = %s".format(users=users), (user_id,))
                            user_result = cursor.fetchone()

                            if not user_result:
                                flash('Selected user not found.', 'danger')
                                return redirect(url_for('manager_marketing_dashboard'))

                            username = user_result['name']
                        except Exception as e:
                            flash(f'Error fetching user details: {str(e)}', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        # Get form data with validation
                        night = request.form.get('night', '').strip()
                        morning = request.form.get('morning', '').strip()
                        shop_money = safe_float(request.form.get('shop_money', 0))
                        veg_money = safe_float(request.form.get('veg_money', 0))
                        non_veg_money = safe_float(request.form.get('nonveg_money', 0))
                        other_money = safe_float(request.form.get('other_money', 0))
                        common_money = safe_float(request.form.get('common_money', 0))
                        note = request.form.get('note', '').strip() or 'nothing'

                        # Validate amounts
                        if shop_money < 0 or veg_money < 0 or non_veg_money < 0 or other_money < 0 or common_money < 0:
                            flash('Amounts cannot be negative.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        # Check if at least one amount is provided
                        total_amount = shop_money + veg_money + non_veg_money + other_money + common_money
                        if total_amount <= 0:
                            flash('Please enter at least one non-zero amount.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        # Insert into marketing table
                        try:
                            cursor.execute("""
                                INSERT INTO `{marketing}` 
                                (id, username, date, morning, night, shop_money, veg_money, non_veg_money, other_money, common_money, note, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """.format(marketing=marketing), 
                            (user_id, username, date_obj, morning, night, shop_money, veg_money, non_veg_money, other_money, common_money, note, 'accepted'))

                            conn.commit()
                            flash('Marketing entry has been added successfully.', 'success')

                        except Exception as e:
                            conn.rollback()
                            flash(f'Error adding marketing entry: {str(e)}', 'danger')

                        return redirect(url_for('manager_marketing_dashboard'))

                    # FETCH DATA MODE
                    elif meal_marketing == 'fetch_data':
                        start_date = request.form.get('start_date', '').strip()
                        end_date = request.form.get('end_date', '').strip()

                        if not start_date or not end_date:
                            flash('Please select both start and end dates.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        try:
                            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                        except ValueError:
                            flash('Invalid date format.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        if start_date_obj > end_date_obj:
                            flash('Start date must be before or equal to end date.', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        if end_date_obj > last_day_of_month:
                            flash(f'End date must be within this month (up to {last_day_of_month}).', 'danger')
                            return redirect(url_for('manager_marketing_dashboard'))

                        try:
                            cursor.execute("""
                                SELECT * FROM `{marketing}` 
                                WHERE date BETWEEN %s AND %s 
                                ORDER BY date DESC
                            """.format(marketing=marketing), (start_date_obj, end_date_obj))

                            marketing_data = cursor.fetchall()

                            if marketing_data:
                                session['marketing_data'] = marketing_data
                                flash(f'Data fetched from {start_date} to {end_date}.', 'info')
                            else:
                                flash(f'No marketing data found between {start_date} and {end_date}.', 'info')
                                marketing_data = []

                        except Exception as e:
                            flash(f'Error fetching marketing data: {str(e)}', 'danger')
                            marketing_data = []

                        return redirect(url_for('manager_marketing_dashboard'))

                    else:
                        flash('Please select a valid action.', 'danger')
                        return redirect(url_for('manager_marketing_dashboard'))

                except Exception as e:
                    flash(f'Error processing request: {str(e)}', 'danger')
                    conn.rollback()
                    return redirect(url_for('manager_marketing_dashboard'))

            # GET request - Load data
            if meal_marketing != 'fetch_data':
                try:
                    cursor.execute(
                        "SELECT * FROM `{marketing}` WHERE date >= %s ORDER BY date DESC".format(marketing=marketing),
                        (month_start,)
                    )
                    marketing_data = cursor.fetchall()

                    if not marketing_data:
                        marketing_data = []

                except Exception as e:
                    flash(f'Error fetching marketing data: {str(e)}', 'danger')
                    marketing_data = []

            # Fetch pending entries
            try:
                cursor.execute(
                    "SELECT * FROM `{marketing_pending}` WHERE status = 'pending' ORDER BY date DESC".format(marketing_pending=marketing_pending)
                )
                pending_entries = cursor.fetchall()

                if not pending_entries:
                    pending_entries = []

            except Exception as e:
                flash(f'Error fetching pending entries: {str(e)}', 'danger')
                pending_entries = []

        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
            if conn:
                conn.rollback()
            marketing_data = []
            pending_entries = []
            members = []

        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

        # Convert date format in marketing_data
        for data in marketing_data:
            try:
                if isinstance(data.get('date'), str):
                    try:
                        dt = datetime.strptime(data['date'], '%a, %d %b %Y %H:%M:%S GMT')
                        data['date'] = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            dt = datetime.strptime(data['date'], '%Y-%m-%d')
                            data['date'] = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            pass
            except Exception:
                pass

        # Convert date format in pending_entries
        for entry in pending_entries:
            try:
                if isinstance(entry.get('date'), str):
                    try:
                        dt = datetime.strptime(entry['date'], '%a, %d %b %Y %H:%M:%S GMT')
                        entry['date'] = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            dt = datetime.strptime(entry['date'], '%Y-%m-%d')
                            entry['date'] = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            pass
            except Exception:
                pass

        # Get message from session
        message = session.pop('message', None)

        return render_template(
            'manager_marketing.html', 
            pending_entries=pending_entries if pending_entries else [], 
            marketing_data=marketing_data if marketing_data else [], 
            members=members, 
            messages=message, 
            meal_marketing=meal_marketing
        )

    except Exception as e:
        print("error:",e)
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect('/')


@app.route('/user/deposit', methods=['GET', 'POST'])
def user_deposit_dashboard():
    # Session validation
    if 'user_id' not in session or session.get('role') != 'user' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')

    conn = None
    cursor = None
    
    try:
        # Get mess code and table names
        mess_code = session.get('mess_code')
        if not mess_code:
            flash('Mess code not found in session', 'error')
            return redirect('/')
        
        mess_code = str(mess_code)
        users = str((mess_code) + "_users")
        meals = str((mess_code) + "_meals")
        marketing = str((mess_code) + "_marketing")
        marketing_pending = str((mess_code) + "_marketing_pending")
        deposit = str((mess_code) + "_deposit")
        deposit_pending = str((mess_code) + "_deposit_pending")

        # Get database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'error')
            return redirect('/')
        
        cursor = conn.cursor(dictionary=True)

        # Get user session data
        username = session.get('name')
        user_id = session.get('user_id')
        
        if not username or not user_id:
            flash('User session data not found', 'error')
            return redirect('/')

        # Get today's date and month start
        try:
            today = datetime.today().date()
            month_start = today.replace(day=1)
        except Exception as date_err:
            print(f"Error getting current date: {str(date_err)}")
            flash('Error processing date. Please try again.', 'error')
            return redirect('/')

        # Get session messages and data
        message = session.pop('message', None)
        deposit_datas = session.pop('deposit_datas', [])
        meal_deposit = session.pop('meal_deposit', None)

        if request.method == 'POST':
            try:
                meal_deposit = request.form.get('meal_deposit', None)
                
                if not meal_deposit:
                    flash('Please select an option (Deposit Form or Fetch Data)', 'error')
                    return redirect(url_for('user_deposit_dashboard'))
                
                session['meal_deposit'] = meal_deposit
                print("meal_deposit:", meal_deposit)

                # Handle deposit submission
                if meal_deposit != 'fetch_data':
                    date_string = request.form.get('date', '').strip()
                    
                    if not date_string:
                        message = "Please select a date for your deposit."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Validate and parse date
                    try:
                        date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
                    except (ValueError, TypeError) as date_err:
                        print(f"Date parsing error: {str(date_err)}")
                        message = "Invalid date format. Please select a valid date."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Validate date range
                    if not (month_start <= date_obj <= today):
                        message = "Please select a date that is today or earlier."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Get and validate money amount
                    money = request.form.get('money', '').strip()
                    if not money:
                        message = "Please enter the deposit amount."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    try:
                        money = float(money)
                        if money <= 0:
                            message = "Deposit amount must be greater than zero."
                            session['message'] = message
                            return redirect(url_for('user_deposit_dashboard'))
                    except (ValueError, TypeError):
                        message = "Invalid deposit amount. Please enter a valid number."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Get payment method
                    payment_by = request.form.get('payment_by', '').strip()
                    if not payment_by or payment_by == 'selected':
                        message = "Please select a payment method."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Get note (optional)
                    other_note = request.form.get('other_note', '').strip()
                    if not other_note:
                        other_note = 'nothing'
                    
                    # Sanitize note length
                    if len(other_note) > 255:
                        other_note = other_note[:255]

                    # Insert deposit entry
                    try:
                        cursor.execute("""
                            INSERT INTO {deposit_pending} (id, name, date, money, payment_by, note)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """.format(deposit_pending=deposit_pending), (user_id, username, date_obj, money, payment_by, other_note))
                        conn.commit()
                        message = "Your deposit entry has been submitted for review."
                        session['message'] = message
                    except mysql.connector.Error as db_err:
                        conn.rollback()
                        print(f"Database error inserting deposit: {str(db_err)}")
                        message = "Error submitting deposit entry. Please try again."
                        session['message'] = message
                    
                    return redirect(url_for('user_deposit_dashboard'))

                # Handle fetch data request
                elif meal_deposit == 'fetch_data':
                    start_date = request.form.get('start_date', '').strip()
                    end_date = request.form.get('end_date', '').strip()
                    
                    if not start_date or not end_date:
                        message = "Please select both start date and end date."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Validate and parse dates
                    try:
                        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    except (ValueError, TypeError) as date_err:
                        print(f"Date parsing error: {str(date_err)}")
                        message = "Invalid date format. Please select valid dates."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Validate date range
                    if start_date_obj > end_date_obj:
                        message = "Start date cannot be after end date."
                        session['message'] = message
                        return redirect(url_for('user_deposit_dashboard'))
                    
                    # Fetch deposit data for the specified date range
                    try:
                        cursor.execute("""
                            SELECT * FROM {deposit} WHERE id = %s AND date BETWEEN %s AND %s
                        """.format(deposit=deposit), (user_id, start_date_obj, end_date_obj))
                        deposit_datas = cursor.fetchall()
                        
                        if not deposit_datas:
                            deposit_datas = []
                        
                        session['deposit_datas'] = deposit_datas
                        message = f"Data fetched from {start_date} to {end_date}."
                        session['message'] = message
                    except mysql.connector.Error as db_err:
                        print(f"Database error fetching deposit data: {str(db_err)}")
                        message = "Error fetching deposit data. Please try again."
                        session['message'] = message
                        deposit_datas = []
                    
                    return redirect(url_for('user_deposit_dashboard'))

            except mysql.connector.Error as db_err:
                if conn:
                    conn.rollback()
                print(f"Database error in POST request: {str(db_err)}")
                flash('Database error occurred. Please try again.', 'error')
                return redirect(url_for('user_deposit_dashboard'))
            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"Unexpected error in POST request: {str(e)}")
                flash('An unexpected error occurred. Please try again.', 'error')
                return redirect(url_for('user_deposit_dashboard'))

        # GET request handling
        try:
            # Fetch pending entries
            cursor.execute("""
                SELECT * FROM {deposit_pending} WHERE id = %s ORDER BY date DESC
            """.format(deposit_pending=deposit_pending), (user_id,))
            entries = cursor.fetchall()
            
            if not entries:
                entries = []

            # Clean up accepted entries
            for entry in entries:
                if entry and entry.get('status') == 'accepted':
                    try:
                        cursor.execute("""
                            DELETE FROM {deposit_pending} WHERE status = 'accepted'
                        """.format(deposit_pending=deposit_pending))
                        conn.commit()
                    except mysql.connector.Error as db_err:
                        conn.rollback()
                        print(f"Error deleting accepted entries: {str(db_err)}")

            # Fetch deposit data if not from fetch_data request
            if meal_deposit != 'fetch_data':
                try:
                    cursor.execute("""
                        SELECT * FROM {deposit} WHERE id = %s AND date >= %s ORDER BY date DESC
                    """.format(deposit=deposit), (user_id, month_start))
                    deposit_datas = cursor.fetchall()
                    
                    if not deposit_datas:
                        deposit_datas = []
                except mysql.connector.Error as db_err:
                    print(f"Error fetching deposit data: {str(db_err)}")
                    deposit_datas = []

            # Format dates in deposit_datas
            for deposit_data in deposit_datas:
                if deposit_data and 'date' in deposit_data and isinstance(deposit_data['date'], str):
                    try:
                        # Convert RFC 1123 -> datetime -> YYYY-MM-DD
                        dt = datetime.strptime(deposit_data['date'], '%a, %d %b %Y %H:%M:%S GMT')
                        deposit_data['date'] = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        pass  # Not a date string, skip
                    except Exception as format_err:
                        print(f"Error formatting date: {str(format_err)}")
                        pass

        except mysql.connector.Error as db_err:
            print(f"Database error in GET request: {str(db_err)}")
            flash('Error loading deposit data. Please try again.', 'error')
            entries = []
            deposit_datas = []
        except Exception as e:
            print(f"Unexpected error in GET request: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'error')
            entries = []
            deposit_datas = []

        return render_template('user_deposit.html', 
                             entries=entries, 
                             deposit_datas=deposit_datas, 
                             username=username, 
                             message=message)

    except mysql.connector.Error as db_err:
        if conn:
            conn.rollback()
        print(f"Database error in /user/deposit: {str(db_err)}")
        flash('Database error occurred. Please try again later.', 'error')
        return redirect('/')
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Unexpected error in /user/deposit: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect('/')
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()


@app.route('/manager/deposit', methods=['GET', 'POST'])
def manager_deposit_dashboard():
    # Session validation
    if 'user_id' not in session or session.get('role') != 'manager' and session.get('role') != 'head_manager' or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')

    conn = None
    cursor = None
    
    try:
        # Get mess code and validate
        mess_code = session.get('mess_code')
        if not mess_code:
            flash('Mess code not found in session', 'error')
            return redirect('/')
        
        mess_code = str(mess_code)
        users = str((mess_code) + "_users")
        meals = str((mess_code) + "_meals")
        marketing = str((mess_code) + "_marketing")
        marketing_pending = str((mess_code) + "_marketing_pending")
        deposit = str((mess_code) + "_deposit")
        deposit_pending = str((mess_code) + "_deposit_pending")

        # Get today's date and month start
        try:
            today = datetime.today().date()
            month_start = today.replace(day=1)
        except Exception as date_err:
            print(f"Error getting current date: {str(date_err)}")
            flash('Error processing date. Please try again.', 'error')
            return redirect('/')

        # Get session data
        message = session.pop('message', None)
        deposit_data = session.pop('deposit_data', [])
        meal_deposit = session.pop('meal_deposit', None)

        # Get database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'error')
            return redirect('/')
        
        cursor = conn.cursor(dictionary=True)

        # Fetch active members
        members = []
        try:
            cursor.execute("SELECT * FROM {users} WHERE blocked = 0".format(users=users))
            members = cursor.fetchall()
            if not members:
                members = []
        except mysql.connector.Error as db_err:
            print(f"Database error fetching users: {str(db_err)}")
            message = "Error fetching users. Please try again."
            session['message'] = message
            members = []
        except Exception as e:
            print(f"Unexpected error fetching users: {str(e)}")
            message = "Error fetching users: {}".format(e)
            session['message'] = message
            members = []

        if request.method == 'POST':
            try:
                meal_deposit = request.form.get('meal_deposit', None)
                session['meal_deposit'] = meal_deposit

                # Handle approval/rejection actions
                if 'action' in request.form and 'entry_sl_no' in request.form:
                    action = request.form.get('action', '').strip()
                    entry_sl_no = request.form.get('entry_sl_no', '').strip()

                    # Validate inputs
                    if not action or not entry_sl_no:
                        message = "Invalid action or entry number."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Validate action value
                    if action not in ['accept', 'reject']:
                        message = "Invalid action specified."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Convert entry_sl_no to integer safely
                    try:
                        entry_sl_no = int(entry_sl_no)
                    except (ValueError, TypeError):
                        message = "Invalid entry number format."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    if action == 'accept':
                        existing_row = None
                        try:
                            cursor.execute("""
                                SELECT * FROM {deposit_pending} WHERE SL_no = %s
                            """.format(deposit_pending=deposit_pending), (entry_sl_no,))
                            existing_row = cursor.fetchone()
                        except mysql.connector.Error as db_err:
                            print(f"Database error fetching from deposit_pending: {str(db_err)}")
                            message = "Error fetching deposit entry. Please try again."
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))
                        except Exception as e:
                            print(f"Unexpected error fetching from deposit_pending: {str(e)}")
                            message = "Error fetching from deposit_pending: {}".format(e)
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))

                        if existing_row:
                            row = None
                            try:
                                cursor.execute("""
                                    SELECT * FROM {deposit_pending} WHERE SL_no = %s
                                """.format(deposit_pending=deposit_pending), (entry_sl_no,))
                                row = cursor.fetchone()
                            except mysql.connector.Error as db_err:
                                print(f"Database error re-fetching from deposit_pending: {str(db_err)}")
                                message = "Error processing deposit entry. Please try again."
                                session['message'] = message
                                conn.rollback()
                                return redirect(url_for('manager_deposit_dashboard'))
                            except Exception as e:
                                print(f"Unexpected error re-fetching from deposit_pending: {str(e)}")
                                message = "Error fetching from deposit_pending: {}".format(e)
                                session['message'] = message
                                conn.rollback()
                                return redirect(url_for('manager_deposit_dashboard'))

                            if row:
                                # Validate row data
                                if not all(key in row for key in ['SL_no', 'id', 'name', 'date', 'money', 'payment_by', 'note']):
                                    message = "Incomplete deposit entry data."
                                    session['message'] = message
                                    conn.rollback()
                                    return redirect(url_for('manager_deposit_dashboard'))

                                try:
                                    cursor.execute("""
                                        INSERT INTO {deposit} (SL_no, id, name, date, money, payment_by, note, status)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """.format(deposit=deposit), (
                                        row['SL_no'], 
                                        row['id'], 
                                        row['name'], 
                                        row['date'], 
                                        row['money'], 
                                        row['payment_by'], 
                                        row['note'], 
                                        'accepted'
                                    ))
                                except mysql.connector.Error as db_err:
                                    print(f"Database error inserting into deposit table: {str(db_err)}")
                                    message = "Error accepting deposit entry. Please try again."
                                    session['message'] = message
                                    conn.rollback()
                                    return redirect(url_for('manager_deposit_dashboard'))
                                except Exception as e:
                                    print(f"Unexpected error inserting into deposit table: {str(e)}")
                                    message = "Error inserting into deposit table: {}".format(e)
                                    session['message'] = message
                                    conn.rollback()
                                    return redirect(url_for('manager_deposit_dashboard'))
                        else:
                            message = "Deposit entry not found."
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))

                        # Update pending entry status
                        try:
                            cursor.execute("""
                                UPDATE {deposit_pending} SET status = 'accepted' WHERE SL_no = %s
                            """.format(deposit_pending=deposit_pending), (entry_sl_no,))
                            conn.commit()
                            message = "Deposit entry accepted successfully."
                            session['message'] = message
                        except mysql.connector.Error as db_err:
                            print(f"Database error updating deposit_pending status: {str(db_err)}")
                            message = "Error updating deposit status. Please try again."
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))
                        except Exception as e:
                            print(f"Unexpected error updating deposit_pending status: {str(e)}")
                            message = "Error updating deposit_pending status: {}".format(e)
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))

                    elif action == 'reject':
                        try:
                            # Verify entry exists before deleting
                            cursor.execute("""
                                SELECT SL_no FROM {deposit_pending} WHERE SL_no = %s
                            """.format(deposit_pending=deposit_pending), (entry_sl_no,))
                            entry_exists = cursor.fetchone()

                            if not entry_exists:
                                message = "Deposit entry not found."
                                session['message'] = message
                                return redirect(url_for('manager_deposit_dashboard'))

                            cursor.execute("""
                                DELETE FROM {deposit_pending} WHERE SL_no = %s
                            """.format(deposit_pending=deposit_pending), (entry_sl_no,))
                            conn.commit()
                            message = "Deposit entry rejected successfully."
                            session['message'] = message
                        except mysql.connector.Error as db_err:
                            print(f"Database error deleting from deposit_pending: {str(db_err)}")
                            message = "Error rejecting deposit entry. Please try again."
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))
                        except Exception as e:
                            print(f"Unexpected error deleting from deposit_pending: {str(e)}")
                            message = "Error deleting from deposit_pending: {}".format(e)
                            session['message'] = message
                            conn.rollback()
                            return redirect(url_for('manager_deposit_dashboard'))

                    return redirect(url_for('manager_deposit_dashboard'))

                # Handle deposit submission
                elif meal_deposit == 'yes_deposit':
                    date_string = request.form.get('date', '').strip()
                    
                    if not date_string:
                        message = "Please select a date for the deposit."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Validate and parse date
                    try:
                        date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
                    except (ValueError, TypeError) as date_err:
                        print(f"Date parsing error: {str(date_err)}")
                        message = "Invalid date format. Please select a valid date."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Validate date range
                    if not (month_start <= date_obj <= today):
                        message = "Please select a date that is today or earlier."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Get and validate user ID
                    user_id = request.form.get('id', '').strip()
                    if not user_id:
                        message = "Please select a user."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Fetch username
                    username = None
                    try:
                        cursor.execute("""
                            SELECT name FROM {users} WHERE id = %s
                        """.format(users=users), (user_id,))
                        user_record = cursor.fetchone()
                        
                        if not user_record:
                            message = "User not found."
                            session['message'] = message
                            return redirect(url_for('manager_deposit_dashboard'))
                        
                        username = user_record.get('name')
                        if not username:
                            message = "Username not found."
                            session['message'] = message
                            return redirect(url_for('manager_deposit_dashboard'))
                    except mysql.connector.Error as db_err:
                        print(f"Database error fetching username: {str(db_err)}")
                        message = "Error fetching user information. Please try again."
                        session['message'] = message
                        conn.rollback()
                        return redirect(url_for('manager_deposit_dashboard'))
                    except Exception as e:
                        print(f"Unexpected error fetching username: {str(e)}")
                        message = "Error fetching username: {}".format(e)
                        session['message'] = message
                        conn.rollback()
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Get and validate money amount
                    money = request.form.get('money', '').strip()
                    if not money:
                        message = "Please enter the deposit amount."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    try:
                        money = float(money)
                        if money <= 0:
                            message = "Deposit amount must be greater than zero."
                            session['message'] = message
                            return redirect(url_for('manager_deposit_dashboard'))
                    except (ValueError, TypeError):
                        message = "Invalid deposit amount. Please enter a valid number."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Get and validate payment method
                    payment_by = request.form.get('payment_by', '').strip()
                    if not payment_by or payment_by == 'selected' or payment_by == '':
                        message = "Please select a payment method."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Get note (optional)
                    other_note = request.form.get('other_note', '').strip()
                    if not other_note:
                        other_note = 'nothing'
                    
                    # Sanitize note length
                    if len(other_note) > 255:
                        other_note = other_note[:255]

                    # Insert deposit entry
                    try:
                        cursor.execute("""
                            INSERT INTO {deposit} (id, name, date, money, payment_by, note, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """.format(deposit=deposit), (user_id, username, date_obj, money, payment_by, other_note, 'accepted'))
                        conn.commit()
                        message = "Deposit entry has been added successfully."
                        session['message'] = message
                    except mysql.connector.Error as db_err:
                        conn.rollback()
                        print(f"Database error inserting into deposit table: {str(db_err)}")
                        message = "An error occurred while adding the deposit entry. Please try again."
                        session['message'] = message
                    except Exception as e:
                        conn.rollback()
                        print(f"Unexpected error inserting into deposit table: {str(e)}")
                        message = "An error occurred while adding the deposit entry."
                        session['message'] = message

                    return redirect(url_for('manager_deposit_dashboard'))

                # Handle fetch data request
                elif meal_deposit == 'fetch_data':
                    start_date = request.form.get('start_date', '').strip()
                    end_date = request.form.get('end_date', '').strip()

                    if not start_date or not end_date:
                        message = "Please select both start date and end date."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Validate and parse dates
                    try:
                        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    except (ValueError, TypeError) as date_err:
                        print(f"Date parsing error: {str(date_err)}")
                        message = "Invalid date format. Please select valid dates."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Validate date range
                    if start_date_obj > end_date_obj:
                        message = "Start date cannot be after end date."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    if end_date_obj > today:
                        message = "Please select a date within this month or valid start and end dates."
                        session['message'] = message
                        return redirect(url_for('manager_deposit_dashboard'))

                    # Fetch deposit data for the specified date range
                    try:
                        cursor.execute("""
                            SELECT * FROM {deposit} WHERE date BETWEEN %s AND %s ORDER BY date DESC
                        """.format(deposit=deposit), (start_date_obj, end_date_obj))
                        deposit_data = cursor.fetchall()

                        if not deposit_data:
                            deposit_data = []
                            message = f"No deposit data found from {start_date} to {end_date}."
                        else:
                            message = f"Data fetched from {start_date} to {end_date}."

                        session['deposit_data'] = deposit_data
                        session['message'] = message
                    except mysql.connector.Error as db_err:
                        print(f"Database error fetching deposit data: {str(db_err)}")
                        message = "Error fetching deposit data. Please try again."
                        session['message'] = message
                        deposit_data = []
                    except Exception as e:
                        print(f"Unexpected error fetching deposit data: {str(e)}")
                        message = "Error fetching deposit data: {}".format(e)
                        session['message'] = message
                        deposit_data = []

                    return redirect(url_for('manager_deposit_dashboard'))

                else:
                    # Handle the case where neither 'action' nor valid meal_deposit is present
                    message = "Please try again."
                    session['message'] = message
                    return redirect(url_for('manager_deposit_dashboard'))

            except mysql.connector.Error as db_err:
                if conn:
                    conn.rollback()
                print(f"Database error in POST request: {str(db_err)}")
                flash('Database error occurred. Please try again.', 'error')
                return redirect(url_for('manager_deposit_dashboard'))
            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"Unexpected error in POST request: {str(e)}")
                flash('An unexpected error occurred. Please try again.', 'error')
                return redirect(url_for('manager_deposit_dashboard'))

        # GET request handling
        try:
            # Fetch deposit data if not from fetch_data request
            if meal_deposit != 'fetch_data':
                try:
                    cursor.execute("""
                        SELECT * FROM {deposit} WHERE date >= %s ORDER BY date DESC
                    """.format(deposit=deposit), (month_start,))
                    deposit_data = cursor.fetchall()

                    if not deposit_data:
                        deposit_data = []
                except mysql.connector.Error as db_err:
                    print(f"Database error fetching deposit data: {str(db_err)}")
                    message = "Error fetching deposit data. Please try again."
                    session['message'] = message
                    deposit_data = []
                except Exception as e:
                    print(f"Unexpected error fetching deposit data: {str(e)}")
                    message = "Error fetching deposit data: {}".format(e)
                    session['message'] = message
                    deposit_data = []

            # Fetch pending entries
            pending_entries = []
            try:
                cursor.execute("""
                    SELECT * FROM {deposit_pending} ORDER BY date DESC
                """.format(deposit_pending=deposit_pending))
                pending_entries = cursor.fetchall()

                if not pending_entries:
                    pending_entries = []
            except mysql.connector.Error as db_err:
                print(f"Database error fetching pending entries: {str(db_err)}")
                message = "Error fetching pending entries. Please try again."
                session['message'] = message
                pending_entries = []
            except Exception as e:
                print(f"Unexpected error fetching pending entries: {str(e)}")
                message = "Error fetching pending entries: {}".format(e)
                session['message'] = message
                pending_entries = []

            # Format dates in deposit_data
            if deposit_data:
                for data in deposit_data:
                    if data and 'date' in data and isinstance(data['date'], str):
                        try:
                            # Convert RFC 1123 -> datetime -> YYYY-MM-DD
                            dt = datetime.strptime(data['date'], '%a, %d %b %Y %H:%M:%S GMT')
                            data['date'] = dt.strftime('%Y-%m-%d')
                        except ValueError:
                            pass  # Not a date string, skip
                        except Exception as format_err:
                            print(f"Error formatting date: {str(format_err)}")
                            pass

        except mysql.connector.Error as db_err:
            print(f"Database error in GET request: {str(db_err)}")
            flash('Error loading deposit data. Please try again.', 'error')
            deposit_data = []
            pending_entries = []
        except Exception as e:
            print(f"Unexpected error in GET request: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'error')
            deposit_data = []
            pending_entries = []

        return render_template('manager_deposit.html', 
                             members=members, 
                             pending_entries=pending_entries, 
                             deposit_data=deposit_data, 
                             message=message)

    except mysql.connector.Error as db_err:
        if conn:
            conn.rollback()
        print(f"Database error in /manager/deposit: {str(db_err)}")
        flash('Database error occurred. Please try again later.', 'error')
        return redirect('/')
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Unexpected error in /manager/deposit: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect('/')
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

# this function are called two times first user meal amount (line no 4255) and second time in manager meal amount (line no 4442) to get previous month calculation date for meal charge calculation and update

def get_previous_month_date(cursor, variables, today, previous_month_last_day, last_day_of_month):
    try:
        cursor.execute("SELECT meal_calculation_date FROM `{variables}` ORDER BY meal_calculation_date DESC LIMIT 2".format(variables=variables))
        result = cursor.fetchall()
        print("Fetched calculation dates:", result)
        if result:
            latest_calculation_date = result[0]['meal_calculation_date'] 
            previous_month_calculation_date = result[1]['meal_calculation_date'] if len(result) > 1 else None
        
    except mysql.connector.Error as db_err:
        print(f"Database error fetching calculation date: {str(db_err)}")
    if latest_calculation_date > today:
        previous_calculation_date = previous_month_calculation_date
        previous_variable_date = previous_month_last_day
    else:
        previous_calculation_date = latest_calculation_date
        previous_variable_date = last_day_of_month
    return previous_calculation_date, latest_calculation_date, previous_variable_date

@app.route('/meal_amount', methods=['GET', 'POST'])
def user_meal_amount(unknow=None, know=None):
    # Session validation
    if 'user_id' not in session or session.get('mess_blocked') == 1:
        return redirect('/')
    
    conn = None
    cursor = None

    do_not_entry_value = request.args.get('DoNotEntery', 0) 
    do_not_entry_value = int(do_not_entry_value)
    print(f"The value is: {do_not_entry_value}")
    try:
        # Get mess code and validate
        mess_code = session.get('mess_code')
        if not mess_code:
            flash('Mess code not found in session', 'error')
            return redirect('/')
        
        mess_code = str(mess_code)
        users = str((mess_code) + "_users")
        meals = str((mess_code) + "_meals")
        marketing = str((mess_code) + "_marketing")
        marketing_pending = str((mess_code) + "_marketing_pending")
        deposit = str((mess_code) + "_deposit")
        deposit_pending = str((mess_code) + "_deposit_pending")
        meal_charge = str((mess_code) + "_meal_charge")
        variables = str((mess_code) + "_variables")

        # Get user session data
        username = session.get('name')
        user_id = session.get('user_id')

        if request.method == 'POST' and request.form.get('SelectedId') and request.form.get('manager_to_user'):
            user_id = request.form.get('SelectedId')
        
        if not username or not user_id:
            flash('User session data not found', 'error')
            return redirect('/')

        # Get date information
        try:
            today = datetime.today().date()
            now = datetime.now().time()
            month_start = today.replace(day=1)
            next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
            last_day_of_month = next_month - timedelta(days=1)
            previous_month_last_day = month_start - timedelta(days=1)
        except Exception as date_err:
            print(f"Error calculating dates: {str(date_err)}")
            flash('Error processing dates. Please try again.', 'error')
            return redirect('/')

        # Get database connection
        conn = get_db()
        if not conn:
            flash('Database connection failed. Please try again.', 'error')
            return redirect('/')
        
        cursor = conn.cursor(dictionary=True, buffered=True)

        search_meal_charge_data = session.pop('search_meal_charge_data', None)
        search_variable_data = session.pop('search_variable_data', None)

        # Fetch active users
        active_users = []
        try:
            cursor.execute("SELECT id, name FROM `{users}` WHERE blocked = 0".format(users=users))
            active_users = cursor.fetchall()
            if not active_users:
                active_users = []
        except mysql.connector.Error as db_err:
            print(f"Database error fetching active users: {str(db_err)}")
            flash('Error fetching user data. Please try again.', 'error')
            active_users = []

        # Fetch or create variables data
        variables_data = []
        try:
            cursor.execute("SELECT * FROM `{variables}` WHERE date = %s".format(variables=variables), (last_day_of_month,))
            variables_data = cursor.fetchall()

            if not variables_data:
                try:
                    cursor.execute("INSERT INTO `{variables}` (date, meal_calculation_date) VALUES (%s)".format(variables=variables), (last_day_of_month, last_day_of_month))
                    conn.commit()
                    cursor.execute("SELECT * FROM `{variables}` WHERE date = %s".format(variables=variables), (last_day_of_month,))
                    variables_data = cursor.fetchall()
                except mysql.connector.Error as insert_err:
                    print(f"Error inserting variables: {str(insert_err)}")
                    conn.rollback()
        except mysql.connector.Error as db_err:
            print(f"Database error fetching variables: {str(db_err)}")
            variables_data = []

        if not variables_data or len(variables_data) == 0:
            flash('Error loading configuration data. Please try again.', 'error')
            return redirect('/')

        # Extract variables safely
        try:
            masi_M_on_off = variables_data[0].get('masi_M_on_off', 'per_head')
            masi_charge = int(variables_data[0].get('masi_charge') or 0)
            veg_guest_money = int(variables_data[0].get('veg_guest_charge') or 0)
            egg_guest_money = int(variables_data[0].get('egg_guest_charge') or 0)
            fish_guest_money = int(variables_data[0].get('fish_guest_charge') or 0)
            chicken_guest_money = int(variables_data[0].get('chicken_guest_charge') or 0)
            beef_guest_money = int(variables_data[0].get('beef_guest_charge') or 0)
            other_guest_money = int(variables_data[0].get('other_guest_charge') or 0)
            common_meal = int(variables_data[0].get('common_meal') or 0)
            guest_meal_range = int(variables_data[0].get('guest_meal_range') or 0)
            one_time_meal_charge_update = variables_data[0].get('one_time_meal_charge_update', 0)
            calculation_date = variables_data[0].get('meal_calculation_date', last_day_of_month)
        except (KeyError, ValueError, TypeError) as var_err:
            print(f"Error extracting variables: {str(var_err)}")
            flash('Error loading configuration. Please contact administrator.', 'error')
            masi_M_on_off = 'per_head'
            masi_charge = 0
            veg_guest_money = 0
            egg_guest_money = 0
            fish_guest_money = 0
            chicken_guest_money = 0
            beef_guest_money = 0
            other_guest_money = 0
            common_meal = 0
            guest_meal_range = 0
            one_time_meal_charge_update = 0
            calculation_date = last_day_of_month

        if not calculation_date:
            calculation_date = last_day_of_month  # Default to last day of month if not set or invalid

        # Process meal adjustments
        if (today == calculation_date and one_time_meal_charge_update == 0) or (today == calculation_date and unknow == 1):
            try:
                for user in active_users:
                    if not user or 'id' not in user:
                        continue
                    
                    for_user_id = user['id']
                    
                    try:
                        cursor.execute("""
                            SELECT SUM(morning) as total_morning, SUM(night) as total_night 
                            FROM `{meals}` WHERE id = %s AND date BETWEEN %s AND %s
                        """.format(meals=meals), (for_user_id, month_start, calculation_date))
                        meals_user_aggregate = cursor.fetchall()
                        
                        if not meals_user_aggregate or not meals_user_aggregate[0]:
                            continue
                        
                        total_user_morning = int(meals_user_aggregate[0].get('total_morning') or 0)
                        total_user_night = int(meals_user_aggregate[0].get('total_night') or 0)
                        total_user_meals = total_user_morning + total_user_night
                    except mysql.connector.Error as db_err:
                        print(f"Error fetching meals for user {for_user_id}: {str(db_err)}")
                        continue

                    # Common meal adjustment
                    if common_meal > 0:
                        if guest_meal_range <= total_user_meals < common_meal:
                            new_user_meals = common_meal - total_user_meals
                            if new_user_meals > 0:
                                for new_user_meal in range(new_user_meals):
                                    current_day = month_start
                                    while current_day <= calculation_date:
                                        try:
                                            cursor.execute("""
                                                SELECT morning, night FROM `{meals}` 
                                                WHERE id = %s AND date = %s
                                            """.format(meals=meals), (for_user_id, current_day))
                                            meal_entry = cursor.fetchone()
                                            
                                            if meal_entry:
                                                if meal_entry.get('morning') == 0:
                                                    cursor.execute("""
                                                        UPDATE `{meals}` SET morning = 1 
                                                        WHERE id = %s AND date = %s
                                                    """.format(meals=meals), (for_user_id, current_day))
                                                    conn.commit()
                                                    break
                                                elif meal_entry.get('night') == 0:
                                                    cursor.execute("""
                                                        UPDATE `{meals}` SET night = 1 
                                                        WHERE id = %s AND date = %s
                                                    """.format(meals=meals), (for_user_id, current_day))
                                                    conn.commit()
                                                    break
                                        except mysql.connector.Error as db_err:
                                            print(f"Error updating meal for user {for_user_id}: {str(db_err)}")
                                            conn.rollback()
                                            break
                                        
                                        current_day += timedelta(days=1)

                    # Guest meal range adjustment
                    if guest_meal_range > 0:
                        if 0 < total_user_meals < guest_meal_range:
                            current_day = month_start
                            while current_day <= calculation_date:
                                try:
                                    cursor.execute("""
                                        SELECT morning, night FROM `{meals}` 
                                        WHERE id = %s AND date = %s
                                    """.format(meals=meals), (for_user_id, current_day))
                                    meal_entry = cursor.fetchone()
                                    
                                    if meal_entry:
                                        # Handle morning meal
                                        if meal_entry.get('morning') == 1:
                                            try:
                                                cursor.execute("""
                                                    SELECT guest_morning FROM `{meals}` 
                                                    WHERE id = %s AND date = %s
                                                """.format(meals=meals), (for_user_id, current_day))
                                                result = cursor.fetchone()

                                                guest = 1
                                                if result:
                                                    if isinstance(result, dict):
                                                        value = result.get('guest_morning', 0)
                                                    else:
                                                        value = result[0]
                                                    
                                                    try:
                                                        if value:
                                                            guest = int(str(value)[0] if len(str(value)) > 0 else 0) + 1
                                                    except (ValueError, TypeError, IndexError):
                                                        guest = 1

                                                cursor.execute("""
                                                    UPDATE `{meals}` SET morning = 0, guest_morning = %s 
                                                    WHERE id = %s AND date = %s
                                                """.format(meals=meals), (guest, for_user_id, current_day))
                                                conn.commit()
                                            except mysql.connector.Error as db_err:
                                                print(f"Error updating guest morning: {str(db_err)}")
                                                conn.rollback()

                                        # Handle night meal
                                        if meal_entry.get('night') == 1:
                                            try:
                                                cursor.execute("""
                                                    SELECT guest_night FROM `{meals}` 
                                                    WHERE id = %s AND date = %s
                                                """.format(meals=meals), (for_user_id, current_day))
                                                result = cursor.fetchone()

                                                guest = 1
                                                if result:
                                                    if isinstance(result, dict):
                                                        value = result.get('guest_night', 0)
                                                    else:
                                                        value = result[0]
                                                    
                                                    try:
                                                        if value:
                                                            guest = int(str(value)[0] if len(str(value)) > 0 else 0) + 1
                                                    except (ValueError, TypeError, IndexError):
                                                        guest = 1

                                                cursor.execute("""
                                                    UPDATE `{meals}` SET night = 0, guest_night = %s 
                                                    WHERE id = %s AND date = %s
                                                """.format(meals=meals), (guest, for_user_id, current_day))
                                                conn.commit()
                                            except mysql.connector.Error as db_err:
                                                print(f"Error updating guest night: {str(db_err)}")
                                                conn.rollback()
                                except mysql.connector.Error as db_err:
                                    print(f"Error processing guest meals: {str(db_err)}")
                                    break
                                
                                current_day += timedelta(days=1)
            except Exception as e:
                print(f"Error in meal adjustment logic: {str(e)}")
                conn.rollback()

        # Define helper function for guest meal categorization
        def find_veg_nonveg(guest_meals):
            total_veg_guest = 0
            total_egg_guest = 0
            total_fish_guest = 0
            total_chicken_guest = 0
            total_beef_guest = 0
            total_other_guest = 0
            another_guest = 0
            
            if not guest_meals:
                return (total_veg_guest, total_egg_guest, total_fish_guest, 
                       total_chicken_guest, total_beef_guest, total_other_guest)
            
            for guest_meal in guest_meals:
                if not guest_meal:
                    continue
                
                guest_morning = guest_meal.get('guest_morning')
                guest_night = guest_meal.get('guest_night')
                
                # Process morning guest
                if guest_morning:
                    try:
                        guest_morning_str = str(guest_morning)
                        if guest_morning_str and len(guest_morning_str) >= 2:
                            meal_type = guest_morning_str[2] if len(guest_morning_str) > 2 else ''
                            
                            try:
                                guest_count = int(guest_morning_str.split()[0])
                            except (ValueError, IndexError):
                                guest_count = 0
                            
                            if meal_type == 'v':
                                total_veg_guest += guest_count
                            elif meal_type == 'c':
                                total_chicken_guest += guest_count
                            elif meal_type == 'e':
                                total_egg_guest += guest_count
                            elif meal_type == 'f':
                                total_fish_guest += guest_count
                            elif meal_type == 'b':
                                total_beef_guest += guest_count
                            elif meal_type == 'o':
                                total_other_guest += guest_count
                        else:
                            try:
                                guest = int(guest_morning_str)
                                another_guest += guest
                            except ValueError:
                                pass
                    except Exception as e:
                        print(f"Error processing guest_morning: {str(e)}")
                        continue

                # Process night guest
                if guest_night:
                    try:
                        guest_night_str = str(guest_night)
                        if guest_night_str and len(guest_night_str) >= 2:
                            meal_type = guest_night_str[2] if len(guest_night_str) > 2 else ''
                            
                            try:
                                guest_count = int(guest_night_str.split()[0])
                            except (ValueError, IndexError):
                                guest_count = 0
                            
                            if meal_type == 'v':
                                total_veg_guest += guest_count
                            elif meal_type == 'c':
                                total_chicken_guest += guest_count
                            elif meal_type == 'e':
                                total_egg_guest += guest_count
                            elif meal_type == 'f':
                                total_fish_guest += guest_count
                            elif meal_type == 'b':
                                total_beef_guest += guest_count
                            elif meal_type == 'o':
                                total_other_guest += guest_count
                        else:
                            try:
                                guest = int(guest_night_str)
                                another_guest += guest
                            except ValueError:
                                pass
                    except Exception as e:
                        print(f"Error processing guest_night: {str(e)}")
                        continue
            
            return (total_veg_guest, total_egg_guest, total_fish_guest, 
                   total_chicken_guest, total_beef_guest, total_other_guest)

        # Calculate total guest meals
        total_guest_meals = []
        try:
            cursor.execute("""
                SELECT guest_morning, guest_night FROM `{meals}` 
                WHERE date BETWEEN %s AND %s
            """.format(meals=meals), (month_start, today))
            total_guest_meals = cursor.fetchall()
            if not total_guest_meals:
                total_guest_meals = []
        except mysql.connector.Error as db_err:
            print(f"Database error fetching guest meals: {str(db_err)}")
            total_guest_meals = []

        total_veg_guest, total_egg_guest, total_fish_guest, total_chicken_guest, total_beef_guest, total_other_guest = find_veg_nonveg(total_guest_meals)

        # Calculate total meals
        total_morning = 0
        total_night = 0
        total_meals = 0
        try:
            cursor.execute("""
                SELECT SUM(morning) as total_morning, SUM(night) as total_night 
                FROM `{meals}` WHERE date BETWEEN %s AND %s
            """.format(meals=meals), (month_start, today))
            meals_aggregate = cursor.fetchall()
            
            if meals_aggregate and meals_aggregate[0]:
                total_morning = int(meals_aggregate[0].get('total_morning') or 0)
                total_night = int(meals_aggregate[0].get('total_night') or 0)
                total_meals = total_morning + total_night
        except mysql.connector.Error as db_err:
            print(f"Database error fetching meal aggregates: {str(db_err)}")
            total_morning = 0
            total_night = 0
            total_meals = 0

        # Calculate guest amounts
        total_guests = total_veg_guest + total_egg_guest + total_fish_guest + total_chicken_guest + total_beef_guest + total_other_guest
        guest_veg_amount = total_veg_guest * veg_guest_money
        guest_egg_amount = total_egg_guest * egg_guest_money
        guest_fish_amount = total_fish_guest * fish_guest_money
        guest_chicken_amount = total_chicken_guest * chicken_guest_money
        guest_beef_amount = total_beef_guest * beef_guest_money
        guest_other_amount = total_other_guest * other_guest_money
        guest_amount = guest_veg_amount + guest_egg_amount + guest_fish_amount + guest_chicken_amount + guest_beef_amount + guest_other_amount

        # Calculate marketing totals
        total_shop = 0
        total_veg = 0
        total_nonveg = 0
        total_other = 0
        total_common = 0
        total_marketing = 0
        try:
            cursor.execute("""
                SELECT SUM(shop_money), SUM(veg_money), SUM(non_veg_money), 
                       SUM(other_money), SUM(common_money) 
                FROM `{marketing}` WHERE date BETWEEN %s AND %s
            """.format(marketing=marketing), (month_start, today))
            marketing_data = cursor.fetchall()
            
            if marketing_data and marketing_data[0]:
                total_shop = int(marketing_data[0].get('SUM(shop_money)') or 0)
                total_veg = int(marketing_data[0].get('SUM(veg_money)') or 0)
                total_nonveg = int(marketing_data[0].get('SUM(non_veg_money)') or 0)
                total_other = int(marketing_data[0].get('SUM(other_money)') or 0)
                total_common = int(marketing_data[0].get('SUM(common_money)') or 0)
                total_marketing = total_shop + total_veg + total_other
        except mysql.connector.Error as db_err:
            print(f"Database error fetching marketing data: {str(db_err)}")

        # Calculate deposit totals
        total_deposit = 0
        try:
            cursor.execute("""
                SELECT SUM(money) FROM `{deposit}` 
                WHERE date BETWEEN %s AND %s
            """.format(deposit=deposit), (month_start, today))
            deposit_data = cursor.fetchall()
            
            if deposit_data and deposit_data[0]:
                total_deposit = int(deposit_data[0].get('SUM(money)') or 0)
        except mysql.connector.Error as db_err:
            print(f"Database error fetching deposit data: {str(db_err)}")

        amount_alive = total_deposit - total_marketing

        # Calculate meal charge
        mealcharge = 0
        try:
            if total_meals > 0:
                mealcharge = (((total_marketing - guest_amount) - total_deposit) / total_meals)
            else:
                mealcharge = 0
        except ZeroDivisionError:
            mealcharge = 0
        except Exception as e:
            print(f"Error calculating meal charge: {str(e)}")
            mealcharge = 0

        # Define function to find meal charge for a user
        def find_meal_charge(user_id, total_common):
            T_common = total_common
            
            # Fetch user guest meals
            user_guest_meals = []
            try:
                cursor.execute("""
                    SELECT guest_morning, guest_night FROM `{meals}` 
                    WHERE id = %s AND date BETWEEN %s AND %s
                """.format(meals=meals), (user_id, month_start, today))
                user_guest_meals = cursor.fetchall()
                if not user_guest_meals:
                    user_guest_meals = []
            except mysql.connector.Error as db_err:
                print(f"Error fetching user guest meals: {str(db_err)}")
                user_guest_meals = []

            total_user_veg_guest, total_user_egg_guest, total_user_fish_guest, total_user_chicken_guest, total_user_beef_guest, total_user_other_guest = find_veg_nonveg(user_guest_meals)

            # Calculate user meal totals
            total_user_morning = 0
            total_user_night = 0
            total_user_meals = 0
            try:
                cursor.execute("""
                    SELECT SUM(morning) as total_morning, SUM(night) as total_night 
                    FROM `{meals}` WHERE id = %s AND date BETWEEN %s AND %s
                """.format(meals=meals), (user_id, month_start, today))
                meals_user_aggregate = cursor.fetchall()
                
                if meals_user_aggregate and meals_user_aggregate[0]:
                    total_user_morning = int(meals_user_aggregate[0].get('total_morning') or 0)
                    total_user_night = int(meals_user_aggregate[0].get('total_night') or 0)
                    total_user_meals = total_user_morning + total_user_night
            except mysql.connector.Error as db_err:
                print(f"Error fetching user meals: {str(db_err)}")

            total_user_guests = total_user_veg_guest + total_user_egg_guest + total_user_fish_guest + total_user_chicken_guest + total_user_beef_guest + total_user_other_guest
            user_guest_amount = (total_user_veg_guest * veg_guest_money) + (total_user_egg_guest * egg_guest_money) + (total_user_fish_guest * fish_guest_money) + (total_user_chicken_guest * chicken_guest_money) + (total_user_beef_guest * beef_guest_money) + (total_user_other_guest * other_guest_money)

            # Calculate user deposit
            total_user_deposit = 0
            try:
                cursor.execute("""
                    SELECT SUM(money) FROM `{deposit}` 
                    WHERE id = %s AND date BETWEEN %s AND %s
                """.format(deposit=deposit), (user_id, month_start, today))
                user_deposit_data = cursor.fetchall()
                
                if user_deposit_data and user_deposit_data[0]:
                    total_user_deposit = int(user_deposit_data[0].get('SUM(money)') or 0)
            except mysql.connector.Error as db_err:
                print(f"Error fetching user deposit: {str(db_err)}")

            # Calculate amount
            amount = 0
            if total_user_meals > 0:
                amount = (((total_user_meals * mealcharge) + user_guest_amount + T_common) - total_user_deposit)
            elif total_user_meals == 0 and user_guest_amount > 0:
                amount = user_guest_amount - total_user_deposit
                T_common = 0
            elif total_user_guests == 0 and total_user_meals == 0:
                amount = 0
                T_common = 0
            
            return (total_user_meals, total_user_veg_guest, total_user_egg_guest, total_user_fish_guest, 
                   total_user_chicken_guest, total_user_beef_guest, total_user_other_guest, 
                   total_user_guests, user_guest_amount, total_user_deposit, T_common, amount)

        # Get current user's meal charge
        total_user_meals, total_user_veg_guest, total_user_egg_guest, total_user_fish_guest, total_user_chicken_guest, total_user_beef_guest, total_user_other_guest, total_user_guests, user_guest_amount, total_user_deposit, total_common, amount = find_meal_charge(user_id, total_common)

        # Update meal charge data
        if (today == calculation_date and datetime.strptime('00:00', '%H:%M').time() < now <= datetime.strptime('23:59', '%H:%M').time() and one_time_meal_charge_update == 0 and know != 1) or (today == calculation_date and datetime.strptime('00:00', '%H:%M').time() < now <= datetime.strptime('23:59', '%H:%M').time() and unknow == 1):
            try:
                # Fetch active users
                active_users_update = []
                try:
                    cursor.execute("SELECT id, name FROM `{users}` WHERE blocked = 0".format(users=users))
                    active_users_update = cursor.fetchall()
                    if not active_users_update:
                        active_users_update = []
                except mysql.connector.Error as db_err:
                    print(f"Error fetching active users for update: {str(db_err)}")
                    active_users_update = []

                total_members = len(active_users_update)
                
                # Count members with meals
                count_meal_member = 0
                for user in active_users_update:
                    if not user or 'id' not in user:
                        continue
                    
                    only_user_id = user['id']
                    try:
                        cursor.execute("""
                            SELECT SUM(morning) as total_morning, SUM(night) as total_night 
                            FROM `{meals}` WHERE id = %s AND date BETWEEN %s AND %s
                        """.format(meals=meals), (only_user_id, month_start, calculation_date))
                        meals_user_aggregate = cursor.fetchall()
                        
                        if meals_user_aggregate and meals_user_aggregate[0]:
                            total_user_morning = int(meals_user_aggregate[0].get('total_morning') or 0)
                            total_user_night = int(meals_user_aggregate[0].get('total_night') or 0)
                            total_user_meals = total_user_morning + total_user_night
                            if total_user_meals > 0:
                                count_meal_member += 1
                    except mysql.connector.Error as db_err:
                        print(f"Error counting meal members: {str(db_err)}")
                        continue

                # Adjust masi charge
                if count_meal_member > 0:
                    if masi_M_on_off == 'per_month':
                        masi_charge = int((masi_charge / count_meal_member) + 1)
                    if total_common > 0:
                        total_common = ((total_common / count_meal_member) + masi_charge)

                # Find manager
                manager_name = None
                for user in active_users_update:
                    if not user or 'id' not in user:
                        continue
                    
                    just_user_id = user['id']
                    try:
                        cursor.execute("""
                            SELECT name, role FROM `{users}` WHERE id = %s
                        """.format(users=users), (just_user_id,))
                        user_data = cursor.fetchone()
                        
                        if user_data:
                            role = user_data.get('role')
                            if role == 'manager':
                                manager_name = user_data.get('name')
                                break
                    except mysql.connector.Error as db_err:
                        print(f"Error fetching user role: {str(db_err)}")
                        continue

                # Update variables table
                try:
                    cursor.execute("""
                        UPDATE `{variables}` SET meal_charge = %s, common_charge = %s, no_of_members = %s, 
                        manager_name = %s, total_morning_meal = %s, total_night_meal = %s, total_meal = %s, 
                        total_guest_veg_meal = %s, total_guest_egg_meal = %s, total_guest_fish_meal = %s, 
                        total_guest_chicken_meal = %s, total_guest_beef_meal = %s, total_guest_other_meal = %s,
                        total_guest_meal = %s, Market_shop_money = %s, Market_veg_money = %s, 
                        Market_non_veg_money = %s, Market_other_money = %s, total_marketing_money = %s, 
                        total_deposit_amount = %s WHERE date = %s
                    """.format(variables=variables), (mealcharge, total_common, total_members, manager_name, 
                    total_morning, total_night, total_meals, total_veg_guest, total_egg_guest, 
                    total_fish_guest, total_chicken_guest, total_beef_guest, total_other_guest, 
                    total_guests, total_shop, total_veg, total_nonveg, total_other, 
                    total_marketing, total_deposit, last_day_of_month))
                    conn.commit()
                except mysql.connector.Error as db_err:
                    print(f"Database error updating variables: {str(db_err)}")
                    conn.rollback()

                # Insert meal charge for all active users
                for user in active_users_update:
                    if not user or 'id' not in user or 'name' not in user:
                        continue
                    
                    try:
                        user_meal_data = find_meal_charge(user['id'], total_common)
                        total_user_meals, total_user_veg_guest, total_user_egg_guest, total_user_fish_guest, total_user_chicken_guest, total_user_beef_guest, total_user_other_guest, total_user_guests, user_guest_amount, total_user_deposit, T_common, amount = user_meal_data
                        
                        cursor.execute("""
                            INSERT INTO `{meal_charge}` (id, date, name, total_meal, meal_charge, 
                            T_veg_guest_meal, T_egg_guest_meal, T_fish_guest_meal, T_chicken_guest_meal, 
                            T_beef_guest_meal, T_other_guest_meal, T_guest_amount, common_charge, deposit, amount) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE total_meal = VALUES(total_meal), 
                            meal_charge = VALUES(meal_charge), T_veg_guest_meal = VALUES(T_veg_guest_meal), 
                            T_egg_guest_meal = VALUES(T_egg_guest_meal), T_fish_guest_meal = VALUES(T_fish_guest_meal), 
                            T_chicken_guest_meal = VALUES(T_chicken_guest_meal), T_beef_guest_meal = VALUES(T_beef_guest_meal), 
                            T_other_guest_meal = VALUES(T_other_guest_meal), T_guest_amount = VALUES(T_guest_amount),
                            common_charge = VALUES(common_charge), deposit = VALUES(deposit), amount = VALUES(amount)
                        """.format(meal_charge=meal_charge), (user['id'], calculation_date, user['name'], 
                        total_user_meals, mealcharge, total_user_veg_guest, total_user_egg_guest, 
                        total_user_fish_guest, total_user_chicken_guest, total_user_beef_guest, 
                        total_user_other_guest, user_guest_amount, T_common, total_user_deposit, amount))
                        conn.commit()
                    except mysql.connector.Error as db_err:
                        print(f"Database error inserting meal charge for user {user.get('id')}: {str(db_err)}")
                        conn.rollback()
                        continue
                    except Exception as e:
                        print(f"Error processing meal charge for user {user.get('id')}: {str(e)}")
                        continue
            except mysql.connector.IntegrityError as integrity_err:
                print(f"Integrity error in meal charge update: {str(integrity_err)}")
                pass
            except Exception as e:
                print(f"Error in meal charge update section: {str(e)}")
                conn.rollback()

        # Get previous month data
        previous_calculation_date, latest_calculation_date, previous_variable_date = get_previous_month_date(cursor, variables, today, previous_month_last_day, last_day_of_month)

        # Fetch previous meal charge data
        previous_meal_charge_data = []
        try:
            cursor.execute("""
                SELECT * FROM `{meal_charge}` WHERE id = %s AND date = %s
            """.format(meal_charge=meal_charge), (user_id, previous_calculation_date))
            previous_meal_charge_data = cursor.fetchall()
            if not previous_meal_charge_data:
                previous_meal_charge_data = []
        except mysql.connector.Error as db_err:
            print(f"Database error fetching previous meal charge: {str(db_err)}")
            previous_meal_charge_data = []

        # Fetch previous variable data
        previous_variable_data = []
        try:
            cursor.execute("""
                SELECT * FROM `{variables}` WHERE date = %s
            """.format(variables=variables), (previous_variable_date,))
            previous_variable_data = cursor.fetchall()
            if not previous_variable_data:
                previous_variable_data = []
        except mysql.connector.Error as db_err:
            print(f"Database error fetching previous variables: {str(db_err)}")
            previous_variable_data = []

        # Prepare money data dictionary
        moneydata = {
            "total_meals": total_meals,
            "total_marketing": total_marketing,
            "total_deposit": total_deposit,
            "amount_alive": amount_alive,
            "total_guests": total_guests,
            "mealcharge": mealcharge,
            "guest_amount": guest_amount,
            "total_user_meals": total_user_meals,
            "total_user_deposit": total_user_deposit,
            "total_user_veg_guest": total_user_veg_guest,
            "total_user_egg_guest": total_user_egg_guest,
            "total_user_fish_guest": total_user_fish_guest,
            "total_user_chicken_guest": total_user_chicken_guest,
            "total_user_beef_guest": total_user_beef_guest,
            "total_user_other_guest": total_user_other_guest,
            "total_user_guests": total_user_guests,
            "user_guest_amount": user_guest_amount,
            "amount": amount,
            "masi_M_on_off": masi_M_on_off,
            "masi_charge": masi_charge,
            "veg_guest_money": veg_guest_money,
            "egg_guest_money": egg_guest_money,
            "fish_guest_money": fish_guest_money,
            "chicken_guest_money": chicken_guest_money,
            "beef_guest_money": beef_guest_money,
            "other_guest_money": other_guest_money,
            "total_shop": total_shop,
            "total_veg": total_veg,
            "total_nonveg": total_nonveg,
            "total_common": total_common
        }

        # Handle different return scenarios
        if know == 1:
            return (moneydata, session.pop('message', None), previous_variable_data)
        
        if unknow == 1:
            previous_meal_charge_datas = []
            try:
                cursor.execute("""
                    SELECT * FROM `{meal_charge}` WHERE date = %s
                """.format(meal_charge=meal_charge), (previous_calculation_date,))
                previous_meal_charge_datas = cursor.fetchall()
                if not previous_meal_charge_datas:
                    previous_meal_charge_datas = []
                print("previous_meal_charge_data:", previous_meal_charge_datas)
            except mysql.connector.Error as db_err:
                print(f"Database error fetching all meal charges: {str(db_err)}")
                previous_meal_charge_datas = []
            
            return (moneydata, session.pop('message', None), previous_meal_charge_datas, previous_variable_data)
        
        if request.method == 'POST' and request.form.get('selected_id'):
            selected_id = request.form.get('selected_id')
            selected_date_str = request.form.get('meal_charge_date')
            if selected_id and selected_date_str:
                try:
                    start_date = selected_date_str + "-01"

                    query = f"""SELECT *FROM `{meal_charge}`WHERE id = %sAND date >= %sAND date < DATE_ADD(%s, INTERVAL 1 MONTH)"""
                    cursor.execute(query, (selected_id, start_date, start_date))
                    search_meal_charge_data = cursor.fetchall()

                    query = f"""SELECT *FROM `{variables}`WHERE date >= %sAND date < DATE_ADD(%s, INTERVAL 1 MONTH)"""
                    cursor.execute(query, (start_date, start_date))
                    search_variable_data = cursor.fetchall()

                    if search_meal_charge_data and search_variable_data:
                        session['search_meal_charge_data'] = search_meal_charge_data
                        session['search_variable_data'] = search_variable_data
                    else:
                        message = "No meal charge data found for the selected user and date."
                        session['message'] = message
                        return redirect(url_for('user_meal_amount'))
                except ValueError:
                    message = "Invalid date format or wrong user selection."
                    session['message'] = message
                    return redirect(url_for('user_meal_amount'))
                except Exception as e:
                    message = f"Unexpected error in date search: {str(e)}"
                    session['message'] = message
                    return redirect(url_for('user_meal_amount'))
            else:
                message = "Please select a user and date."
                session['message'] = message
                return redirect(url_for('user_meal_amount'))
            return redirect(url_for('user_meal_amount'))


        return render_template('user_meal_amount.html', 
                             role=session.get('role'), 
                             active_users = active_users,
                             moneydata=moneydata, 
                             message=session.pop('message', None), 
                             previous_meal_charge_data=previous_meal_charge_data, 
                             previous_variable_data=previous_variable_data,
                             search_variable_data = search_variable_data,
                             search_meal_charge_data = search_meal_charge_data )

    except mysql.connector.Error as db_err:
        if conn:
            conn.rollback()
        print(f"Database error in /meal_amount: {str(db_err)}")
        flash('Database error occurred. Please try again later.', 'error')
        return redirect('/')
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Unexpected error in /meal_amount: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect('/')
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()




@app.route('/manager/meal_amount', methods=['GET', 'POST']) 
def manager_meal_amount():
    # User authentication and authorization checks
    if 'user_id' not in session or (session.get('role') != 'manager' and session.get('role') != 'head_manager') or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')

    # Database connection handling
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True, buffered=True)
    except Exception as e:
        # If DB connection fails, show error
        return render_template('manager_meal_amount.html', moneydata=None, message=f"Database connection failed: {str(e)}", previous_meal_charge_datas=None, previous_variable_data=None)

    mess_code = str(session.get('mess_code'))
    users = str((mess_code) + "_users")
    meals = str((mess_code) + "_meals")
    marketing = str((mess_code) + "_marketing")
    marketing_pending = str((mess_code) + "_marketing_pending")
    deposit = str((mess_code) + "_deposit")
    deposit_pending = str((mess_code) + "_deposit_pending")
    meal_charge = str((mess_code) + "_meal_charge")
    variables = str((mess_code) + "_variables")

    today = datetime.today().date()
    now = datetime.now().time()
    month_start = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day_of_month = next_month - timedelta(days=1)
    previous_month_last_day = month_start - timedelta(days=1)

    # Get session-pushed messages
    message = session.pop('message', None)
    search_meal_charge_data = session.pop('search_meal_charge_data', None)
    search_variable_data = session.pop('search_variable_data', None)
    search_meal_charge_datas = session.pop('search_meal_charge_datas', None)
    search_total_meal_amount = session.pop('search_total_meal_amount', None)

    # Fetch previous meal charge data, robust error handling
    try:
        previous_calculation_date, latest_calculation_date, previous_variable_date = get_previous_month_date(cursor, variables, today, previous_month_last_day, last_day_of_month)
        cursor.execute("SELECT * FROM `{meal_charge}` WHERE date = %s".format(meal_charge=meal_charge), (previous_calculation_date,))
        previous_meal_charge_datas = cursor.fetchall()
        if not previous_meal_charge_datas:
            # Custom handler, handle error/result in user_meal_amount
            moneydata, messages, previous_meal_charge_datas, previous_variable_data = user_meal_amount(unknow=1, know=None)
        else:
            moneydata, messages, previous_variable_data = user_meal_amount(unknow=None, know=1)
    except mysql.connector.Error as e:
        # Future-proof: handles SQL error and prints error details for debugging
        print("MySQL error:", e)
        return render_template('manager_meal_amount.html', moneydata=None, message=f"Error fetching data: {str(e)}", previous_meal_charge_datas=None, previous_variable_data=None)
    except Exception as e:
        # Any unknown error handled clearly
        print("General error:", e)
        return render_template('manager_meal_amount.html', moneydata=None, message=f"Unexpected error occurred: {str(e)}", previous_meal_charge_datas=None, previous_variable_data=None)

    try:
        cursor.execute("SELECT id, name FROM `{users}` WHERE blocked = 0 ".format(users=users))
        active_users = cursor.fetchall()
    except mysql.connector.Error as e:
        return render_template('manager_meal_amount.html', moneydata=None, message=f"Error loading users: {str(e)}", previous_meal_charge_datas=None, previous_variable_data=None)
    except Exception as e:
        return render_template('manager_meal_amount.html', moneydata=None, message=f"Unexpected user error: {str(e)}", previous_meal_charge_datas=None, previous_variable_data=None)
    
    #Find total meal amount 
    try:
        cursor.execute("SELECT SUM(amount) FROM `{meal_charge}` WHERE date = %s".format(meal_charge=meal_charge), (previous_calculation_date,))
        result = cursor.fetchone()
        total_meal_amount = result["SUM(amount)"] if result and result["SUM(amount)"] else 0
    except mysql.connector.Error as e:
        total_meal_amount = 0
    except Exception as e:
        total_meal_amount = 0

    # POST request logic
    if request.method == 'POST': #stop reloading data on submit
        options = request.form.get('update')
        # Option 1: meal_data_update
        if options == 'meal_data_update' and (latest_calculation_date < today <= last_day_of_month or (month_start <= today <= (month_start + timedelta(days=7)))):
            if latest_calculation_date < today <= last_day_of_month:
                perfect_date = latest_calculation_date
            elif month_start <= today <= (month_start + timedelta(days=7)):
                perfect_date = previous_calculation_date

            selected_id = request.form.get('selected_id')
            if selected_id:
                number_of_meals = request.form.get('number_of_meals')
                guest_amount = request.form.get('guest_amount')
                common_charge = request.form.get('user_common_charge')
                deposit_amount = request.form.get('deposit_amount')
                calculated_amount = request.form.get('calculated_amount')

                def to_float(value, name):
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        try:
                            cursor.execute("SELECT {name} FROM `{meal_charge}` WHERE id = %s AND date = %s".format(meal_charge=meal_charge, name=name), (selected_id, perfect_date))
                            user_meal_charge = cursor.fetchone()
                            return float(user_meal_charge[name]) if user_meal_charge else 0.0
                        except Exception as e:
                            print("Error converting to float:", e)
                            return 0.0

                number_of_meals = number_of_meals if number_of_meals else to_float(None, 'total_meal')
                guest_amount = to_float(guest_amount, 'T_guest_amount')
                common_charge = to_float(common_charge, 'common_charge')
                deposit_amount = to_float(deposit_amount, 'deposit')
                calculated_amount = to_float(calculated_amount, 'amount')

                try:
                    cursor.execute(f"""
                        INSERT INTO `{meal_charge}` (id, date, total_meal, T_guest_amount, common_charge, deposit, amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_meal = VALUES(total_meal),
                        T_guest_amount = VALUES(T_guest_amount),
                        common_charge = VALUES(common_charge),
                        deposit = VALUES(deposit),
                        amount = VALUES(amount)
                    """, (selected_id, perfect_date, number_of_meals, guest_amount, common_charge, deposit_amount, calculated_amount))
                    conn.commit()
                except mysql.connector.Error as e:
                    print("MySQL error:", e)
                    message = f"Database error while updating meal charge: {str(e)}"
                    return render_template('manager_meal_amount.html', role=session['role'], moneydata=moneydata, message=message, previous_meal_charge_datas=previous_meal_charge_datas, previous_variable_data=previous_variable_data, active_users=active_users)
                except Exception as e:
                    print("General error:", e)
                    message = f"Unexpected error while updating meal charge: {str(e)}"
                    return render_template('manager_meal_amount.html', role=session['role'], moneydata=moneydata, message=message, previous_meal_charge_datas=previous_meal_charge_datas, previous_variable_data=previous_variable_data, active_users=active_users)
                finally:
                    try:
                        cursor.execute(f"""
                            UPDATE `{variables}` SET one_time_meal_charge_update = 1
                            WHERE date = %s
                        """, (perfect_date,))
                        conn.commit()
                        message = "successfully Update !"
                        session['message'] = message
                    except Exception as e:
                        print("Error updating variables:", e)
                    cursor.close()
                    conn.close()
                return redirect(url_for('manager_meal_amount'))
            else:
                message = "Please select a user."
                return render_template('manager_meal_amount.html', role=session['role'], moneydata=moneydata, message=message, previous_meal_charge_datas=previous_meal_charge_datas, previous_variable_data=previous_variable_data, active_users=active_users)

        # Option 2: meal_charge_update
        elif options == 'meal_charge_update' and (latest_calculation_date < today <= last_day_of_month or (month_start <= today <= (month_start + timedelta(days=7)))):
            if latest_calculation_date < today <= last_day_of_month:
                perfect_date = latest_calculation_date
            elif month_start <= today <= (month_start + timedelta(days=7)):
                perfect_date = previous_calculation_date
            meal_charge_amount = request.form.get('meal_charge_amount')
            common_charge = request.form.get('common_charge')
            def to_float(value, name):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    try:
                        cursor.execute("SELECT {name} FROM `{variables}` WHERE date = %s".format(variables=variables, name=name), (perfect_date,))
                        user_meal_charge = cursor.fetchone()
                        return float(user_meal_charge[name]) if user_meal_charge else 0.0
                    except Exception as e:
                        print("Error converting to float:", e)
                        return 0.0

            meal_charge_amount = to_float(meal_charge_amount, 'meal_charge')
            common_charge = to_float(common_charge, 'common_charge')

            try:
                cursor.execute(f"""
                        UPDATE `{variables}` SET meal_charge = %s, common_charge = %s
                        WHERE date = %s
                    """, (meal_charge_amount, common_charge, perfect_date))
                conn.commit()
                for active_user in active_users:
                    user_id = active_user['id']
                    cursor.execute("SELECT total_meal FROM `{meal_charge}` WHERE id = %s AND date = %s".format(meal_charge=meal_charge), (user_id, perfect_date))
                    meals_user_aggregate = cursor.fetchone()
                    if meals_user_aggregate:
                        total_user_meals = int(meals_user_aggregate['total_meal'] or 0)
                        if total_user_meals > 0:
                            cursor.execute(f"""
                                UPDATE `{meal_charge}` SET meal_charge = %s, common_charge = %s
                                WHERE id = %s AND date = %s
                            """, (meal_charge_amount, common_charge, user_id, perfect_date))
                            conn.commit()
                        else:
                            cursor.execute(f"""
                                UPDATE `{meal_charge}` SET meal_charge = %s, common_charge = %s
                                WHERE id = %s AND date = %s
                            """, (0.00, 0.00, user_id, perfect_date))
                            conn.commit()

                    cursor.execute("SELECT total_meal, meal_charge, T_guest_amount, deposit, common_charge FROM `{meal_charge}` WHERE id = %s AND date = %s".format(meal_charge=meal_charge), (user_id, perfect_date))
                    user_meal_charge = cursor.fetchone()
                    if user_meal_charge:
                        try:
                            total_meal = int(user_meal_charge['total_meal'])
                            meal_charge_update = float(user_meal_charge['meal_charge'])
                            T_guest_amount = float(user_meal_charge['T_guest_amount'])
                            deposit = float(user_meal_charge['deposit'])
                            common_charge_update = float(user_meal_charge['common_charge'])
                            if total_meal != 0 :
                                amount = ((total_meal * meal_charge_update) + T_guest_amount + common_charge_update) - deposit
                            else:
                                amount = 0 - deposit
                        except Exception as e:
                            print("Amount calculation failed:", e)
                            amount = 0.0 - float(user_meal_charge.get('deposit', 0))

                        cursor.execute(f"""
                            UPDATE `{meal_charge}` SET amount = %s
                            WHERE id = %s AND date = %s
                        """, (float(amount), user_id, perfect_date))
                        conn.commit()
            except mysql.connector.Error as e:
                print("MySQL error:", e)
                message = f"Database error during charge update: {str(e)}"
                return render_template('manager_meal_amount.html', role=session['role'], moneydata=moneydata, message=message, previous_meal_charge_datas=previous_meal_charge_datas, previous_variable_data=previous_variable_data, active_users=active_users)
            except Exception as e:
                print("Charge update general error:", e)
                message = f"Unexpected error during charge update: {str(e)}"
                return render_template('manager_meal_amount.html', role=session['role'], moneydata=moneydata, message=message, previous_meal_charge_datas=previous_meal_charge_datas, previous_variable_data=previous_variable_data, active_users=active_users)
            finally:
                try:
                    cursor.execute(f"""
                        UPDATE `{variables}` SET one_time_meal_charge_update = 1
                        WHERE date = %s
                    """, (perfect_date,))
                    conn.commit()
                    message = "successfully Update !"
                    session['message'] = message
                except Exception as e:
                    print("Error updating meal charge variable flag:", e)
                cursor.close()
                conn.close()
            return redirect(url_for('manager_meal_amount'))

        # Option 3: search_by_date
        elif options == 'search_by_date':
            selected_id = request.form.get('selected_id')
            selected_date_str = request.form.get('meal_charge_date')
            if selected_id and selected_date_str:
                try:
                    start_date = selected_date_str + "-01"

                    query = f"""SELECT *FROM `{meal_charge}`WHERE id = %sAND date >= %sAND date < DATE_ADD(%s, INTERVAL 1 MONTH)"""
                    cursor.execute(query, (selected_id, start_date, start_date))
                    search_meal_charge_data = cursor.fetchall()

                    query = f"""SELECT *FROM `{variables}`WHERE date >= %sAND date < DATE_ADD(%s, INTERVAL 1 MONTH)"""
                    cursor.execute(query, (start_date, start_date))
                    search_variable_data = cursor.fetchall()
                    
                    if search_meal_charge_data and search_variable_data:
                        session['search_meal_charge_data'] = search_meal_charge_data
                        session['search_variable_data'] = search_variable_data
                    else:
                        message = "No meal charge data found for the selected user and date."
                        session['message'] = message
                        return redirect(url_for('manager_meal_amount'))
                except ValueError:
                    message = "Invalid date format or wrong user selection."
                    session['message'] = message
                    return redirect(url_for('manager_meal_amount'))
                except Exception as e:
                    message = f"Unexpected error in date search: {str(e)}"
                    session['message'] = message
                    return redirect(url_for('manager_meal_amount'))
            else:
                message = "Please select a user and date."
                session['message'] = message
                return redirect(url_for('manager_meal_amount'))
            return redirect(url_for('manager_meal_amount'))

        # Option 4: search_by_date_for_meal
        elif options == 'search_by_date_for_meal':
            selected_date_str = request.form.get('meal_charge_by_date')
            if selected_date_str:
                try:
                    start_date = selected_date_str + "-01"

                    query = f"""SELECT *FROM `{meal_charge}`WHERE date >= %sAND date < DATE_ADD(%s, INTERVAL 1 MONTH)"""
                    cursor.execute(query, (start_date, start_date))
                    search_meal_charge_datas = cursor.fetchall()

                    query = f"""SELECT *FROM `{variables}`WHERE date >= %sAND date < DATE_ADD(%s, INTERVAL 1 MONTH)"""
                    cursor.execute(query, (start_date, start_date))
                    search_variable_data = cursor.fetchall()

                    if search_meal_charge_datas and search_variable_data:
                        search_total_meal_amount = sum(row['amount'] for row in search_meal_charge_datas) if search_meal_charge_datas else 0
                        session['search_meal_charge_datas'] = search_meal_charge_datas
                        session['search_variable_data'] = search_variable_data
                        session['search_total_meal_amount'] = search_total_meal_amount
                    else:
                        message = "No meal charge data found for the selected date."
                        session['message'] = message
                        return redirect(url_for('manager_meal_amount'))
                except ValueError:
                    message = "Invalid date selection."
                    session['message'] = message
                    return redirect(url_for('manager_meal_amount'))
                except Exception as e:
                    message = f"Error during date search: {str(e)}"
                    session['message'] = message
                    return redirect(url_for('manager_meal_amount'))
            else:
                message = "Please select a date."
                session['message'] = message
                return redirect(url_for('manager_meal_amount'))
            return redirect(url_for('manager_meal_amount'))

    # Final data rendering
    return render_template('manager_meal_amount.html',
        role=session['role'],
        moneydata=moneydata,
        message=messages if messages else message,
        previous_meal_charge_datas=search_meal_charge_datas if search_meal_charge_datas else previous_meal_charge_datas,
        previous_variable_data=search_variable_data if search_variable_data else previous_variable_data,
        active_users=active_users,
        search_meal_charge_data=search_meal_charge_data,
        total_meal_amount=search_total_meal_amount if search_total_meal_amount is not None else total_meal_amount
    )

@app.route('/today_upddate', methods=['GET', 'POST'])
def today_update():
    # User authentication and authorization checks
    if 'user_id' not in session or session.get('blocked') == 1 or session.get('mess_blocked') == 1:
        return redirect('/')

    # Database connection handling
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True, buffered=True)
    except Exception as e:
        # If DB connection fails, show error
        return render_template('manager_meal_amount.html', moneydata=None, message=f"Database connection failed: {str(e)}", previous_meal_charge_datas=None, previous_variable_data=None)

    mess_code = str(session.get('mess_code'))
    users = str((mess_code) + "_users")
    meals = str((mess_code) + "_meals")
    marketing = str((mess_code) + "_marketing")
    marketing_pending = str((mess_code) + "_marketing_pending")
    deposit = str((mess_code) + "_deposit")
    deposit_pending = str((mess_code) + "_deposit_pending")
    meal_charge = str((mess_code) + "_meal_charge")
    variables = str((mess_code) + "_variables")

    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    now = datetime.now().time()
    month_start = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day_of_month = next_month - timedelta(days=1)

    # Get session-pushed messages
    message = session.pop('message', None)

    #How many meals are there for morning
    today_morning_datas = []
    today_total_morning = 0
    type_of_morning = None

    def fetch_morning_data(which_date, type_of_meal):
        typeOrSearch_of_morning = type_of_meal
        try:
            cursor.execute("SELECT name, SUM(CASE WHEN date = %s AND morning = 1 THEN 1 ELSE 0 END) AS morning_sum, SUM(CASE WHEN date = %s THEN guest_morning ELSE 0 END) AS guest_morning_sum FROM `{meals}` GROUP BY name".format(meals=meals), (which_date, which_date))
            todayOrSearch_morning_datas = cursor.fetchall()
            print("todayOrSearch_morning_datas:", todayOrSearch_morning_datas)
            todayOrSearch_total_morning = sum(row['morning_sum'] + int(row['guest_morning_sum']) for row in todayOrSearch_morning_datas)
        except mysql.connector.Error as e:
            print(f"Database error fetching today's morning meals: {str(e)}")
            todayOrSearch_morning_datas = []
        except Exception as e:
            print(f"Unexpected error fetching today's morning meals: {str(e)}")
            todayOrSearch_morning_datas = []
            todayOrSearch_total_morning = 0
        return todayOrSearch_morning_datas, todayOrSearch_total_morning, typeOrSearch_of_morning

    if (now < datetime.strptime('18:00', '%H:%M').time()):
        today_morning_datas, today_total_morning, type_of_morning = fetch_morning_data(today, "Today")
    elif (datetime.strptime('18:00', '%H:%M').time() < now <= datetime.strptime('23:59', '%H:%M').time()):
        type_of_morning = "Tomorrow"
        try:
            cursor.execute("SELECT name, SUM(CASE WHEN date = %s AND morning = 1 THEN 1 ELSE 0 END) AS morning_sum, SUM(CASE WHEN date = %s THEN guest_morning ELSE 0 END) AS guest_morning_sum FROM `{meals}` GROUP BY name".format(meals=meals), (tomorrow, tomorrow))
            today_morning_datas = cursor.fetchall()
            print("today_morning_datas:", today_morning_datas)
            today_total_morning = sum(row['morning_sum'] + int(row['guest_morning_sum']) for row in today_morning_datas)
        except mysql.connector.Error as e:
            print(f"Database error fetching today's morning meals: {str(e)}")
            today_morning_datas = []
        except Exception as e:
            print(f"Unexpected error fetching today's morning meals: {str(e)}")
            today_morning_datas = []
            today_total_morning = 0

    #How many meals are there for night
    today_night_datas = []
    today_total_night = 0
    type_of_night = None

    def fetch_night_data(which_date, type_of_meal):
        typeOrSearch_of_night = type_of_meal
        try:
            cursor.execute("SELECT name, SUM(CASE WHEN date = %s AND night = 1 THEN 1 ELSE 0 END) AS night_sum, SUM(CASE WHEN date = %s THEN guest_night ELSE 0 END) AS guest_night_sum FROM `{meals}` GROUP BY name".format(meals=meals), (which_date, which_date))
            todayOrSearch_night_datas = cursor.fetchall()
            print("todayOrSearch_night_datas:", todayOrSearch_night_datas)
            todayOrSearch_total_night = sum(row['night_sum'] + int(row['guest_night_sum']) for row in todayOrSearch_night_datas)
        except mysql.connector.Error as e:
            print(f"Database error fetching today's night meals: {str(e)}")
            todayOrSearch_night_datas = []
        except Exception as e:
            print(f"Unexpected error fetching today's night meals: {str(e)}")
            todayOrSearch_night_datas = []
            todayOrSearch_total_night = 0
        return todayOrSearch_night_datas, todayOrSearch_total_night, typeOrSearch_of_night

    if (now > datetime.strptime('10:00', '%H:%M').time()):
        today_night_datas, today_total_night, type_of_night = fetch_night_data(today, "Today")

    elif (now < datetime.strptime('10:00', '%H:%M').time()):
        type_of_night = "Yesterday"
        try:
            cursor.execute("SELECT name, SUM(CASE WHEN date = %s AND night = 1 THEN 1 ELSE 0 END) AS night_sum, SUM(CASE WHEN date = %s THEN guest_night ELSE 0 END) AS guest_night_sum FROM `{meals}` GROUP BY name".format(meals=meals), (yesterday, yesterday))
            today_night_datas = cursor.fetchall()
            print("today_night_datas:", today_night_datas)
            today_total_night = sum(row['night_sum'] + int(row['guest_night_sum']) for row in today_night_datas)
        except mysql.connector.Error as e:
            print(f"Database error fetching today's night meals: {str(e)}")
            today_night_datas = []
        except Exception as e:
            print(f"Unexpected error fetching today's night meals: {str(e)}")
            today_night_datas = []
            today_total_night = 0

    #Search by date functionality
    search_date_morning_datas = session.pop('search_date_morning_datas', None)
    search_date_total_morning = session.pop('search_date_total_morning', None)
    search_of_morning = session.pop('search_of_morning', None)

    search_date_night_datas = session.pop('search_date_night_datas', None)
    search_date_total_night = session.pop('search_date_total_night', None)
    search_of_night = session.pop('search_of_night', None)

    if request.method == 'POST':
        search_date_str = request.form.get('search_date')
        if search_date_str:
            try:
                #For morning data
                search_date = datetime.strptime(search_date_str, '%Y-%m-%d').date()
                search_date_morning_datas, search_date_total_morning, search_of_morning = fetch_morning_data(search_date, str(search_date))
                session['search_date_morning_datas'] = search_date_morning_datas
                session['search_date_total_morning'] = search_date_total_morning
                session['search_of_morning'] = search_of_morning

                #For night data
                search_date_night_datas, search_date_total_night, search_of_night = fetch_night_data(search_date, str(search_date))
                session['search_date_night_datas'] = search_date_night_datas
                session['search_date_total_night'] = search_date_total_night
                session['search_of_night'] = search_of_night
                return redirect(url_for('today_update'))
            except ValueError:
                message = "Invalid date format."
                session['message'] = message
                return redirect(url_for('today_update'))
            except Exception as e:
                message = f"Error processing date search: {str(e)}"
                session['message'] = message
                return redirect(url_for('today_update'))
        else:
            message = "Please select a date."
            session['message'] = message
            return redirect(url_for('today_update'))
    
    return render_template('today_update.html', 
                            todayOrSearch_morning_datas = search_date_morning_datas if search_date_morning_datas else today_morning_datas, 
                            todayOrSearch_total_morning=search_date_total_morning if search_date_total_morning else today_total_morning,   
                            message=message, 
                            typeOrSearch_of_morning=search_of_morning if search_of_morning else type_of_morning, 
                            todayOrSearch_night_datas=search_date_night_datas if search_date_night_datas else today_night_datas, 
                            todayOrSearch_total_night=search_date_total_night if search_date_total_night else today_total_night, 
                            typeOrSearch_of_night=search_of_night if search_of_night else type_of_night)

if __name__ == '__main__':
    app.run(debug=True)


