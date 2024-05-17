import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
import os
import assemblyai as aai
import google.generativeai as genai
from .models import Video, VideoSession

def index(request):
    return render(request, 'ask_yourtube/index.html')


@csrf_exempt
def analyze_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            user_id = data.get('user_id')

            if not user_id:  
                user_id = uuid.uuid4()
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        # Configure Google Generative AI
        genai.configure(api_key=settings.GENAI_API_KEY)

        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript"}, status=500)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 256,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        try:
            model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)
        except:
            return JsonResponse({'error': "Failed to generate summary"}, status=500)
        
        chat_session = model.start_chat(history=[])

        #  Send the transcript as user input
        response = chat_session.send_message(f"""Based on the following transcript from a YouTube video, write a concise summary. Write it based on the transcript, but don't make it look like a YouTube video, and After you generate the summary, I will ask you questions about the video based on the transcript. Please answer my questions accurately and concisely.:

        {transcription}

        Summary:
        """)
        generated_summary = response.result

        # Create Video and VideoSession
        video, created = Video.objects.get_or_create(
            user_id=user_id, 
            youtube_link=yt_link,
            defaults={'youtube_title': title}
        )
        session = VideoSession.objects.create(video=video, transcript=transcription, summary=generated_summary)
        session.save()

        return JsonResponse({'summary': generated_summary, 'session_id': session.session_id, 'user_id': user_id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def ask_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data['question']
            session_id = data['session_id']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        genai.configure(api_key=settings.GENAI_API_KEY)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 512,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        try:
            model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)
        except:
            return JsonResponse({'error': "Failed to get answer"}, status=500)

        # Get the session from the database
        session = VideoSession.objects.get(session_id=session_id)

        # Construct the chat history based on previous messages
        chat_history = session.chat_history
        
        # Create a new chat session with the history
        chat_session = model.start_chat(history=chat_history)

        # Ask the question and get the answer
        response = chat_session.send_message(f"""Based on the following transcript from a YouTube video, answer the provided question.

        Question: 
        {question}

        Answer:
        """)
        generated_answer = response.result

        # Update the chat history in the session
        session.chat_history.append({
            "role": "user",
            "parts": [
                question
            ],
        })
        session.chat_history.append({
            "role": "model",
            "parts": [
                generated_answer
            ],
        })
        session.save()

        # return answer as a response
        return JsonResponse({'answer': generated_answer})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

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
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text

def video_list(request):
    user_id = request.GET.get('user_id') 
    if user_id:
        videos = Video.objects.filter(user_id=user_id).order_by('-created_at')
        return render(request, 'ask_yourtube/video_list.html', {'videos': videos, 'user_id': user_id})
    else:
        return render(request, 'ask_yourtube/index.html', {'error': 'User ID is required.'})

def video_details(request, video_id):
    user_id = request.GET.get('user_id') 
    if user_id:
        video = get_object_or_404(Video, id=video_id, user_id=user_id) 
        return render(request, 'ask_yourtube/video_details.html', {'video': video, 'user_id': user_id})
    else:
        return render(request, 'ask_yourtube/index.html', {'error': 'User ID is required.'})