from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='682022',
    db='gym_management',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Routes
@app.route('/')
def login():
    return render_template("index.html")

@app.route('/homeAdmin')
def home_admin():
    return render_template("home_admin.html")

@app.route('/homeMember')
def home_member():
    return render_template("home_member.html")

@app.route('/addMember')
def add_member_page():
    return render_template("add_member.html", success='')

@app.route('/addTrainer')
def add_trainer_page():
    return render_template("add_trainer.html", success='')

@app.route('/addSchedule')
def add_schedule_page():
    return render_template("add_schedule.html", success='')

@app.route('/addMemberReq', methods=['POST'])
def add_member():
    name = request.form['name'].strip()
    email = request.form['email'].strip()
    if name == '' or email == '':
        return render_template("add_member.html", success='Name or Email cannot be empty')
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `member` (`name`, `email`) VALUES (%s, %s)"
            cursor.execute(sql, (name, email))
            connection.commit()
            return render_template("add_member.html", success='Member added successfully')
    except Exception as e:
        return render_template("add_member.html", success='Can\'t add Member: ' + str(e))

@app.route('/addTrainerReq', methods=['POST'])
def add_trainer():
    name = request.form['name'].strip()
    specialty = request.form['specialty'].strip()
    if name == '' or specialty == '':
        return render_template("add_trainer.html", success='Name or Specialty cannot be empty')
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `trainer` (`name`, `specialty`) VALUES (%s, %s)"
            cursor.execute(sql, (name, specialty))
            connection.commit()
            return render_template("add_trainer.html", success='Trainer added successfully')
    except Exception as e:
        return render_template("add_trainer.html", success='Can\'t add Trainer: ' + str(e))

@app.route('/addScheduleReq', methods=['POST'])
def add_schedule():
    trainer_id = request.form['trainer_id'].strip()
    day = request.form['day'].strip()
    time = request.form['time'].strip()
    if trainer_id == '' or day == '' or time == '':
        return render_template("add_schedule.html", success='Please fill all fields.')
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `schedule`(`trainer_id`, `day`, `time`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (trainer_id, day, time))
            connection.commit()
            return render_template("add_schedule.html", success='Schedule added successfully')
    except Exception as e:
        return render_template("add_schedule.html", success='Can\'t add Schedule: ' + str(e))

@app.route('/viewMembers')
def view_members_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `member`"
            cols = ['id', 'name', 'email']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_members.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_members.html", items=[], cols=[], success='Can\'t view Members: ' + str(e))

@app.route('/viewTrainers')
def view_trainers_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `trainer`"
            cols = ['id', 'name', 'specialty']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_trainers.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_trainers.html", items=[], cols=[], success='Can\'t view Trainers: ' + str(e))

@app.route('/viewSchedules')
def view_schedules_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT schedule.id, trainer.name, schedule.day, schedule.time FROM `schedule` JOIN `trainer` ON schedule.trainer_id = trainer.id"
            cols = ['id', 'trainer', 'day', 'time']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_schedules.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_schedules.html", items=[], cols=[], success='Can\'t view Schedules: ' + str(e))

@app.route('/deleteMember')
def delete_member_page():
    return render_template("delete_member.html", success='')

@app.route('/deleteTrainer')
def delete_trainer_page():
    return render_template("delete_trainer.html", success='')

@app.route('/deleteSchedule')
def delete_schedule_page():
    return render_template("delete_schedule.html", success='')

@app.route('/deleteMemberReq', methods=['POST'])
def delete_member():
    member_id = request.form['id'].strip()
    if member_id == '':
        return render_template("delete_member.html", success='ID cannot be empty')
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `member` WHERE `id`=%s"
            cursor.execute(sql, (member_id,))
            connection.commit()
            return render_template("delete_member.html", success='Member deleted successfully')
    except Exception as e:
        return render_template("delete_member.html", success='Can\'t delete Member: ' + str(e))

@app.route('/deleteTrainerReq', methods=['POST'])
def delete_trainer():
    trainer_id = request.form['id'].strip()
    if trainer_id == '':
        return render_template("delete_trainer.html", success='ID cannot be empty')
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `trainer` WHERE `id`=%s"
            cursor.execute(sql, (trainer_id,))
            connection.commit()
            return render_template("delete_trainer.html", success='Trainer deleted successfully')
    except Exception as e:
        return render_template("delete_trainer.html", success='Can\'t delete Trainer: ' + str(e))

@app.route('/deleteScheduleReq', methods=['POST'])
def delete_schedule():
    schedule_id = request.form['id'].strip()
    if schedule_id == '':
        return render_template("delete_schedule.html", success='ID cannot be empty')
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `schedule` WHERE `id`=%s"
            cursor.execute(sql, (schedule_id,))
            connection.commit()
            return render_template("delete_schedule.html", success='Schedule deleted successfully')
    except Exception as e:
        return render_template("delete_schedule.html", success='Can\'t delete Schedule: ' + str(e))

if __name__ == '__main__':
    app.run(debug=True)