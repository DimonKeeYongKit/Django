from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, HttpResponse
import calendar
from calendar import HTMLCalendar, month_name
from datetime import datetime

from reportlab.lib import pagesizes
from .models import Event, Venue
from .forms import VenueForm, EventForm
import csv

# import PDF Stuff
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# import Pagenation Stuff
from django.core.paginator import Paginator

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    month = month.capitalize()

    # convert str month to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    #create calander
    cal = HTMLCalendar().formatmonth(year, month_number)
    
    # get current year
    now = datetime.now()
    current_year = now.year

    # get current time
    time = now.strftime('%I:%M:%S %p')
    return render(request, 'home.html', {
        'name': 'Dimon',
        'year':year,
        'month':month,
        'month_number':month_number,
        'cal':cal,
        'current_year': current_year,
        'time': time,
    })

def all_events(request):
    event_list = Event.objects.all().order_by('event_date','-name')
    return render(request, 'event_list.html', {'event_list':event_list})


def list_venues(request):
    # venue_list = Venue.objects.all().order_by('?') # ? for random
    venue_list = Venue.objects.all()

    # set up Pagination
    p = Paginator(Venue.objects.all(), per_page=2)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = "a" * venues.paginator.num_pages

    return render(request, 'venue.html', {'venue_list':venue_list, 'venues':venues, 'nums':nums})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    return render(request, 'show_venue.html', {'venue':venue})


def add_venue(request):
    submitted = False

    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_venue.html', {'form':form, 'submitted':submitted})


def search_venue(request):
    if request.method == "POST":
        searched = request.POST.get('searched')
        venues = Venue.objects.filter(name__icontains=searched)
        return render(request, 'search_venue.html', {'search':searched, 'venues':venues})
    else:
        return render(request, 'search_venue.html', {})


def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list_venues')
    return render(request, 'update_venue.html', {'venue':venue, 'form':form})


def add_event(request):
    submitted = False

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_event?submitted=True')
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_event.html', {'form':form, 'submitted':submitted})


def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('all_events')
    return render(request, 'update_event.html', {'event':event, 'form':form})


def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('all_events')


def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list_venues')


def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'

    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n\n ')

    # lines = ["This is line 1\n",
    # 'This is line 2\n',
    # 'This is line 3\n4',]

    response.writelines(lines)
    return response


def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'

    # Create a csv writer
    writer = csv.writer(response)

    # Designate the Model
    venues = Venue.objects.all()

    # Add heading in csv file
    writer.writerow(['Venue Name', "Address", 'Zip Code', 'Phone', 'Web', "Email Address"])

    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code, venue.phone, venue.web, venue.email_address])

    # lines = ["This is line 1\n",
    # 'This is line 2\n',
    # 'This is line 3\n4',]

    return response


def venue_pdf(request):
    # Create Bytestram buffer
    buf = io.BytesIO()

    # create a canvas
    c= canvas.Canvas(buf,pagesize=letter, bottomup=0)

    # Create a text object
    textOJ = c.beginText()
    textOJ.setTextOrigin(inch, inch)
    textOJ.setFont("Helvetica",14)

    # Designate the Model
    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append(" ")
    
    for line in lines:
       textOJ.textLine(line)

    #Finish Up
    c.drawText(textOJ)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='venues.pdf')