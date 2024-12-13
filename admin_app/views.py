from django.shortcuts import render,redirect, get_object_or_404
from game.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from game.models import *
# from .forms import *
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required,user_passes_test
# from django.http import JsonResponse,HttpResponseBadRequest
# from datetime import datetime,timedelta




# Create your views here.
def admin_login(request):
    try:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admindashboard')
        
        # messages.info(request,'Account not found')
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_obj = User.objects.filter(email = email)
            if not user_obj.exists ():
                messages.info(request,'Account not found')
                return render (request,'admin_login.html')
            
            user_obj = authenticate(request,email = email,password = password)
            if user_obj and user_obj.is_superuser or user_obj.is_staff:
                login(request, user_obj)
                return redirect('admindashboard')
            
            messages.info(request,'Invailed password')
            return render (request,'admin_login.html')
        
        return render (request,'admin_login.html')
    except Exception as e:
        print(e)

def admin_logout(request):
    logout(request)
    # Redirect to admin login page after logout
    return redirect('admin_login')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admindashboard_page(request):
    # user_count = User.objects.count()
    # latest_users = User.objects.filter(is_superuser=False).order_by('-date_joined')[:5] 
    
    return render(request, 'admindashboard.html')      

# @user_passes_test(lambda u: u.is_staff or u.is_superuser)
# def admin_profile(request):
#     user = request.user

#     if request.method == 'POST':
#         form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your Profile updated successfully.') 
#             return redirect('admin_profile')  # Redirect to the profile page after successful update
#         # else:
#         #     form = UserProfileUpdateForm(instance=user)
#     else:
#         form = UserProfileUpdateForm(instance=user)

#     context = {
#         'form':form
#     }   
#     return render(request, 'admin_profile.html', context)

# @user_passes_test(lambda u: u.is_staff or u.is_superuser)
# def show_user(request):
   
#         # users_list = User.objects.all()
#         users_list = User.objects.filter(is_superuser=False)
#         paginator = Paginator(users_list, 10)  # Change 10 to the number of items per page you want

#         page = request.GET.get('page')
#         try:
#             users = paginator.page(page)

#         except PageNotAnInteger:
#             # If page is not an integer, deliver the first page.
#             users = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             users = paginator.page(paginator.num_pages)
#         context = {
#             'users':users,
#         }
#         return render(request, 'user/show_user.html', context)
    
# @user_passes_test(lambda u: u.is_staff or u.is_superuser)
# def add_user(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'User added successfully.') 
#             return redirect('show_user')  # Redirect to the user list page after successful user addition
#     else:
#         form = SignUpForm()
#     return render(request, 'user/add_user.html', {'form': form})

# @user_passes_test(lambda u: u.is_staff or u.is_superuser)
# def edit_user(request, user_id):
#     user = User.objects.get(pk=user_id)
#     if request.method == 'POST':
#         form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'User updated successfully.') 
#             return redirect('edit_user', user_id)  # Redirect to the profile page after successful update
#     else:
#         form = UserProfileUpdateForm(instance=user)

#     context = {
#         'form': form,
#         'user': user  # Pass the user object to the context
#     }    
#     return render(request, 'user/edit_user.html', context)

# @user_passes_test(lambda u: u.is_staff or u.is_superuser)
# def delete_user(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     user.delete()
#     messages.error(request, 'User deleted successfully.') 
#     return redirect('show_user') 

