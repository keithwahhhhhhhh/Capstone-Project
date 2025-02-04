from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, url_for, Response
from flask_login import current_user
from app.classes.data import Task
from app.classes.forms import TaskForm
from flask_login import login_required
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io


@app.route('/task/list')

@login_required
def taskList():

    tasks = Task.objects()

    return render_template('tasks.html',tasks=tasks)

@app.route('/task/moodRating')
@login_required
def moodList():

    tasks = Task.objects()
    moodList = []
    for task in tasks:
        moodList.append(task.moodRating)
        

    moodList.sort()

    plt.rcParams["figure.figsize"] = [1, 1]
    plt.rcParams["figure.autolayout"] = True

    fig, ax = plt.subplots(figsize=(11, 11))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1)) 
    n, bins, patches = plt.hist(moodList, 10)

    plt.xlabel('Mood Rating Value')
    plt.ylabel('Number of Mood Rating Value')
    plt.title('Histogram of Mood Rating')
    plt.grid(True)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


@app.route('/task/sleepTimes')
@login_required
def sleepList():

    tasks = Task.objects()
    sleepList = []
    for task in tasks:
        sleepList.append(int(task.sleepTime))

    sleepList.sort()

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
 
    n, bins, patches = plt.hist(sleepList, 10)

    plt.xlabel('Number of hours slept')
    plt.ylabel('Number of times you spent sleeping those amount of hours')
    plt.title('Histogram of Sleep Hours')
    plt.grid(True)
    #plt.show()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')

@app.route('/task/<taskID>')

@login_required
def task(taskID):

    thisTask = Task.objects.get(id=taskID)

    return render_template('task.html',task=thisTask)

@app.route('/task/delete/<taskID>')

@login_required
def taskDelete(taskID):

    deleteTask = Task.objects.get(id=taskID)

    if current_user == deleteTask.author:

        deleteTask.delete()

        flash('The entry was deleted.')
    else:

        flash("You can't delete an entry you don't own.")

    tasks = Task.objects()  

    return render_template('tasks.html',tasks=tasks)

@app.route('/task/new', methods=['GET', 'POST'])

@login_required

def taskNew():

    form = TaskForm()

    if form.validate_on_submit():

 
        newTask = Task(
            sleepTime = form.sleepTime.data,
            work = form.work.data,
            exercise = form.exercise.data,
            exercises = form.exercises.data,
            moodRating = form.moodRating.data,
            meal = form.meal.data,
            meals = form.meals.data,
            thoughts = form.thoughts.data,
            dental = form.dental.data,
            shower = form.shower.data,

            author = current_user.id,
            modifydate = dt.datetime.utcnow
        )
        
        newTask.save()

        return redirect(url_for('task',taskID=newTask.id))

    return render_template('taskform.html',form=form)

@app.route('/task/edit/<taskID>', methods=['GET', 'POST'])
@login_required
def TaskEdit(taskID):
    editTask = Task.objects.get(id=taskID)

    if current_user != editTask.author:
        flash("You can't edit an entry you don't own.")
        return redirect(url_for('task',taskID=taskID))

    form = TaskForm()

    if form.validate_on_submit():

        editTask.update(
            sleepTime= form.sleepTime.data,
            work = form.work.data,
            exercise = form.exercise.data,
            exercises = form.exercises.data,
            moodRating = form.moodRating.data,
            meal = form.meal.data,
            meals = form.meals.data,
            thoughts = form.thoughts.data,
            dental = form.dental.data,
            shower = form.shower.data,
            modifydate = dt.datetime.utcnow
        )

        return redirect(url_for('task',taskID=taskID))

    form.sleepTime.data = editTask.sleepTime
    form.work.data = editTask.work
    form.exercise.data = editTask.exercise
    form.exercises.data = editTask.exercises
    form.moodRating.data = editTask.moodRating
    form.meals.data = editTask.meals
    form.meal.data = editTask.meal
    form.thoughts.data = editTask.thoughts
    form.dental.data = editTask.dental
    form.shower.data = editTask.shower

    return render_template('taskform.html',form=form)
