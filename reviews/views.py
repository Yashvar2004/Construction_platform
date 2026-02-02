from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.http import JsonResponse
from .models import Review
from .forms import ReviewForm, WorkerReviewForm, ThekedarReviewForm
from workers.models import WorkerProfile
from thekedars.models import ThekedarProfile


@login_required
def create_worker_review(request, worker_id):
    """Create review for a worker"""
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, 'Only workers can create reviews.')
        return redirect('dashboard:home')
    
    worker = get_object_or_404(WorkerProfile, id=worker_id)
    
    # Check if user has already reviewed this worker
    if Review.objects.filter(reviewer=request.user, worker=worker).exists():
        messages.error(request, 'You have already reviewed this worker.')
        return redirect('workers:profile')
    
    if request.method == 'POST':
        form = WorkerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.worker = worker
            review.save()
            
            messages.success(request, 'Your review has been submitted!')
            return redirect('workers:profile')
    else:
        form = WorkerReviewForm()
    
    return render(request, 'reviews/create_worker_review.html', {
        'form': form,
        'worker': worker
    })


@login_required
def create_thekedar_review(request, thekedar_id):
    """Create review for a thekedar"""
    try:
        profile = request.user.worker_profile
    except WorkerProfile.DoesNotExist:
        messages.error(request, 'Only workers can create reviews.')
        return redirect('dashboard:home')
    
    thekedar = get_object_or_404(ThekedarProfile, id=thekedar_id)
    
    # Check if user has already reviewed this thekedar
    if Review.objects.filter(reviewer=request.user, thekedar=thekedar).exists():
        messages.error(request, 'You have already reviewed this thekedar.')
        return redirect('thekedars:profile')
    
    if request.method == 'POST':
        form = ThekedarReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.thekedar = thekedar
            review.save()
            
            messages.success(request, 'Your review has been submitted!')
            return redirect('thekedars:profile')
    else:
        form = ThekedarReviewForm()
    
    return render(request, 'reviews/create_thekedar_review.html', {
        'form': form,
        'thekedar': thekedar
    })


@login_required
def my_reviews(request):
    """View reviews created by current user"""
    reviews = Review.objects.filter(reviewer=request.user).order_by('-created_at')
    
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})


@login_required
def worker_reviews(request, worker_id):
    """View all reviews for a specific worker"""
    worker = get_object_or_404(WorkerProfile, id=worker_id)
    reviews = Review.objects.filter(worker=worker).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'reviews/worker_reviews.html', {
        'worker': worker,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': reviews.count()
    })


@login_required
def thekedar_reviews(request, thekedar_id):
    """View all reviews for a specific thekedar"""
    thekedar = get_object_or_404(ThekedarProfile, id=thekedar_id)
    reviews = Review.objects.filter(thekedar=thekedar).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'reviews/thekedar_reviews.html', {
        'thekedar': thekedar,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': reviews.count()
    })


@login_required
def delete_review(request, review_id):
    """Delete a review (only by the reviewer)"""
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('reviews:my_reviews')
    
    return render(request, 'reviews/delete_review.html', {'review': review})


@login_required
def update_review(request, review_id):
    """Update a review (only by the reviewer)"""
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('reviews:my_reviews')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/update_review.html', {
        'form': form,
        'review': review
    })


def get_review_stats(request, target_type, target_id):
    """API endpoint to get review statistics"""
    if target_type == 'worker':
        reviews = Review.objects.filter(worker_id=target_id)
    elif target_type == 'thekedar':
        reviews = Review.objects.filter(thekedar_id=target_id)
    else:
        return JsonResponse({'error': 'Invalid target type'})
    
    stats = {
        'total_reviews': reviews.count(),
        'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
        'rating_distribution': {}
    }
    
    # Calculate rating distribution
    for i in range(1, 6):
        stats['rating_distribution'][str(i)] = reviews.filter(rating=i).count()
    
    return JsonResponse(stats)
