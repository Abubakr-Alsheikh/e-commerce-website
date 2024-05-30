import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import os
import assemblyai as aai
import google.generativeai as genai
from .models import Video, VideoSession, UserCustom
import mimetypes

def index(request):
    return render(request, 'ask_yourtube/index.html')

def _get_genai_model():
    # Configure Google Generative AI
    genai.configure(api_key=settings.GENAI_API_KEY)
    GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1024,
    }
    SAFETY_SETTINGS = [
        {"category": f"HARM_CATEGORY_{cat}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"} 
        for cat in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
    ]
    return genai.GenerativeModel(model_name="gemini-1.5-flash", 
                                    generation_config=GENERATION_CONFIG,
                                    safety_settings=SAFETY_SETTINGS)

@csrf_exempt
def analyze_video(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    user_id = request.POST.get('user_id')
    video_file = request.FILES.get('video')
    if not user_id or not video_file:
        return JsonResponse({'error': 'User ID and video file are required.'}, status=400)

    try:
        durationFile = float(request.POST.get('duration', 0)) 
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid duration information.'}, status=400)
    
    # Validate file type
    file_type = mimetypes.guess_type(video_file.name)[0]
    if not file_type.startswith("video/") and not file_type.startswith("audio/"):
        return JsonResponse({'error': 'Invalid file type. Please select a video or audio file.'}, status=400)

    # Validate file size
    MAX_FILE_SIZE_MB = 50
    if video_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return JsonResponse({'error': f'File size too large. The maximum allowed size is {MAX_FILE_SIZE_MB}MB.'}, status=400)

    # Validate file duration
    MAX_DURATION_MINUTES = 15 
    if durationFile > MAX_DURATION_MINUTES * 60:
        return JsonResponse({
            'error': f'Media duration too long. The maximum allowed duration is {MAX_DURATION_MINUTES} minutes. Your video is {durationFile/60:.2f} minutes long.'
        }, status=400)
    user, _ = UserCustom.objects.get_or_create(user_id=user_id)
    temp_video_path = os.path.join(settings.MEDIA_ROOT, f"temp_video_{uuid.uuid4()}.mp4")
    
    try:
        with open(temp_video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
    
        transcription = get_transcription(temp_video_path)
        os.remove(temp_video_path)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript, please try again."}, status=500)
        
        model = _get_genai_model()
        if not model:
            return JsonResponse({'error': "Failed to load GenAI model. Please try again later."}, status=500)

        chat_session = model.start_chat(history=[])
        prompt = f"""You will be provided with a transcript of a video. Please analyze it and write a concise summary of the video's content and write it in the same the language of the video. After you provide the summary, a user will be able to ask you questions about the video. You should use your knowledge of the transcript to answer those questions comprehensively and accurately. Here is the title of the video: {video_file.name}\n Here is the video transcript: \n{transcription}\n Summary: """
        response = chat_session.send_message(prompt)
        generated_summary = response.text  
        # generated_summary = "This is a dummy summary. "  # Replace this with your dummy data

        video = Video.objects.create(user_id=user, video_title=video_file.name)
        session = VideoSession.objects.create(video=video, transcript=transcription, summary=generated_summary)
        session.chat_history.extend([
            {"role": "user", "parts": [prompt]},
            {"role": "model", "parts": [generated_summary]},
        ])
        session.save()

        return JsonResponse({'summary': generated_summary, 'session_id': session.session_id, 'user_id': user_id, 'transcript': session.transcript})
    except Exception as e:
        os.remove(temp_video_path)
        return JsonResponse({'error': f"Something went wrong. Please try again later. Details: {e}"}, status=500)


@csrf_exempt
def ask_question(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        question = data['question']
        session_id = data['session_id']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid data sent'}, status=400)
    
    try:
        model = _get_genai_model()
        if not model:
            return JsonResponse({'error': "Failed to load GenAI model. Please try again later."}, status=500)

        session = VideoSession.objects.get(session_id=session_id)
        chat_session = model.start_chat(history=session.chat_history)
        response = chat_session.send_message(question) 
        generated_answer = response.text
        # generated_answer = "This is a dummy answer."  # Replace this with your dummy data

        session.chat_history.extend([
            {"role": "user", "parts": [question]},
            {"role": "model", "parts": [generated_answer]},
        ])
        session.save()

        return JsonResponse({'answer': generated_answer})
    except VideoSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found. Please try analyzing a video again.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"Something went wrong. Please try again later. Details: {e}"}, status=500)
    
def detect_language(audio_url):
    config = aai.TranscriptionConfig(
        audio_end_at=60000,  # first 60 seconds (in milliseconds)
        language_detection=True,
        speech_model=aai.SpeechModel.nano,
    )
    transcriber = aai.Transcriber()
    try:
        transcript = transcriber.transcribe(audio_url, config=config)
        return transcript.json_response["language_code"]
    except Exception as e:
        return None

def transcribe_file(audio_url, language_code):
    supported_languages_for_best = {'en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'nl-NL', 'pt-BR', 'tr-TR', 'ru-RU', 'hi-IN', 'ta-IN', 'mr-IN'}

    config = aai.TranscriptionConfig(
        language_code=language_code,
        speech_model=(
            aai.SpeechModel.best if language_code in supported_languages_for_best
            else aai.SpeechModel.nano
        ),
    )
    transcriber = aai.Transcriber()
    try:
        transcript = transcriber.transcribe(audio_url, config=config)
        return transcript
    except Exception as e:
        return None

def get_transcription(audio_file):
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    language_code = detect_language(audio_file)
    if not language_code:
        return None

    transcript = transcribe_file(audio_file, language_code)
    if not transcript:
        return None

    return transcript.text
    # return "This is a dummy transcription. "  # Replace this with your dummy data


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
        try:
            video = get_object_or_404(Video, id=video_id, user_id=user_id)
            video_session = VideoSession.objects.get(video=video) 

            chat_history = video_session.chat_history[2:]

            context = {
                'video': video,
                'user_id': user_id,
                'video_session': video_session,
                'chat_history': chat_history  
            }
            return render(request, 'ask_yourtube/video_details.html', context)

        except VideoSession.DoesNotExist:
            return render(request, 'ask_yourtube/index.html', {'error': 'Video session not found.'})

    else:
        return redirect('ask-yourtube:index') 