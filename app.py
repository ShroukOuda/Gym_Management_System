

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pymysql

app = Flask(__name__)
from config import Config
app.config.from_object(Config)



pymysql.install_as_MySQLdb()

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # admin, secretary, trainer, member
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    membership_type = db.Column(db.String(50), nullable=False)
    membership_start = db.Column(db.Date, nullable=False)
    membership_end = db.Column(db.Date, nullable=False)

    user = db.relationship('User', backref=db.backref('member_profile', uselist=False))
    attendances = db.relationship('Attendance', backref='member', lazy=True)
    enrollments = db.relationship('Enrollment', backref='member', lazy=True)

class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    specialization = db.Column(db.String(100), nullable=False)
  
    
    user = db.relationship('User', backref=db.backref('trainer_profile', uselist=False))
    classes = db.relationship('GymClass', backref='trainer', lazy=True)
class Secretary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    
    user = db.relationship('User', backref=db.backref('secretary_profile', uselist=False))
    attendances = db.relationship('Attendance', backref='secretary', lazy=True)
class GymClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    schedule_day = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    enrollments = db.relationship('Enrollment', backref='gym_class', lazy=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('gym_class.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    secretary_id = db.Column(db.Integer, db.ForeignKey('secretary.id'), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out = db.Column(db.DateTime)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.Date)
    last_maintenance = db.Column(db.Date)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    role = session['role']
    
    if role == 'admin':
        return render_template('admin_dashboard.html', user=user)
    elif role == 'secretary':
        secretary = Secretary.query.filter_by(user_id=user.id).first()
        return render_template('secretary_dashboard.html', user=user, secretary=secretary)
    elif  role == 'trainer':
        trainer = Trainer.query.filter_by(user_id=user.id).first()
        return render_template('trainer_dashboard.html', user=user, trainer=trainer)
    else:
        member = Member.query.filter_by(user_id=user.id).first()
        return render_template('member_dashboard.html', user=user, member=member)
# Member Routes
@app.route('/members')
def members_list():
    if 'user_id' not in session or session['role'] not in ['admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    members = Member.query.all()
    return render_template('members_list.html', members=members)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if 'user_id' not in session or session['role'] not in ['admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Create user first
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('add_member.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('add_member.html')
        
        user = User(username=username, email=email, role='member')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to get user.id
        
        # Create member profile
        member = Member(
            user_id=user.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            membership_type=request.form.get('membership_type'),
            membership_start=datetime.strptime(request.form.get('membership_start'), '%Y-%m-%d'),
            membership_end=datetime.strptime(request.form.get('membership_end'), '%Y-%m-%d'),
        )
        
        db.session.add(member)
        db.session.commit()
        
        flash('Member added successfully', 'success')
        return redirect(url_for('members_list'))
    
    return render_template('add_member.html')

@app.route('/members/edit/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    if 'user_id' not in session or session['role'] not in ['admin', 'staff', 'trainer']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    member = Member.query.get_or_404(id)
    
    if request.method == 'POST':
        member.first_name = request.form.get('first_name')
        member.last_name = request.form.get('last_name')
        member.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d')
        member.phone = request.form.get('phone')
        member.address = request.form.get('address')
        member.membership_type = request.form.get('membership_type')
        member.membership_start = datetime.strptime(request.form.get('membership_start'), '%Y-%m-%d')
        member.membership_end = datetime.strptime(request.form.get('membership_end'), '%Y-%m-%d')
    
        db.session.commit()
        flash('Member updated successfully', 'success')
        return redirect(url_for('members_list'))
    
    return render_template('edit_member.html', member=member)

# Trainer Routes
@app.route('/trainers')
def trainers_list():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    trainers = Trainer.query.all()
    return render_template('trainers_list.html', trainers=trainers)
@app.route('/trainers/add', methods=['GET', 'POST'])
def add_trainer():
    if 'user_id' not in session or session['role'] not in ['admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Create user first
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('add_trainer.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('add_trainer.html')
        
        user = User(username=username, email=email, role='trainer')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to get user.id
        
        # Create trainer profile
        trainer = Trainer(
            user_id=user.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            specialization=request.form.get('specialization')
        )
        
        db.session.add(trainer)
        db.session.commit()
        
        flash('Trainer added successfully', 'success')
        return redirect(url_for('trainers_list'))
    
    return render_template('add_trainer.html')

@app.route('/trainers/edit/<int:id>', methods=['GET', 'POST'])
def edit_trainer(id):
    if 'user_id' not in session or session['role'] not in ['admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    trainer = Trainer.query.get_or_404(id)
    
    if request.method == 'POST':
        trainer.first_name = request.form.get('first_name')
        trainer.last_name = request.form.get('last_name')
        trainer.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d')
        trainer.phone = request.form.get('phone')
        trainer.address = request.form.get('address')
        trainer.specialization = request.form.get('specialization')
        db.session.commit()
        flash('Trainer updated successfully', 'success')
        return redirect(url_for('trainers_list'))
    
    return render_template('edit_trainer.html', trainer=trainer)

#Secretary Routes
@app.route('/secretaries')
def secretaries_list():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    secretaries = Secretary.query.all()
    return render_template('secretaries_list.html', secretaries=secretaries)
@app.route('/secretaries/add', methods=['GET', 'POST'])
def add_secretary():
    if 'user_id' not in session or session['role'] not in ['admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Create user first
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('add_secretary.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('add_secretary.html')
        
        user = User(username=username, email=email, role='secretary')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to get user.id
        
        # Create secretary profile
        secretary = Secretary(
            user_id=user.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            
        )
        
        db.session.add(secretary)
        db.session.commit()
        
        flash('Seretary added successfully', 'success')
        return redirect(url_for('secretaries_list'))
    
    return render_template('add_secretary.html')

@app.route('/secretaries/edit/<int:id>', methods=['GET', 'POST'])
def edit_secretary(id):
    if 'user_id' not in session or session['role'] not in ['admin']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    secretary = Secretary.query.get_or_404(id)
    
    if request.method == 'POST':
        secretary.first_name = request.form.get('first_name')
        secretary.last_name = request.form.get('last_name')
        secretary.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d')
        secretary.phone = request.form.get('phone')
        secretary.address = request.form.get('address')

        db.session.commit()
        flash('Secretary updated successfully', 'success')
        return redirect(url_for('secretaries_list'))
    
    return render_template('edit_secretary.html', secretary=secretary)
# Class Routes
@app.route('/classes')
def classes_list():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    classes = GymClass.query.all()
    return render_template('classes_list.html', classes=classes)

@app.route('/classes/add', methods=['GET', 'POST'])
def add_class():
    if 'user_id' not in session or session['role'] not in ['admin', 'staff']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        gym_class = GymClass(
            name=request.form.get('name'),
            description=request.form.get('description'),
            trainer_id=request.form.get('trainer_id'),
            capacity=request.form.get('capacity'),
            schedule_day=request.form.get('schedule_day'),
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        )
        
        db.session.add(gym_class)
        db.session.commit()
        flash('Class added successfully', 'success')
        return redirect(url_for('classes_list'))
    
    trainers = Trainer.query.all()
    return render_template('add_class.html', trainers=trainers)
# trainer class routes

@app.route('/trainer/classes')
def trainer_classes():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    # Get the current user and check if they are a trainer
    user = User.query.get(session['user_id'])
    trainer = Trainer.query.filter_by(user_id=user.id).first()
    
    # If not a trainer or not found, redirect with error
    if not trainer:
        flash('Access restricted to trainers only', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all classes assigned to this trainer
    classes = GymClass.query.filter_by(trainer_id=trainer.id).all()
    
    # For each class, calculate how many students are enrolled
    for gym_class in classes:
        gym_class.enrolled_count = Enrollment.query.filter_by(class_id=gym_class.id).count()
    
    return render_template('trainer_classes.html', classes=classes, trainer=trainer)

@app.route('/trainer/class/<int:class_id>')
def trainer_class_detail(class_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    trainer = Trainer.query.filter_by(user_id=user.id).first()
    
    if not trainer:
        flash('Access restricted to trainers only', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get the specific class and verify it belongs to this trainer
    gym_class = GymClass.query.get_or_404(class_id)
    
    if gym_class.trainer_id != trainer.id:
        flash('You are not authorized to view this class', 'danger')
        return redirect(url_for('trainer_classes'))
    
    # Get all enrollments for this class
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    
    # Get member information for each enrollment
    enrolled_members = []
    for enrollment in enrollments:
        member = Member.query.get(enrollment.member_id)
        enrolled_members.append({
            'member': member,
            'enrollment_date': enrollment.enrollment_date
        })
    
    return render_template('trainer_class_detail.html', 
                           gym_class=gym_class, 
                           enrolled_members=enrolled_members,
                           trainer=trainer)

@app.route('/trainer/class/update/<int:class_id>', methods=['GET', 'POST'])
def update_class_details(class_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    trainer = Trainer.query.filter_by(user_id=user.id).first()
    
    if not trainer:
        flash('Access restricted to trainers only', 'danger')
        return redirect(url_for('dashboard'))
    
    gym_class = GymClass.query.get_or_404(class_id)
    
    if gym_class.trainer_id != trainer.id:
        flash('You are not authorized to update this class', 'danger')
        return redirect(url_for('trainer_classes'))
    
    if request.method == 'POST':
        gym_class.name = request.form.get('name')
        gym_class.description = request.form.get('description')
        gym_class.schedule_day = request.form.get('schedule_day')
        gym_class.start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        gym_class.end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        
        db.session.commit()
        flash('Class details updated successfully', 'success')
        return redirect(url_for('trainer_class_detail', class_id=class_id))
    
    return render_template('update_class.html', gym_class=gym_class, trainer=trainer)

# Attendance Routes
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user_id' not in session or session['role'] not in ['admin', 'secretary']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    
    # Get secretary profile for the current user
    secretary = None
    if session['role'] == 'secretary':
        secretary = Secretary.query.filter_by(user_id=user.id).first()
    elif session['role'] == 'admin':
        # For admin, we'll use the first secretary or create a placeholder
        secretary = Secretary.query.first()
        if not secretary:
            flash('No secretary account found in the system. Please create one first.', 'warning')
            return redirect(url_for('secretaries_list'))
    
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        attendance_type = request.form.get('attendance_type')
        
        if attendance_type == 'check_in':
            # Check if member already checked in
            existing_attendance = Attendance.query.filter_by(member_id=member_id, check_out=None).first()
            if existing_attendance:
                flash('Member already checked in', 'warning')
            else:
                attendance = Attendance(
                    member_id=member_id,
                    secretary_id=secretary.id,
                    check_in=datetime.utcnow()
                )
                db.session.add(attendance)
                db.session.commit()
                flash('Check-in recorded', 'success')
        else:  # check_out
            attendance = Attendance.query.filter_by(member_id=member_id, check_out=None).first()
            if attendance:
                attendance.check_out = datetime.utcnow()
                db.session.commit()
                flash('Check-out recorded', 'success')
            else:
                flash('No active check-in found for this member', 'warning')
    
    members = Member.query.all()
    attendances = Attendance.query.filter(Attendance.check_in >= datetime.today().replace(hour=0, minute=0, second=0))
    return render_template('attendance.html', members=members, attendances=attendances)

# Class Enrollment Routes
@app.route('/enroll/<int:class_id>', methods=['POST'])
def enroll_class(class_id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    member = Member.query.filter_by(user_id=user.id).first()
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(member_id=member.id, class_id=class_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this class', 'warning')
        return redirect(url_for('classes_list'))
    
    # Check class capacity
    gym_class = GymClass.query.get(class_id)
    enrolled_count = Enrollment.query.filter_by(class_id=class_id).count()
    
    if enrolled_count >= gym_class.capacity:
        flash('Class is already at full capacity', 'warning')
        return redirect(url_for('classes_list'))
    
    enrollment = Enrollment(member_id=member.id, class_id=class_id)
    db.session.add(enrollment)
    db.session.commit()
    flash('Successfully enrolled in class', 'success')
    return redirect(url_for('classes_list'))

# Equipment Routes
@app.route('/equipment')
def equipment_list():
    if 'user_id' not in session or session['role'] not in ['admin', 'staff']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    equipment = Equipment.query.all()
    return render_template('equipment_list.html', equipment=equipment)

@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    if 'user_id' not in session or session['role'] not in ['admin', 'staff']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        equipment = Equipment(
            name=request.form.get('name'),
            description=request.form.get('description'),
            quantity=request.form.get('quantity'),
            purchase_date=datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d'),
            last_maintenance=datetime.strptime(request.form.get('last_maintenance'), '%Y-%m-%d')
        )
        
        db.session.add(equipment)
        db.session.commit()
        flash('Equipment added successfully', 'success')
        return redirect(url_for('equipment_list'))
    
    return render_template('add_equipment.html')

# Create database tables
@app.cli.command('create_tables')
def create_tables():
    db.create_all()
    print('Tables created successfully')

# Create admin user
@app.cli.command('create_admin')
def create_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@gym.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin user already exists')

if __name__ == '__main__':
    app.run(debug=True)