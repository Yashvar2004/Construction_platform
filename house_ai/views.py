from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import os
from .models import HouseRequirement, MediaUpload, AIResponse
from .forms import HouseRequirementForm, MultipleMediaUploadForm


def get_groq_client():
    """Initialize and return a Groq client."""
    try:
        from groq import Groq
        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            api_key = getattr(settings, 'GROQ_API_KEY', '')
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except Exception:
        return None


CONSTRUCTION_SYSTEM_PROMPT = """You are an expert AI Construction Assistant for a platform that connects construction workers (workers) with contractors (thekedars) in India. Your role is to provide helpful, accurate, and practical advice about house construction in India.

Key areas of expertise:
- Construction costs in India (in INR ₹)
- Building materials and their costs
- Construction timelines and planning
- Foundation types and soil considerations
- RCC structure and brick wall construction
- Electrical and plumbing systems
- Interior finishing (tiles, paint, fixtures)
- Vastu Shastra considerations
- Building permits and regulations in India
- Finding and managing contractors (thekedars)
- Worker management and labor costs
- Quality standards and inspection tips

Guidelines:
- Always respond in a helpful, professional tone
- Provide specific cost estimates in INR when possible
- Mention regional variations when relevant
- Keep responses concise but informative (under 300 words)
- Use simple language accessible to homeowners
- Include practical tips and actionable advice
- When discussing costs, mention they are approximate and may vary by location
- Format responses with clear structure using bullet points when helpful"""


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

            # Generate AI response
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
    """Generate AI response using Groq API based on house requirements."""
    client = get_groq_client()

    if client is None:
        # Fallback to template-based response if Groq is not configured
        response_text = f"""🏠 AI Analysis for House Construction

Based on your requirements:
- Plot Size: {requirement.plot_size}
- Budget: ₹{requirement.budget:,.0f}
- Floors: {requirement.floors}
- City: {requirement.city}

📋 Estimated Construction Details:
- Foundation: Standard concrete foundation suitable for {requirement.city}
- Structure: RCC frame with brick walls
- Roof: Concrete slab with waterproofing
- Flooring: Vitrified tiles for living areas, marble for bedrooms
- Electrical: Concealed wiring with safety features
- Plumbing: CPVC pipes with modern fixtures

💰 Estimated Cost Breakdown:
- Foundation: ₹{requirement.budget * 0.15:,.0f} (15%)
- Structure: ₹{requirement.budget * 0.35:,.0f} (35%)
- Finishing: ₹{requirement.budget * 0.30:,.0f} (30%)
- Electrical & Plumbing: ₹{requirement.budget * 0.10:,.0f} (10%)
- Miscellaneous: ₹{requirement.budget * 0.10:,.0f} (10%)

⏱️ Recommended Timeline: {requirement.floors * 6} months

💡 Tip: Set GROQ_API_KEY environment variable for AI-powered detailed analysis."""

        AIResponse.objects.create(
            requirement=requirement,
            design_suggestion=response_text,
            cost_insight=f"Based on ₹{requirement.budget:,.0f} budget for {requirement.plot_size} plot with {requirement.floors} floors in {requirement.city}"
        )
        return

    try:
        user_prompt = f"""Analyze and provide a detailed construction plan for a house with these requirements:

- Plot Size: {requirement.plot_size}
- Budget: ₹{requirement.budget:,.0f}
- Number of Floors: {requirement.floors}
- City/Location: {requirement.city}

Please provide:
1. A detailed design suggestion covering structure, materials, and layout recommendations
2. A cost breakdown with approximate percentages and amounts for each phase
3. Timeline estimation for each construction phase
4. Material recommendations suitable for the {requirement.city} region
5. Any important tips or considerations for this specific budget and location

Keep the response practical and focused on Indian construction practices and costs."""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": CONSTRUCTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1500,
        )

        design_suggestion = chat_completion.choices[0].message.content

        # Generate cost insight separately
        cost_prompt = f"""Provide a concise cost insight summary for:
- Budget: ₹{requirement.budget:,.0f}
- Plot: {requirement.plot_size}, {requirement.floors} floors in {requirement.city}

Give a 2-3 sentence summary of budget allocation and key cost factors. Be specific with numbers."""

        cost_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": CONSTRUCTION_SYSTEM_PROMPT},
                {"role": "user", "content": cost_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300,
        )

        cost_insight = cost_completion.choices[0].message.content

        AIResponse.objects.create(
            requirement=requirement,
            design_suggestion=design_suggestion,
            cost_insight=cost_insight
        )

    except Exception as e:
        # Fallback on API error
        response_text = f"""🏠 AI Analysis for House Construction

Based on your requirements:
- Plot Size: {requirement.plot_size}
- Budget: ₹{requirement.budget:,.0f}
- Floors: {requirement.floors}
- City: {requirement.city}

📋 Estimated Construction Details:
- Foundation: Standard concrete foundation
- Structure: RCC frame with brick walls
- Roof: Concrete slab with waterproofing
- Flooring: Vitrified tiles for living areas
- Electrical: Concealed wiring with safety features
- Plumbing: CPVC pipes with modern fixtures

💰 Estimated Cost Breakdown:
- Foundation: ₹{requirement.budget * 0.15:,.0f} (15%)
- Structure: ₹{requirement.budget * 0.35:,.0f} (35%)
- Finishing: ₹{requirement.budget * 0.30:,.0f} (30%)
- Electrical & Plumbing: ₹{requirement.budget * 0.10:,.0f} (10%)
- Miscellaneous: ₹{requirement.budget * 0.10:,.0f} (10%)

⏱️ Recommended Timeline: {requirement.floors * 6} months

⚠️ Note: AI service encountered an error. Showing template response."""

        AIResponse.objects.create(
            requirement=requirement,
            design_suggestion=response_text,
            cost_insight=f"Based on ₹{requirement.budget:,.0f} budget for {requirement.plot_size} plot with {requirement.floors} floors in {requirement.city}"
        )


@login_required
def ai_chat(request):
    """AI chat interface for construction queries using Groq API."""
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

        client = get_groq_client()

        if client is None:
            # Fallback response when Groq is not configured
            ai_response = f"""I received your question: "{user_message}"

⚠️ The AI assistant needs a Groq API key to provide intelligent responses. Please ask the administrator to set the GROQ_API_KEY environment variable.

In the meantime, here are some general tips:
- For cost queries: Construction costs in India typically range ₹1,500-3,500 per sq ft
- For timeline: A standard 2-floor house takes 8-14 months
- For materials: Use branded cement (ACC, UltraTech) and TMT steel bars

You can also submit your house requirements for a detailed analysis."""

            return JsonResponse({
                'user_message': user_message,
                'ai_response': ai_response
            })

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": CONSTRUCTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=800,
            )

            ai_response = chat_completion.choices[0].message.content

            return JsonResponse({
                'user_message': user_message,
                'ai_response': ai_response
            })

        except Exception as e:
            return JsonResponse({
                'user_message': user_message,
                'ai_response': f"I'm sorry, I encountered an error processing your request. Please try again. Error: {str(e)}"
            })

    return render(request, 'house_ai/ai_chat.html')
