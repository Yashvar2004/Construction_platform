from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import os
import logging
import traceback
from .models import HouseRequirement, MediaUpload, AIResponse
from .forms import HouseRequirementForm, MultipleMediaUploadForm

logger = logging.getLogger(__name__)


def get_groq_client():
    """Initialize and return a Groq client."""
    try:
        from groq import Groq
        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            api_key = getattr(settings, 'GROQ_API_KEY', '')
        if not api_key:
            logger.warning("GROQ_API_KEY is not set")
            return None
        return Groq(api_key=api_key)
    except ImportError:
        logger.error("groq package is not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
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


def call_groq_api(messages, max_tokens=800):
    """Call Groq API with error handling. Returns (response_text, error_message)."""
    client = get_groq_client()

    if client is None:
        return None, "AI service is not configured. Please set the GROQ_API_KEY environment variable."

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        error_detail = str(e)
        logger.error(f"Groq API error: {error_detail}\n{traceback.format_exc()}")
        return None, f"AI service error: {error_detail}"


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

    messages_list = [
        {"role": "system", "content": CONSTRUCTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    design_suggestion, error = call_groq_api(messages_list, max_tokens=1500)

    if design_suggestion is None:
        # AI call failed - use template fallback with error note
        design_suggestion = f"""🏠 AI Analysis for House Construction

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

⚠️ Note: {error}"""
        cost_insight = f"Based on ₹{requirement.budget:,.0f} budget for {requirement.plot_size} plot with {requirement.floors} floors in {requirement.city}"
    else:
        # Generate cost insight separately
        cost_prompt = f"""Provide a concise cost insight summary for:
- Budget: ₹{requirement.budget:,.0f}
- Plot: {requirement.plot_size}, {requirement.floors} floors in {requirement.city}

Give a 2-3 sentence summary of budget allocation and key cost factors. Be specific with numbers."""

        cost_messages = [
            {"role": "system", "content": CONSTRUCTION_SYSTEM_PROMPT},
            {"role": "user", "content": cost_prompt}
        ]

        cost_insight, cost_error = call_groq_api(cost_messages, max_tokens=300)
        if cost_insight is None:
            cost_insight = f"Based on ₹{requirement.budget:,.0f} budget for {requirement.plot_size} plot with {requirement.floors} floors in {requirement.city}"

    AIResponse.objects.create(
        requirement=requirement,
        design_suggestion=design_suggestion,
        cost_insight=cost_insight
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

        messages_list = [
            {"role": "system", "content": CONSTRUCTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        ai_response, error = call_groq_api(messages_list, max_tokens=800)

        if ai_response is None:
            ai_response = f"⚠️ {error}\n\nPlease check that the GROQ_API_KEY is configured in your Vercel project settings."

        return JsonResponse({
            'user_message': user_message,
            'ai_response': ai_response
        })

    return render(request, 'house_ai/ai_chat.html')


DESIGN_SYSTEM_PROMPT = """You are an expert Indian house architect and interior designer. Generate a detailed, personalized house design plan based on the user's requirements.

You MUST respond in valid JSON format with exactly this structure:
{
    "architectural_style": "Style name and why it suits these requirements",
    "style_description": "2-3 sentences describing the overall aesthetic",
    "exterior": {
        "design": "Detailed exterior design description (facade, materials, colors)",
        "features": ["feature1", "feature2", "feature3", "feature4"]
    },
    "room_layout": {
        "ground_floor": {
            "rooms": ["Room1: description", "Room2: description", ...],
            "highlight": "One key design highlight"
        },
        "first_floor": {
            "rooms": ["Room1: description", "Room2: description", ...],
            "highlight": "One key design highlight"
        }
    },
    "interiors": {
        "living_room": "Design description with colors, furniture style, lighting",
        "kitchen": "Kitchen layout, countertop material, cabinet style",
        "bedrooms": "Bedroom design approach, storage solutions",
        "bathrooms": "Bathroom fixtures, tiles, modern features"
    },
    "color_palette": {
        "primary": "Color name and hex code",
        "secondary": "Color name and hex code",
        "accent": "Color name and hex code",
        "description": "Why this palette works for this home"
    },
    "materials": {
        "flooring": "Recommended flooring types per area",
        "walls": "Wall treatments and paint",
        "roof": "Roofing material and style",
        "windows": "Window type and style"
    },
    "vastu_tips": ["tip1", "tip2", "tip3"],
    "smart_features": ["feature1", "feature2", "feature3"],
    "estimated_timeline": "Construction timeline breakdown by phase",
    "pro_tips": ["tip1", "tip2", "tip3"]
}

Be specific to Indian construction practices, local materials, and climate considerations for the given city. All cost references should be in INR (₹). Keep descriptions vivid and practical."""


@login_required
def explore_designs(request, requirement_id):
    """Generate and display personalized house design inspiration."""
    if request.user.role != 'user':
        messages.error(request, 'Access denied. Normal user role required.')
        return redirect('dashboard:home')

    requirement = get_object_or_404(HouseRequirement, id=requirement_id, user=request.user)

    # Curated design images by category (Unsplash)
    design_images = {
        'modern_exterior': [
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=600&h=400&fit=crop',
        ],
        'traditional_indian': [
            'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=600&h=400&fit=crop',
        ],
        'living_room': [
            'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=600&h=400&fit=crop',
        ],
        'kitchen': [
            'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600585153490-76fb20a32601?w=600&h=400&fit=crop',
        ],
        'bedroom': [
            'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?w=600&h=400&fit=crop',
        ],
        'bathroom': [
            'https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=600&h=400&fit=crop',
            'https://images.unsplash.com/photo-1600573472591-ee6b68d14c68?w=600&h=400&fit=crop',
        ],
    }

    # Generate AI design plan
    design_json = None
    error = None

    user_prompt = f"""Generate a personalized house design plan for:

- Plot Size: {requirement.plot_size}
- Budget: ₹{requirement.budget:,.0f}
- Floors: {requirement.floors}
- City: {requirement.city}

Consider the local climate, available materials, and Indian construction practices for {requirement.city}. Provide room layouts appropriate for a {requirement.plot_size} plot with {requirement.floors} floor(s) within a ₹{requirement.budget:,.0f} budget. Include Vastu Shastra recommendations."""

    messages_list = [
        {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    response_text, error = call_groq_api(messages_list, max_tokens=2000)

    if response_text:
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                import json
                design_json = json.loads(json_match.group())
            else:
                error = "AI returned invalid format"
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            error = "AI returned invalid JSON"

    # Build context for template
    context = {
        'requirement': requirement,
        'design_images': design_images,
        'design_json': design_json,
        'error': error,
    }

    return render(request, 'house_ai/explore_designs.html', context)
