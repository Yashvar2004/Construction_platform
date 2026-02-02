from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import ThekedarProfile, Project
from .forms import ThekedarProfileForm, ProjectForm
from workers.models import Skill
from jobs.models import JobPost, JobApplication


@login_required
def thekedar_profile(request):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = ThekedarProfileForm(request.POST, instance=profile)
        if form.is_valid():
            thekedar_profile = form.save(commit=False)
            thekedar_profile.user = request.user
            thekedar_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('thekedars:profile')
    else:
        form = ThekedarProfileForm(instance=profile)
    
    return render(request, 'thekedars/profile.html', {'form': form, 'profile': profile})


@login_required
def create_project(request):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.thekedar = profile
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('thekedars:projects')
    else:
        form = ProjectForm()
    
    return render(request, 'thekedars/create_project.html', {'form': form})


@login_required
def projects_list(request):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    projects = Project.objects.filter(thekedar=profile).order_by('-created_at')
    
    return render(request, 'thekedars/projects.html', {'projects': projects})


@login_required
def edit_project(request, project_id):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    project = get_object_or_404(Project, id=project_id, thekedar=profile)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('thekedars:projects')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'thekedars/edit_project.html', {'form': form, 'project': project})


@login_required
def create_job_post(request):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    if request.method == 'POST':
        required_skill_id = request.POST.get('required_skill')
        duration_days = request.POST.get('duration_days')
        wage_offer = request.POST.get('wage_offer')
        
        if required_skill_id and duration_days and wage_offer:
            try:
                skill = Skill.objects.get(id=required_skill_id)
                JobPost.objects.create(
                    thekedar=profile,
                    required_skill=skill,
                    duration_days=int(duration_days),
                    wage_offer=float(wage_offer)
                )
                messages.success(request, 'Job posted successfully!')
                return redirect('thekedars:job_posts')
            except Skill.DoesNotExist:
                messages.error(request, 'Invalid skill selected.')
        else:
            messages.error(request, 'Please fill all fields.')
    
    skills = Skill.objects.all()
    return render(request, 'thekedars/create_job_post.html', {'skills': skills})


@login_required
def job_posts_list(request):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    job_posts = JobPost.objects.filter(thekedar=profile).order_by('-created_at')
    
    return render(request, 'thekedars/job_posts.html', {'job_posts': job_posts})


@login_required
def job_applications(request, job_id):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    job = get_object_or_404(JobPost, id=job_id, thekedar=profile)
    applications = JobApplication.objects.filter(job=job).order_by('-applied_date')
    
    return render(request, 'thekedars/job_applications.html', {'job': job, 'applications': applications})


@login_required
def update_application_status(request, application_id, action):
    if request.user.role != 'thekedar':
        messages.error(request, 'Access denied. Thekedar role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.thekedar_profile
    except ThekedarProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('thekedars:profile')
    
    application = get_object_or_404(JobApplication, id=application_id, job__thekedar=profile)
    
    if action == 'accept':
        application.status = 'accepted'
        messages.success(request, 'Application accepted!')
    elif action == 'reject':
        application.status = 'rejected'
        messages.success(request, 'Application rejected!')
    
    application.save()
    return redirect('thekedars:job_applications', job_id=application.job.id)
