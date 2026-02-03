from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration - Use environment variables in production
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here_change_in_production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Portfolio data derived from resume (JAHNAVI PASUMARTHI)
PORTFOLIO_ITEMS = [
    {
        'id': 1,
        'title': 'Automatic Dustbin (Arduino)',
        'description': 'Arduino-based automatic dustbin using ultrasonic sensors, LEDs, buzzer and a servo motor for contactless lid opening. Sensor-triggered actions with optimized response time and efficient power usage for real-time operation.',
        'image': 'dustbin.jpg',
        'technologies': ['Arduino', 'Ultrasonic Sensor', 'Servo Motor', 'C', 'Embedded Systems']
    },
    {
        'id': 2,
        'title': 'Breast Cancer Prediction',
        'description': 'Machine learning models for early breast cancer detection using feature engineering and algorithms such as Random Forest and SVM. Implemented preprocessing, model training and evaluation to deliver high-accuracy predictions.',
        'image': 'breast_cancer.jpg',
        'technologies': ['Python', 'scikit-learn', 'pandas', 'NumPy', 'Machine Learning']
    },
    {
        'id': 3,
        'title': 'House Price Prediction',
        'description': 'Regression-based house price prediction project involving data cleaning, feature engineering and predictive modeling to estimate property values and uncover trends.',
        'image': 'house_price.jpg',
        'technologies': ['Python', 'scikit-learn', 'pandas', 'NumPy', 'Regression']
    }
]

SKILLS = {
    'Programming Languages': ['C', 'Java', 'Python'],
    'Data Science': ['pandas', 'NumPy', 'scikit-learn', 'Machine Learning', 'Feature Engineering'],
    'Databases': ['SQL'],
    'Embedded Systems': ['Arduino', 'Ultrasonic Sensor', 'Servo Motor'],
    'Tools': ['Git', 'Arduino IDE']
}

# Structured resume data for templates
RESUME_DATA = {
    'name': 'JAHNAVI PASUMARTHI',
    'contact': 'Sathupally | 9392044591 | jahnavipasumarthi33@gmail.com',
    'email': 'jahnavipasumarthi33@gmail.com',
    'phone': '9392044591',
    'location': 'Sathupally',
    'summary': 'To secure a challenging position in a reputable organization where I can utilize and further develop my technical skills, expand my knowledge, and contribute to the company\'s success.',
    'certifications': [
        'Data Science For Beginners - NPTEL',
        'Hackathon & Workshop on Data Science, ML & AI',
        'Cisco Networking Academy Certification in Programming Essentials (C)'
    ],
    'education': [
        { 'degree': 'B.Tech (Artificial Intelligence & Machine Learning)', 'years': '2023 - 2026', 'institution': 'Mother Teresa Institute of Science & Technology, Sathupally', 'aggregate': '8.0' },
        { 'degree': 'Diploma (ECE)', 'years': '2020 - 2023', 'institution': 'Mother Teresa Institute of Science & Technology, Sathupally', 'aggregate': '7.41' },
        { 'degree': '10th Class', 'years': '2019 - 2020', 'institution': 'Krishnaveni Talent School, Sathupally', 'aggregate': '9.7' }
    ],
    'skills': SKILLS,
    'projects': [
        { 'title': 'Automatic Dustbin (Arduino)', 'description': 'Designed and implemented an Arduino-based automatic dustbin using ultrasonic sensors, LED, buzzer and a servo motor for contactless lid opening. Programmed sensor-triggered actions and optimized response time for reliable operation.' },
        { 'title': 'Breast Cancer Prediction', 'description': 'Built ML models to predict breast cancer with emphasis on preprocessing, feature selection, and evaluation using algorithms like Random Forest and SVM.' },
        { 'title': 'House Price Prediction', 'description': 'Applied regression techniques and feature engineering to predict house prices and extract actionable insights from real estate data.' }
    ]
} 

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Routes ====================

@app.route('/')
def index():
    """Home page with portfolio overview"""
    visits = session.get('visits', 0)
    visits += 1
    session['visits'] = visits
    
    # Check for flash messages
    message = request.args.get('message', None)
    if message:
        flash(message, 'info')
    
    return render_template('index.html', projects=PORTFOLIO_ITEMS[:3], skills=SKILLS)

@app.route('/about')
def about():
    """About page"""
    user_name = session.get('user', 'Guest')
    # Provide resume data so the About page can render the latest resume details
    return render_template('about.html', user_name=user_name, resume_data=RESUME_DATA)

@app.route('/portfolio')
def portfolio():
    """Portfolio/Projects page"""
    # Pass structured resume data so the template can show contact, summary, skills, certifications and education
    return render_template('portfolio.html', projects=PORTFOLIO_ITEMS, skills=SKILLS, resume_data=RESUME_DATA)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Individual project detail page with variable rule"""
    project = next((p for p in PORTFOLIO_ITEMS if p['id'] == project_id), None)
    if project is None:
        flash('Project not found!', 'danger')
        return redirect(url_for('portfolio'))
    return render_template('project_detail.html', project=project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate form data
        if not all([name, email, subject, message]):
            flash('Please fill in all required fields!', 'danger')
            return redirect(url_for('contact'))
        
        # Save contact message (in production, send email)
        contact_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store in session for demo purposes
        contacts = session.get('contacts', [])
        contacts.append(contact_data)
        session['contacts'] = contacts
        
        flash(f'Thank you {name}! Your message has been received. I will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    
    # Pass resume data so the contact page can prefill and show contact details
    return render_template('contact.html', resume_data=RESUME_DATA) 

@app.route('/skills')
def skills():
    """Skills page"""
    return render_template('skills.html', skills=SKILLS)

@app.route('/services')
def services():
    """Services page"""
    services_list = [
        {
            'title': 'Web Development',
            'description': 'Full-stack web development with modern frameworks',
            'icon': '💻'
        },
        {
            'title': 'API Development',
            'description': 'RESTful and GraphQL API development',
            'icon': '⚙️'
        },
        {
            'title': 'Database Design',
            'description': 'Database architecture and optimization',
            'icon': '🗄️'
        },
        {
            'title': 'Consulting',
            'description': 'Technical consulting and code review',
            'icon': '📋'
        }
    ]
    return render_template('services.html', services=services_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Simple authentication (in production, use proper database)
        if username and password == 'password123':
            session['user'] = username
            
            # Set session expiration
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=7)
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = session.get('user')
    contacts = session.get('contacts', [])
    visits = session.get('visits', 0)
    
    return render_template('dashboard.html', user=user, contacts=contacts, visits=visits)

@app.route('/logout')
def logout():
    """Logout user"""
    user = session.get('user', 'User')
    session.clear()
    flash(f'Goodbye, {user}! You have been logged out.', 'info')
    return redirect(url_for('index', message=f'{user} logged out successfully!'))

@app.route('/resume', methods=['GET', 'POST'])
def resume():
    """Resume upload and download page"""
    if request.method == 'POST':
        # Check if file is in request
        if 'resume_file' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(url_for('resume'))
        
        file = request.files['resume_file']
        
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(url_for('resume'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Store in session
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append({
                'filename': filename,
                'original_name': request.files['resume_file'].filename,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            session['uploaded_files'] = uploaded_files
            
            flash('Resume uploaded successfully!', 'success')
            return redirect(url_for('resume'))
        else:
            flash('Invalid file type! Allowed types: pdf, txt, doc, docx, png, jpg, jpeg, gif', 'danger')
    
    uploaded_files = session.get('uploaded_files', [])
    # Ensure the default resume file (provided from the resume text) is listed so the user can download it
    default_resume = 'JAHNAVI_PASUMARTHI_resume.txt'
    default_path = os.path.join(app.config['UPLOAD_FOLDER'], default_resume)
    if os.path.exists(default_path) and not any(f.get('filename') == default_resume for f in uploaded_files):
        uploaded_files.insert(0, {'filename': default_resume, 'original_name': default_resume, 'upload_time': 'Provided with site'})

    return render_template('resume.html', uploaded_files=uploaded_files, resume_data=RESUME_DATA)

@app.route('/download/<filename>')
def download(filename):
    """Download uploaded file"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found!', 'danger')
            return redirect(url_for('resume'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('resume'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback form with file upload"""
    if request.method == 'POST':
        feedback_text = request.form.get('feedback')
        rating = request.form.get('rating')
        
        if not feedback_text:
            flash('Please provide feedback!', 'danger')
            return redirect(url_for('feedback'))
        
        feedback_data = {
            'feedback': feedback_text,
            'rating': rating,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Handle optional file upload
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    feedback_data['attachment'] = filename
        
        # Store feedback
        feedbacks = session.get('feedbacks', [])
        feedbacks.append(feedback_data)
        session['feedbacks'] = feedbacks
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

# ==================== Error Handlers ====================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403

# ==================== Context Processors ====================

@app.context_processor
def inject_user():
    """Inject user data into all templates"""
    return {
        'current_user': session.get('user'),
        'is_logged_in': 'user' in session
    }

# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
