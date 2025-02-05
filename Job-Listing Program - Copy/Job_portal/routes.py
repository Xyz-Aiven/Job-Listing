from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Job, User, Application
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

# Hashed admin code for checking
hashed_admin_code = generate_password_hash("XYOUZ")

@main.route('/')
def index():
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.signup'))
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Sign up successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@main.route('/logout', methods=['POST']) 
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/add', methods=['GET', 'POST'])
def add_job():
    if 'user_id' not in session:
        flash('You must be logged in to post a job.', 'danger')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_job = Job(title=title, description=description, user_id=session['user_id'])
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('main.job_list'))
    return render_template('add_job.html')

@main.route('/jobs')
def job_list():
    jobs = Job.query.all()
    applications = {job.id: job.applications for job in jobs}
    return render_template('job_list.html', jobs=jobs, applications=applications)

@main.route('/apply/<int:job_id>', methods=['POST'])
def apply(job_id):
    if 'user_id' not in session:
        flash('You must be logged in to apply for a job.', 'danger')
        return redirect(url_for('main.login'))

    message = request.form['message']
    portfolio_link = request.form['portfolio_link']
    new_application = Application(message=message, portfolio_link=portfolio_link, job_id=job_id, user_id=session['user_id'])
    db.session.add(new_application)
    db.session.commit()
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('main.job_list'))

@main.route('/check_admin_code', methods=['POST'])
def check_admin_code():
    code = request.form['code']
    if check_password_hash(hashed_admin_code, code):
        session['is_admin'] = True
        return redirect(url_for('main.admin'))
    else:
        flash('Invalid code. Please enter the correct 5-letter code.', 'danger')
        return redirect(url_for('main.admin_code_form'))

@main.route('/admin_code_form', methods=['GET', 'POST'])
def admin_code_form():
    if request.method == 'POST':
        return check_admin_code()
    return render_template('admin_code_form.html')

@main.route('/admin')
def admin():
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('main.admin_code_form'))  # Redirect to admin code form if not an admin
    
    jobs = Job.query.all()
    applications = {job.id: job.applications for job in jobs}
    return render_template('admin.html', jobs=jobs, applications=applications)

@main.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        job.title = request.form['title']
        job.description = request.form['description']
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('main.job_list'))
    return render_template('edit_job.html', job=job)

@main.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)  # Fetch the job or return a 404 if not found
    applications = job.applications  # Get associated applications
    for application in applications:
        db.session.delete(application)  # Delete each application
    db.session.delete(job)  # Delete the job
    db.session.commit()  # Commit the changes
    flash('Job and associated applications deleted successfully!', 'success')  # Flash success message
    return redirect(url_for('main.admin'))  # Redirect to admin page

@main.route('/exit_admin_panel', methods=['POST'])
def exit_admin_panel():
    session.pop('is_admin', None)
    flash('You have exited the admin panel.', 'info')
    return redirect(url_for('main.index'))