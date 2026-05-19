import os
import json
import PyPDF2
import random

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from dotenv import load_dotenv
from openai import OpenAI
import markdown
from django.core.files.storage import FileSystemStorage

from .forms import ContactForm
from .models import ResumeHistory

# =========================
# ENV + OPENAI
# =========================

load_dotenv()
NVIDIA_API_KEY=os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)


# =========================
# SKILLS + ROLES
# =========================

SKILLS = [
    "python", "java", "c++", "django", "html", "css", "javascript",
    "react", "node", "sql", "mysql", "mongodb", "machine learning",
    "data science", "aws", "git"
]

ROLES = {
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Backend Developer": ["python", "django", "sql", "node"],
    "Data Scientist": ["python", "machine learning", "data science"]
}


# =========================
# HOME
# =========================

def home(request):
    return render(request, 'index.html')


# =========================
# UPLOAD RESUME
# =========================

@login_required(login_url='login')
def upload(request):

    if request.method == "POST":

        file = request.FILES.get('resume')

        if file:

            # =========================
            # SAVE FILE
            # =========================

            file_path = os.path.join(settings.MEDIA_ROOT, file.name)

            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # =========================
            # EXTRACT PDF TEXT
            # =========================

            text = ""

            with open(file_path, 'rb') as f:

                reader = PyPDF2.PdfReader(f)

                for page in reader.pages:

                    extracted = page.extract_text()

                    if extracted:
                        text += extracted

            text_lower = text.lower()

            # =========================
            # SKILL DETECTION
            # =========================

            found_skills = []

            for skill in SKILLS:

                if skill.lower() in text_lower:
                    found_skills.append(skill)

            found_skills = sorted(set(found_skills))

            # =========================
            # ADVANCED ROLE DETECTION
            # =========================

            role_scores = {}

            for role, role_skills in ROLES.items():

                matched = 0

                for skill in role_skills:

                    if skill.lower() in text_lower:
                        matched += 1

                role_scores[role] = matched

            best_role = max(role_scores, key=role_scores.get)

            highest_role_score = role_scores[best_role]

            if highest_role_score <= 1:
                best_role = "General Software Developer"

            # =========================
            # ADVANCED ATS SCORE
            # =========================

            score = 0

            # -------------------------
            # TECHNICAL SKILLS
            # -------------------------

            skills_score = min(len(found_skills) * 3, 35)
            score += skills_score

            # -------------------------
            # PROJECTS
            # -------------------------

            project_keywords = [
                "project",
                "projects",
                "developed",
                "built",
                "application",
                "website",
                "system"
            ]

            project_score = 0

            for word in project_keywords:
                if word in text_lower:
                    project_score = 15
                    break

            score += project_score

            # -------------------------
            # EDUCATION
            # -------------------------

            education_keywords = [
                "bca",
                "btech",
                "mca",
                "degree",
                "university",
                "college"
            ]

            education_score = 0

            for word in education_keywords:
                if word in text_lower:
                    education_score = 10
                    break

            score += education_score

            # -------------------------
            # EXPERIENCE
            # -------------------------

            experience_keywords = [
                "internship",
                "experience",
                "worked",
                "developer",
                "freelance"
            ]

            experience_score = 0

            for word in experience_keywords:
                if word in text_lower:
                    experience_score = 15
                    break

            score += experience_score

            # -------------------------
            # CERTIFICATIONS
            # -------------------------

            certificate_keywords = [
                "certificate",
                "certification",
                "coursera",
                "udemy",
                "nptel"
            ]

            certification_score = 0

            for word in certificate_keywords:
                if word in text_lower:
                    certification_score = 10
                    break

            score += certification_score

            # -------------------------
            # CONTACT INFORMATION
            # -------------------------

            contact_score = 0

            if "@" in text:
                contact_score += 5

            if "+91" in text or "phone" in text_lower:
                contact_score += 5

            score += contact_score

            # -------------------------
            # LINKEDIN / GITHUB
            # -------------------------

            social_score = 0

            if "github" in text_lower:
                social_score += 5

            if "linkedin" in text_lower:
                social_score += 5

            score += social_score

            # -------------------------
            # LIMIT FINAL SCORE
            # -------------------------

            if score >= 95:
                score = random.randint(88, 94)

            score = min(score, 94)

            # =========================
            # PROFESSIONAL SUGGESTIONS
            # =========================

            suggestions = []

            if "react" not in found_skills:
                suggestions.append({
                    "title": "Frontend Improvement",
                    "text": "Add React.js projects to improve frontend development opportunities."
                })

            if "django" not in found_skills and "node.js" not in found_skills:
                suggestions.append({
                    "title": "Backend Development",
                    "text": "Include backend frameworks like Django or Node.js for better full-stack profile strength."
                })

            if "sql" not in found_skills:
                suggestions.append({
                    "title": "Database Skills",
                    "text": "Add SQL or database management skills to improve backend compatibility."
                })

            if "git" not in found_skills:
                suggestions.append({
                    "title": "Version Control",
                    "text": "Mention Git and GitHub to demonstrate collaborative development experience."
                })

            if "aws" not in found_skills:
                suggestions.append({
                    "title": "Cloud Computing",
                    "text": "Learning cloud technologies like AWS can significantly improve ATS ranking."
                })

            if "machine learning" not in found_skills:
                suggestions.append({
                    "title": "AI Enhancement",
                    "text": "Adding AI or Machine Learning projects can modernize your technical profile."
                })

            if "project" not in text_lower:
                suggestions.append({
                    "title": "Project Experience",
                    "text": "Add detailed project descriptions including technologies used and measurable outcomes."
                })

            if "internship" not in text_lower and "experience" not in text_lower:
                suggestions.append({
                    "title": "Industry Exposure",
                    "text": "Practical internship or freelance experience can improve recruiter confidence."
                })

            if len(found_skills) < 5:
                suggestions.append({
                    "title": "Skill Diversity",
                    "text": "Increase technical skill diversity to improve ATS matching performance."
                })

            if "linkedin" not in text_lower:
                suggestions.append({
                    "title": "Professional Branding",
                    "text": "Add your LinkedIn profile for improved professional credibility."
                })

            if not suggestions:
                suggestions.append({
                    "title": "Excellent Resume",
                    "text": "Excellent ATS-optimized resume with strong technical alignment."
                })

            # =========================
            # AI ANALYSIS
            # =========================

            try:

                response = client.chat.completions.create(

                    model="meta/llama-3.1-8b-instruct",

                    messages=[
                        {
                            "role": "user",

                            "content": f"""
You are an expert ATS Resume Analyzer,
Senior HR Recruiter,
and Career Consultant.

Analyze the following resume professionally.

Provide recruiter-level analysis.

Return the response in EXACTLY this format:

## Resume Summary
Write a strong professional summary.

## Strengths
- Mention strong technical areas
- Mention ATS-friendly sections
- Mention positive qualities

## Weaknesses
- Mention missing skills
- Mention weak sections
- Mention missing industry exposure

## ATS Improvements
- Suggest keyword improvements
- Suggest formatting improvements
- Suggest project improvements

## Missing Skills To Learn
- Suggest trending technologies
- Suggest role-specific skills
- Suggest industry tools

## Best Career Roles
- Suggest 3 to 5 realistic career roles

## Final Verdict
Write a professional HR-style verdict about the resume,
its hiring potential,
and overall market readiness.

Resume:
{text}
"""
                        }
                    ],

                    max_tokens=1000,
                    temperature=0.7

                )

                ai_output = response.choices[0].message.content

                formatted_ai_output = markdown.markdown(ai_output)

            except Exception as e:

                print("OPENAI ERROR:", e)

                formatted_ai_output = """
<h2>AI Analysis Not Available</h2>

<p>
Unable to generate AI insights at the moment.
Please try again later.
</p>
"""

            # =========================
            # SAVE RESUME HISTORY
            # =========================

            ResumeHistory.objects.create(
                user=request.user,
                filename=file.name,
                ats_score=score,
                predicted_role=best_role,
            )

            resume_url = settings.MEDIA_URL + file.name

            history = ResumeHistory.objects.filter(
            user=request.user
            ).order_by('-uploaded_at')

            # =========================
            # FINAL RENDER
            # =========================

            return render(request, 'dashboard.html', {

                'message': 'Resume analyzed successfully!',

                'resume_text': text[:500],

                'skills': found_skills,

                'score': score,

                'role': best_role,

                'suggestions': suggestions,

                'ai_output': formatted_ai_output,

                'resume_file': file.name,

                'resume_url': resume_url,

                'resume_history': history,

            })  

    return render(request, 'upload.html')


# =========================
# CONTACT
# =========================

def contact(request):

    if request.method == "POST":

        form_data = ContactForm(request.POST)

        if form_data.is_valid():
            form_data.save()

            messages.success(
                request,
                "Our Team will contact you!"
            )

            return redirect('/')

    else:
        form_data = ContactForm()

    context = {
        'contactform': form_data
    }

    return render(request, "contact.html", context)


# =========================
# PORTFOLIO
# =========================

def portfolio(request):
    return redirect(
        "https://amanshah-here.github.io/Portfolio/"
    )


# =========================
# LOGIN
# =========================

def login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            messages.success(
                request,
                "Login successful"
            )

            return redirect('home')

        else:

            messages.error(
                request,
                "Invalid credentials"
            )

            return redirect('login')

    return render(request, 'login.html')


# =========================
# REGISTER
# =========================

def register(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get(
            'confirm_password'
        )

        # password check
        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match"
            )

            return redirect('register')

        # username exists check
        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect('register')

        # email exists check
        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists"
            )

            return redirect('register')

        # create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully"
        )

        return redirect('login')

    return render(request, 'register.html')


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)
    
    return redirect('login')


# =========================
# DONATE
# =========================

# def donate(request):
#     return render(request, 'donate.html')

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .models import ResumeHistory


@staff_member_required
def admin_dashboard(request):

    users = User.objects.all().order_by('-date_joined')

    resumes = ResumeHistory.objects.all().order_by('-uploaded_at')

    total_users = users.count()

    total_uploads = resumes.count()

    average_score = 0

    if resumes.exists():

        average_score = int(
            sum(r.ats_score for r in resumes) / resumes.count()
        )

    top_scores = resumes.order_by('-ats_score')[:5]

    latest_uploads = resumes.order_by('-uploaded_at')[:5]

    context = {

        'users': users,

        'resumes': resumes,

        'total_users': total_users,

        'total_uploads': total_uploads,

        'average_score': average_score,

        'top_scores': top_scores,

        'latest_uploads': latest_uploads,

    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )
import razorpay

from django.conf import settings

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.views.decorators.csrf import csrf_exempt

from .models import Donation


# =========================
# DONATE VIEW
# =========================

def donate(request):

    if request.method == "POST":

        name = request.POST.get("name")

        amount = int(request.POST.get("amount")) * 100

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        payment = client.order.create({

            "amount": amount,

            "currency": "INR",

            "payment_capture": "1"

        })

        donation = Donation.objects.create(

            user=request.user
            if request.user.is_authenticated
            else None,

            name=name,

            amount=amount // 100,

            razorpay_order_id=payment["id"]

        )

        context = {

            "payment": payment,

            "donation": donation,

            "razorpay_key":
            settings.RAZORPAY_KEY_ID,

            "amount": amount,

            "name": name,

        }

        return render(
            request,
            "payment.html",
            context
        )

    return render(request, "donate.html")


# =========================
# PAYMENT SUCCESS
# =========================

@csrf_exempt
def payment_success(request):

    if request.method == "POST":

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        razorpay_payment_id = request.POST.get(
            "razorpay_payment_id"
        )

        razorpay_order_id = request.POST.get(
            "razorpay_order_id"
        )

        razorpay_signature = request.POST.get(
            "razorpay_signature"
        )

        params_dict = {

            'razorpay_order_id':
            razorpay_order_id,

            'razorpay_payment_id':
            razorpay_payment_id,

            'razorpay_signature':
            razorpay_signature

        }

        try:

            client.utility.verify_payment_signature(
                params_dict
            )

            donation = get_object_or_404(

                Donation,

                razorpay_order_id=
                razorpay_order_id

            )

            donation.razorpay_payment_id = (
                razorpay_payment_id
            )

            donation.paid = True

            donation.save()

            return render(
                request,
                "success.html"
            )

        except:

            return render(
                request,
                "failed.html"
            )

    return redirect("donate")