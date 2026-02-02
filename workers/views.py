from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import WorkerProfile, Skill, WorkerSkillMap
from .forms import WorkerProfileForm, SkillForm, WorkerSkillForm
from jobs.models import JobPost, JobApplication


@login_required
def worker_profile(request):
    if request.user.role != 'worker':
        messages.error(request, 'Access denied. Worker role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = WorkerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            worker_profile = form.save(commit=False)
            worker_profile.user = request.user
            worker_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('workers:profile')
    else:
        form = WorkerProfileForm(instance=profile)
    
    return render(request, 'workers/profile.html', {'form': form, 'profile': profile})


@login_required
def manage_skills(request):
    if request.user.role != 'worker':
        messages.error(request, 'Access denied. Worker role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('workers:profile')
    
    if request.method == 'POST':
        # Handle manual checkbox data
        selected_skills_ids = request.POST.getlist('skills')
        
        # Clear existing skills
        WorkerSkillMap.objects.filter(worker=profile).delete()
        
        # Add new skills
        for skill_id in selected_skills_ids:
            try:
                skill = Skill.objects.get(id=skill_id)
                WorkerSkillMap.objects.create(worker=profile, skill=skill)
            except Skill.DoesNotExist:
                continue
        
        messages.success(request, 'Skills updated successfully!')
        return redirect('workers:manage_skills')
    else:
        current_skills = profile.skills.all() if profile else []
        form = WorkerSkillForm(initial={'skills': current_skills})
    
    return render(request, 'workers/manage_skills.html', {
        'form': form,
        'profile': profile,
        'all_skills': Skill.objects.all()
    })


@login_required
def browse_jobs(request):
    if request.user.role != 'worker':
        messages.error(request, 'Access denied. Worker role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('workers:profile')
    
    jobs = JobPost.objects.filter(status='open').order_by('-created_at')
    
    # Filter by worker's skills
    worker_skills = profile.skills.all()
    if worker_skills:
        jobs = jobs.filter(required_skill__in=worker_skills)
    
    return render(request, 'workers/browse_jobs.html', {
        'jobs': jobs,
        'worker_skills': worker_skills
    })


@login_required
def apply_job(request, job_id):
    if request.user.role != 'worker':
        messages.error(request, 'Access denied. Worker role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('workers:profile')
    
    job = get_object_or_404(JobPost, id=job_id)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, worker=profile).exists():
        messages.error(request, 'You have already applied for this job.')
        return redirect('workers:browse_jobs')
    
    # Check if worker has the required skill
    if job.required_skill not in profile.skills.all():
        messages.error(request, 'You do not have the required skill for this job.')
        return redirect('workers:browse_jobs')
    
    if request.method == 'POST':
        JobApplication.objects.create(
            job=job,
            worker=profile,
            status='pending'
        )
        messages.success(request, 'Job application submitted successfully!')
        return redirect('workers:my_applications')
    
    return render(request, 'workers/apply_job.html', {'job': job})


@login_required
def my_applications(request):
    if request.user.role != 'worker':
        messages.error(request, 'Access denied. Worker role required.')
        return redirect('dashboard:home')
    
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('workers:profile')
    
    applications = JobApplication.objects.filter(worker=profile).order_by('-applied_date')
    
    return render(request, 'workers/my_applications.html', {'applications': applications})
