from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm,LoginForm
from django.contrib import messages
import random


# Sign Up View
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # This saves the user and creates the account
            login(request, user)  # Automatically log in the user after successful signup
            return redirect('login')  # Redirect to the home page (or any other page you prefer)
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('daily_game')  # If user is already logged in, redirect to home page.

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                print(user)
                return redirect('daily_game')  # Redirect to home or dashboard after login
            
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('daily_game')



def daily_game(request):
    date_today = timezone.now().date()
    game = DailyGame.objects.filter(date=date_today).first()
    if not game:
        return render(request, 'game_not_available.html')
    user = request.user
    user_history = None
    if user.is_authenticated:
        user_history, created = UserGameHistory.objects.get_or_create(
            user=request.user, game=game
        )
    images = game.episode.images.order_by('order')[:6]
    context = {
        'game': game,
        'images': images,
        'user_history': user_history,
        'title': game.episode.show.title,
        'date_today': date_today,
    }
    return render(request, 'daily_game.html', context)

def past_game(request, game_id):
    # Fetch the game data
    date_today = timezone.now().date()
    today_game = DailyGame.objects.filter(date=date_today).first()
    game = get_object_or_404(DailyGame, id=game_id)
    next_game_exists = today_game.id - 1 if today_game else None
    # Logic to calculate previous and next game IDs
    previous_id = game.id - 1 if game.id > 1 else None
    next_id = game.id + 1 if next_game_exists and game.id < next_game_exists else None
    today_id = game.id -1
    # Fetch the related images
    images = game.episode.images.order_by('order')[:6]
    # Pass the context
    context = {
        'game': game,
        'images': images,
        'title': game.episode.show.title,
        'next_game_exists': next_game_exists,
        'today_id': today_id,
        'previous_id': previous_id,
        'next_id': next_id,
    }

    return render(request, 'past_game.html', context)
    


def submit_guess(request, game_id):
    if request.method == 'POST':
        date_today = timezone.now().date()
        today_game = DailyGame.objects.filter(date=date_today).first()
        if request.user.is_authenticated and today_game.id == game_id:
            
            # Fetch the user's game history
            user_history = get_object_or_404(UserGameHistory, user=request.user, game_id=game_id)
            
            # If the game is completed, return an error
            if user_history.completed:
                return JsonResponse({'error': 'Game already completed'}, status=400)

            # Get the user's guess from the request
            guess = request.POST.get('guess')
            correct_title = user_history.game.episode.show.title  # Correct TV show title
            # Increment the number of guesses
            user_history.guesses += 1
            # Check if the user's guess is correct
            if guess.lower() == correct_title.lower():
                user_history.correct_guess = True
                user_history.completed = True
                # Update user statistics
                stats, _ = UserStatistics.objects.get_or_create(user=request.user)
                stats.total_games_played += 1
                stats.total_correct_guesses += 1
                stats.win_streak += 1
                stats.highest_win_streak = max(stats.win_streak, stats.highest_win_streak)
                stats.save()
                response = {'result': 'correct', 'message': 'Correct!'}
            else:
                response = {'result': 'incorrect', 'message': 'Incorrect. Try again!'}

            # If the user has used all 6 guesses and hasn't guessed correctly
            if user_history.guesses >= 6 and not user_history.correct_guess:
                user_history.completed = True
                response = {'result': 'failed', 'message': correct_title}
                stats, _ = UserStatistics.objects.get_or_create(user=request.user)
                stats.total_games_played += 1
                stats.win_streak = 0
                stats.save()

            # Save the user's game history
            user_history.save()
            
            
            # Prepare the response
            response['guess'] = guess
            response['current_attempt'] = user_history.guesses  # Show current attempt
            response['remaining_attempts'] = 6 - user_history.guesses  # Show remaining attempts
            response['image_to_show'] = user_history.guesses  # Show the next image to the user (1-based index)
            print(response)

            return JsonResponse(response)
        else:
            # Logic for guests (not logged in)
            guess = request.POST.get('guess')
            correct_title = DailyGame.objects.get(id=game_id).episode.show.title
            if guess.lower() == correct_title.lower():
                response = {'result': 'correct', 'message': correct_title}
            else:
                response = {'result': 'incorrect', 'message': 'Incorrect. Try again!'}

            # Guests' attempt data could be stored in session or cookies
            guesses = request.session.get('guest_guesses', 0) + 1
            print(guesses)
            request.session['guest_guesses'] = guesses
            request.session['remaining_attempts'] = 6 - guesses

            if guesses == 6:
                response = {'result': 'failed', 'message': correct_title}

            response['guess'] = guess
            response['current_attempt'] = guesses
            response['remaining_attempts'] = 6 - guesses 
            response['image_to_show'] = guesses 
            
            print(response)
        return JsonResponse(response)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def submit_guesspast(request, game_id):
    if request.method == 'POST':
        # Logic for guests (not logged in)
        guess = request.POST.get('guess')
        print(guess)
        correct_title = DailyGame.objects.get(id=game_id).episode.show.title
        print(correct_title)
        if guess.lower() == correct_title.lower():
            print('right')
            response = {'result': 'correct', 'message': correct_title}
        else:
            response = {'result': 'incorrect', 'message': 'Incorrect. Try again!'}

        # Guests' attempt data could be stored in session or cookies
        guesses = request.session.get('guest_guesses', 0) + 1
        request.session['guest_guesses'] = guesses
        request.session['remaining_attempts'] = 6 - guesses

        if guesses == 6:
            response = {'result': 'failed', 'message': correct_title}

        response['guess'] = guess
        response['current_attempt'] = guesses
        response['remaining_attempts'] = 6 - guesses 
        response['image_to_show'] = guesses 
    return JsonResponse(response)
    

    

@login_required
def user_statistics(request):
    stats, created = UserStatistics.objects.get_or_create(user=request.user)
    return render(request, 'user_statistics.html', {'stats': stats})






def calendar_view(request):
    # Fetch past games, excluding today's date, ordered by id descending
    past_games = DailyGame.objects.filter(date__lt=timezone.now().date()).order_by('-id')
    if past_games.exists():
        # Select a random game
        random_game = random.choice(past_games).id
        print(random_game)
    context={
        'past_games': past_games,
        'random_game': random_game
    }
    return render(request,'calendar.html',context)
