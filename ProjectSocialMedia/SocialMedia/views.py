from django.shortcuts import render

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'home/about.html')

def blog(request):
    return render(request, 'home/blog.html')

def post_details(request):
    return render(request, 'home/post_details.html')

def contact(request):

    return render(request, 'home/contact.html')
