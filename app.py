from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Ajibur@2003',
        database='mess_management'
    )


@app.route('/')
def home():
    today = datetime.today().date()
    month_start = today.replace(day=1)

    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)

        # Get today's totals
        cursor.execute("""
            SELECT 
                SUM(morning) AS total_morning, 
                SUM(night) AS total_night 
            FROM meals 
            WHERE date = %s
        """, (today,))
        totals = cursor.fetchone()

        total_morning = totals['total_morning'] or 0
        total_night = totals['total_night'] or 0
        
        # Sum meals from the start of the month to today
        cursor.execute("""
            SELECT 
                SUM(morning) AS grand_total_morning, 
                SUM(night) AS grand_total_night 
            FROM meals 
            WHERE date BETWEEN %s AND %s
        """, (month_start, today))
        
        grand_totals = cursor.fetchone()
        grand_total_morning = grand_totals['grand_total_morning'] or 0
        grand_total_night = grand_totals['grand_total_night'] or 0
        grand_total = grand_total_morning + grand_total_night

    # Now safe to use totals outside the with block
    return render_template('index.html',
                        total_morning=total_morning,
                        total_night=total_night,
                        grand_total_morning = grand_total_morning,
                        grand_total_night = grand_total_night,
                        grand_total = grand_total 
                        # other context variables...
                        )



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username'].lower()
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        # Register user
        cursor.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)", (name, username, password))
        conn.commit()

        # Create personal table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{username}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                morning TINYINT(1) DEFAULT 0,
                night TINYINT(1) DEFAULT 0
            )
        """)
        conn.commit()

        conn.close()
        return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username'].lower()
            return redirect('/dashboard')
        else:
            return "Invalid login credentials"

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    message = None
    today = datetime.today().date()
    now = datetime.now().time()
    month_start = today.replace(day=1)

    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)

        # Ensure personal table exists
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `{username}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                morning TINYINT(1) DEFAULT 0,
                night TINYINT(1) DEFAULT 0
            )
        """)
        conn.commit()

        def update_personal_table(date_obj, morning, night):
            cursor.execute(f"""
                INSERT INTO `{username}` (date, morning, night)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE morning=VALUES(morning), night=VALUES(night)
            """, (date_obj, int(morning), int(night)))
            conn.commit()

        def update_global_meals_table(username, date_obj, morning, night):
            cursor.execute(f"""
                INSERT INTO meals (name, date, morning, night)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE morning=VALUES(morning), night=VALUES(night)
            """, (username, date_obj, int(morning), int(night)))
            conn.commit()

        if request.method == 'POST':
            mode = request.form.get('meal_mode')
            toggle = 1 if request.form.get('toggle') == 'on' else 0

            if mode == 'continue':
                selected_option = request.form.get('continue_option')

                tonight_start = datetime.strptime('00:00', '%H:%M').time()
                tonight_end = datetime.strptime('16:00', '%H:%M').time()
                tomorrow_morning_start = datetime.strptime('00:00', '%H:%M').time()
                tomorrow_morning_day_end = datetime.strptime('23:59', '%H:%M').time()
                tomorrow_morning_day_start = datetime.strptime('00:00', '%H:%M').time()
                tomorrow_morning_end = datetime.strptime('04:00', '%H:%M').time()

                next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
                last_day_of_month = next_month - timedelta(days=1)

                if selected_option == 'tonight' and tonight_start <= now <= tonight_end:
                    cursor.execute(f"SELECT morning FROM `{username}` WHERE date = %s", (today,))
                    result = cursor.fetchone()
                    preserved_morning = result['morning'] if result else 0

                    current_day = today
                    while current_day <= last_day_of_month:
                        morning = preserved_morning if current_day == today else toggle
                        night = toggle
                        update_personal_table(current_day, morning, night)
                        update_global_meals_table(username, current_day, morning, night)
                        current_day += timedelta(days=1)
                    message = f"Today's morning preserved. Meals updated from tonight to {last_day_of_month}."

                elif selected_option == 'tomorrow_morning':
                    if tomorrow_morning_start <= now <= tomorrow_morning_day_end:
                        current_day = today + timedelta(days=1)
                        while current_day <= last_day_of_month:
                            morning = toggle
                            night = toggle
                            update_personal_table(current_day, morning, night)
                            update_global_meals_table(username, current_day, morning, night)
                            current_day += timedelta(days=1)
                        message = f"Meals updated from tomorrow morning to {last_day_of_month}."
                    elif tomorrow_morning_day_start <= now <= tomorrow_morning_end:
                        current_day = today
                        while current_day <= last_day_of_month:
                            morning = toggle
                            night = toggle
                            update_personal_table(current_day, morning, night)
                            update_global_meals_table(username, current_day, morning, night)
                            current_day += timedelta(days=1)
                        message = f"Meals updated from tomorrow morning to {last_day_of_month}."
                    else:
                        message = f"Time out. Do not update."

                elif selected_option == 'tomorrow_night' and today:
                        cursor.execute(f"SELECT morning FROM `{username}` WHERE date = %s", (today + timedelta(days=1),))
                        result = cursor.fetchone()
                        preserved_morning = result['morning'] if result else 0

                        current_day = today + timedelta(days=1)
                        while current_day <= last_day_of_month:
                            morning = preserved_morning if current_day == today + timedelta(days=1) else toggle
                            night = toggle
                            update_personal_table(current_day, morning, night)
                            update_global_meals_table(username, current_day, morning, night)
                            current_day += timedelta(days=1)
                        message = f"Tomorrow's morning preserved. Meals updated from tomorrow night to {last_day_of_month}."

                else:
                    message = "Invalid time or selection for Continue option."

            elif mode == 'just_night':
                if datetime.strptime('00:00', '%H:%M').time() <= now <= datetime.strptime('17:00', '%H:%M').time():
                    cursor.execute(f"SELECT morning, night FROM `{username}` WHERE date = %s", (today,))
                    result = cursor.fetchone()

                    # Default values if no row exists
                    morning = result['morning'] if result else 0
                    current_night = result['night'] if result else 0

                    # Toggle night value
                    new_night = 0 if current_night == 1 else 1

                    # Update both tables
                    update_personal_table(today, morning, new_night)
                    update_global_meals_table(username, today, morning, new_night)

                    message = f"Night meal {'ON' if new_night else 'OFF'} for today."

            elif mode == 'just_morning':
                six_am = datetime.strptime('06:00', '%H:%M').time()
                end_day = datetime.strptime('23:59', '%H:%M').time()
                midnight = datetime.strptime('00:00', '%H:%M').time()
                three_am = datetime.strptime('03:00', '%H:%M').time()

                if midnight <= now <= three_am:
                    # Toggle today's morning meal
                    cursor.execute(f"SELECT morning, night FROM `{username}` WHERE date = %s", (today,))
                    result = cursor.fetchone()

                    current_morning = result['morning'] if result else 0
                    night = result['night'] if result else 0

                    new_morning = 0 if current_morning == 1 else 1

                    update_personal_table(today, new_morning, night)
                    update_global_meals_table(username, today, new_morning, night)

                    message = f"Today's morning meal {'ON' if new_morning else 'OFF'}."

                elif six_am <= now <= end_day:
                    # Toggle tomorrow's morning meal
                    tomorrow = today + timedelta(days=1)

                    cursor.execute(f"SELECT morning, night FROM `{username}` WHERE date = %s", (tomorrow,))
                    result = cursor.fetchone()

                    current_morning = result['morning'] if result else 0
                    night = result['night'] if result else 0

                    new_morning = 0 if current_morning == 1 else 1

                    update_personal_table(tomorrow, new_morning, night)
                    update_global_meals_table(username, tomorrow, new_morning, night)

                    message = f"Tomorrow's morning meal {'ON' if new_morning else 'OFF'}."

                else:
                    message = "Just Morning updates are allowed from 12:00 AM–3:00 AM or 6:00 AM–11:59 PM."

            elif mode == 'tomorrow_night':
                if today:
                    # Toggle tomorrow's night meal
                    tomorrow = today + timedelta(days=1)

                    cursor.execute(f"SELECT morning, night FROM `{username}` WHERE date = %s", (tomorrow,))
                    result = cursor.fetchone()

                    morning = result['morning'] if result else 0
                    current_night = result['night'] if result else 0
                    new_night = 0 if current_night == 1 else 1

                    update_personal_table(tomorrow, morning, new_night)
                    update_global_meals_table(username, tomorrow, morning, new_night)

                    message = f"Tomorrow's night meal toggled {'ON' if new_night else 'OFF'}."

                else:
                    message = "Tomorrow Night update is allowed only between 12:00 AM–3:00 AM or 6:00 AM–12:00 AM."
            
        cursor.execute(f"""
            SELECT 
                SUM(morning) AS total_morning, 
                SUM(night) AS total_night 
            FROM `{username}` 
            WHERE date BETWEEN %s AND %s
        """, (month_start, today))
        
        totals = cursor.fetchone()
        total_morning = totals['total_morning'] or 0
        total_night = totals['total_night'] or 0
        total = total_morning + total_night



        # Load recent personal meals
        cursor.execute(f"SELECT * FROM `{username}` ORDER BY date")
        meals = cursor.fetchall()

    return render_template('dashboard.html', meals=meals, username=username, message=message, total_morning = total_morning,
                        total_night = total_night,total = total, today=today )
                        


if __name__ == '__main__':
    app.run(debug=True)