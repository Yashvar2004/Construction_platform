from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import User


@login_required
def home(request):
    user = request.user
    
    # Role-based dashboard data
    context = {
        'user': user,
        'role': user.role,
    }
    
    if user.role == 'worker':
        # Worker dashboard data
        try:
            worker_profile = user.worker_profile
            context.update({
                'worker_profile': worker_profile,
                'recent_applications': worker_profile.job_applications.all()[:5],
                'skills': worker_profile.skills.all(),
            })
        except:
            context['profile_incomplete'] = True
    
    elif user.role == 'thekedar':
        # Thekedar dashboard data
        try:
            thekedar_profile = user.thekedar_profile
            context.update({
                'thekedar_profile': thekedar_profile,
                'recent_projects': thekedar_profile.projects.all()[:5],
                'job_posts': thekedar_profile.job_posts.all()[:5],
            })
        except:
            context['profile_incomplete'] = True
    
    elif user.role == 'user':
        # Normal user dashboard data
        context.update({
            'house_requirements': user.house_requirements.all()[:5],
        })
    
    return render(request, f'dashboard/{user.role}_dashboard.html', context)
