from django.shortcuts import render , redirect 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from pytube import YouTube
import assemblyai as aai
from .models import BlogPost
from dotenv import load_dotenv
import os
# Create your views here.




@login_required
def index(request):
    return render(request,'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            
        except(KeyError, json.JSONDecodeError):
            return JsonResponse({'error' : 'Invalid data sent'} , status=400)
        
        #get yt title
        title = yt_title(yt_link)
        #get translate
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error' : 'Failed to get transscipt'}, status=500)
        
        
        #save blog article to database
        new_blog_article = BlogPost.objects.create(
            user = request.user ,
            youtube_title = title ,
            youtube_link = yt_link ,
            generated_content = transcription
        )
        
        new_blog_article.save()
        
        #return blog articles as a response
        return JsonResponse({'content' : transcription})
    else:
        return JsonResponse({'error' : 'Invalid request method'} , status=405)
    
    

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file , new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = os.environ.get('API_KEY')
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text


def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request , 'all-blogs.html' , {'blog_articles' : blog_articles})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username = username , password = password)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username and password"
            return render(request, 'login.html',  {'error_message' : error_message})      
    return render(request, 'login.html')

def user_signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatpassword = request.POST['repeatpassword']
                
                
        if User.objects.filter(username=username).exits():
            error_message = "Username is Alreay Taken.."
            return render(request , 'signup.html', {'error_message': error_message})
            
        elif password == repeatpassword:
            try:
                user = User.objects.create_user(username,email,password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error Creating Account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
            
    return render(request, 'signup.html')

def blog_details(request , pk):
    blog_article_details = BlogPost.objects.get(id=pk)
    if request.user == blog_article_details.user:
        return render(request , 'blog-details.html' , {'blog_article_details' : blog_article_details})
    else:
        return redirect('/')
def user_logout(request):
    logout(request)
    return render(request, 'signup.html')