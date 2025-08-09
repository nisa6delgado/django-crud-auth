from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .resources import TaskResource
from django.http import HttpResponse


def home(request):
    return render(request, 'index.html')


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


@login_required
def tasks(request):
    tasks = Task.objects.filter(
        user=request.user,
        completed__isnull=True
    )

    return render(request, 'tasks/index.html', {
        'tasks': tasks
    })


@login_required
def tasks(request):
    tasks = Task.objects.filter(
        user=request.user,
        completed__isnull=True
    )

    return render(request, 'tasks/index.html', {
        'tasks': tasks,
        'title': 'Tareas pendientes',
    })


@login_required
def completed(request):
    tasks = Task.objects.filter(
            user=request.user,
            completed__isnull=False
        ).order_by('-completed')

    return render(request, 'tasks/index.html', {
        'tasks': tasks,
        'title': 'Tareas completadas',
    })


@login_required
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


@login_required
def show(request, id):
    task = get_object_or_404(Task, pk=id, user=request.user)

    if request.method == 'GET':
        form = TaskForm(instance=task)
        return render(request, 'tasks/show.html', {
            'task': task,
            'form': form,
        })

    else:
        try:
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')

        except ValueError:
            return render(request, 'tasks/show.html', {
                'task': task,
                'form': form,
                'error': 'Error actualizando tarea'
            })


@login_required
def complete(request, id):
    task = get_object_or_404(Task, pk=id, user=request.user)

    if request.method == 'POST':
        task.completed = timezone.now()
        task.save()

        return redirect('tasks')


@login_required
def delete(request, id):
    task = get_object_or_404(Task, pk=id, user=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
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
        

@login_required
def export(request):
    resource = TaskResource()
    dataset = resource.export()
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tareas.xlsx"'
    return response