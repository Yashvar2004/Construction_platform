from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from .models import HouseRequirement, MediaUpload, AIResponse
from .forms import HouseRequirementForm, MultipleMediaUploadForm


@login_required
def submit_requirement(request):
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = HouseRequirementForm(request.POST)
        if form.is_valid():
            requirement = form.save(commit=False)
            requirement.user = request.user
            requirement.save()
            
            # Generate AI response (placeholder)
            generate_ai_response(requirement)
            
            messages.success(request, 'House requirement submitted successfully!')
            return redirect('house_ai:my_requirements')
    else:
        form = HouseRequirementForm()
    
    return render(request, 'house_ai/submit_requirement.html', {'form': form})


@login_required
def upload_media(request, requirement_id):
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    requirement = get_object_or_404(HouseRequirement, id=requirement_id, user=request.user)
    
    if request.method == 'POST':
        form = MultipleMediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            
            for file in files:
                # Determine file type
                media_type = 'image'
                if file.content_type.startswith('video/'):
                    media_type = 'video'
                
                # Save file
                MediaUpload.objects.create(
                    requirement=requirement,
                    media_type=media_type,
                    file_path=file
                )
            
            messages.success(request, f'{len(files)} files uploaded successfully!')
            return redirect('house_ai:view_requirement', requirement_id=requirement.id)
    else:
        form = MultipleMediaUploadForm()
    
    return render(request, 'house_ai/upload_media.html', {
        'form': form,
        'requirement': requirement
    })


@login_required
def my_requirements(request):
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    requirements = HouseRequirement.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'house_ai/my_requirements.html', {'requirements': requirements})


@login_required
def view_requirement(request, requirement_id):
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    requirement = get_object_or_404(HouseRequirement, id=requirement_id, user=request.user)
    media_files = MediaUpload.objects.filter(requirement=requirement)
    ai_response = AIResponse.objects.filter(requirement=requirement).first()
    
    return render(request, 'house_ai/view_requirement.html', {
        'requirement': requirement,
        'media_files': media_files,
        'ai_response': ai_response
    })


@login_required
def delete_media(request, media_id):
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    media = get_object_or_404(MediaUpload, id=media_id, requirement__user=request.user)
    requirement_id = media.requirement.id
    
    # Delete file from storage
    if media.file_path and default_storage.exists(media.file_path.name):
        default_storage.delete(media.file_path.name)
    
    media.delete()
    messages.success(request, 'Media file deleted successfully!')
    
    return redirect('house_ai:view_requirement', requirement_id=requirement_id)


@login_required
def regenerate_ai_response(request, requirement_id):
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    requirement = get_object_or_404(HouseRequirement, id=requirement_id, user=request.user)
    
    # Delete existing AI response
    AIResponse.objects.filter(requirement=requirement).delete()
    
    # Generate new AI response
    generate_ai_response(requirement)
    
    messages.success(request, 'AI response regenerated successfully!')
    return redirect('house_ai:view_requirement', requirement_id=requirement.id)


def generate_ai_response(requirement):
    """Placeholder AI response generation"""
    # This is a placeholder - in real implementation, you would:
    # 1. Process uploaded media files
    # 2. Use AI/ML models to analyze requirements
    # 3. Generate detailed construction plan
    
    response_text = f"""
    AI Analysis for House Construction
    
    Based on your requirements:
    - Plot Size: {requirement.plot_size}
    - Budget: ₹{requirement.budget}
    - Floors: {requirement.floors}
    - City: {requirement.city}
    
    Estimated Construction Details:
    - Foundation: Standard concrete foundation
    - Structure: RCC frame with brick walls
    - Roof: Concrete slab with waterproofing
    - Flooring: Vitrified tiles for living areas, marble for bedrooms
    - Electrical: Concealed wiring with safety features
    - Plumbing: CPVC pipes with modern fixtures
    
    Estimated Cost Breakdown:
    - Foundation: 15% of total budget
    - Structure: 35% of total budget
    - Finishing: 30% of total budget
    - Electrical & Plumbing: 10% of total budget
    - Miscellaneous: 10% of total budget
    
    Recommended Timeline: {requirement.floors * 6} months
    """
    
    AIResponse.objects.create(
        requirement=requirement,
        design_suggestion=response_text,
        cost_insight=f"Based on ₹{requirement.budget} budget for {requirement.plot_size} plot with {requirement.floors} floors in {requirement.city}"
    )


@login_required
def ai_chat(request):
    """AI chat interface for construction queries"""
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        
        # Placeholder AI response
        ai_response = f"""
        Based on your query: "{user_message}"
        
        This is a placeholder AI response. In a real implementation, this would:
        1. Process your natural language query
        2. Access construction knowledge base
        3. Provide detailed, contextual answers
        4. Suggest relevant professionals or materials
        
        For now, please consult with a professional thekedar for detailed advice.
        """
        
        return JsonResponse({
            'user_message': user_message,
            'ai_response': ai_response
        })
    
    return render(request, 'house_ai/ai_chat.html')
