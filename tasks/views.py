from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        if (request.POST['password1'] == request.POST['password2']):
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'],
                )
                user.save()
                
                login(request, user)

                return redirect('tasks')

            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'User already exists'
                })
            
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

def tasks(request):
    tasks = Task.objects.filter(
        user=request.user,
        completed__isnull=True
    )

    return render(request, 'tasks/index.html', {
        'tasks': tasks
    })

def create(request):
    if request.method == 'GET':
        return render(request, 'tasks/create.html', {
            'form': TaskForm
        })

    else:
        try:
            form = TaskForm(request.POST)
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks')

        except ValueError:
            return render(request, 'tasks/create.html', {
                'form': TaskForm,
                'error': 'Please provide valid data'
            })

def show(request, id):
    task = get_object_or_404(Task, pk=id)
    return render(request, 'tasks/show.html', {
        'task': task
    })

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })

    else:
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password'],
        )

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })

        else:
            login(request, user)
            return redirect('tasks')