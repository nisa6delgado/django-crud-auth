from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from .forms import TaskForm
from .models import Task
from .resources import TaskResource


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
def excel(request):
    resource = TaskResource()
    dataset = resource.export()
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tareas.xlsx"'
    return response


@login_required
def pdf(request):
    tasks = Task.objects.all()

    data = [
        [
            Paragraph('<b>Título</b>'),
            Paragraph('<b>Descripción</b>'),
            Paragraph('<b>Fecha de creación</b>'),
            Paragraph('<b>Está completado?</b>'),
            Paragraph('<b>Es importante?</b>'),
            Paragraph('<b>Usuario</b>'),
        ],
    ]

    styles = getSampleStyleSheet()
    style = styles['Normal']

    for task in tasks:
        created = task.created.strftime('%d/%m/%Y')
        completed = 'Si' if task.completed else 'No'
        important = 'Si' if task.important == True else 'No'

        data.append([
            Paragraph(task.title, style),
            Paragraph(task.description, style),
            Paragraph(str(created), style),
            Paragraph(str(completed), style),
            Paragraph(str(important), style),
            Paragraph(str(task.user), style),
        ])
    
    buffer = BytesIO()
    
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=5,
        leftMargin=5,
        topMargin=5,
        bottomMargin=5
    )

    widthPage = letter[0] - document.leftMargin - document.rightMargin
    
    table = Table(data, colWidths=[None] * len(data[0]))
    
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
    ])
    
    table.setStyle(style)

    story = [table]
    document
    document.build(story)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tareas.pdf"'
    return response