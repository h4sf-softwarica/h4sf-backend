import os
import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

@csrf_exempt
@require_POST
def upload_chunk(request):
    chunk = request.FILES.get('chunk')
    upload_id = request.POST.get('upload_id')
    chunk_index = int(request.POST.get('chunk_index'))
    total_chunks = int(request.POST.get('total_chunks'))
    
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads', upload_id)
    os.makedirs(temp_dir, exist_ok=True)
    chunk_path = os.path.join(temp_dir, f"chunk_{chunk_index}")

    with open(chunk_path, 'wb') as f:
        for c in chunk.chunks():
            f.write(c)

    # After receiving all chunks, assemble them into final file
    if chunk_index + 1 == total_chunks:
        final_path = os.path.join(settings.MEDIA_ROOT, f"{upload_id}.mp4")
        with open(final_path, 'wb') as outfile:
            for i in range(total_chunks):
                chunk_file = os.path.join(temp_dir, f"chunk_{i}")
                with open(chunk_file, 'rb') as infile:
                    outfile.write(infile.read())
        # Cleanup chunks
        for i in range(total_chunks):
            os.remove(os.path.join(temp_dir, f"chunk_{i}"))
        os.rmdir(temp_dir)

    return JsonResponse({'status': 'chunk received', 'chunk_index': chunk_index})

@csrf_exempt
@require_POST
def generate_analysis(request):
    try:
        data = json.loads(request.body)
        upload_id = data.get('upload_id')
        if not upload_id:
            return JsonResponse({'error': 'upload_id not provided'}, status=400)

        video_path = os.path.join(settings.MEDIA_ROOT, f"{upload_id}.mp4")
        if not os.path.exists(video_path):
            return JsonResponse({'error': 'Video file not found'}, status=404)

        result = subprocess.run(
            ['python3', 'main.py', '--mode', 'video', '--video', video_path, '--confidence', '0.5'],
            cwd=settings.VIDEO_ANALYSIS_SCRIPT_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        result_file = os.path.join(settings.VIDEO_ANALYSIS_SCRIPT_DIR, 'test_results', 'video_safety_analysis.txt')
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8', errors='ignore') as f:
                result_text = f.read()
        else:
            result_text = 'Analysis result file not found.'

        return JsonResponse({'result': result_text})

    except Exception as e:
        return JsonResponse({'error': f'Error processing video: {str(e)}'}, status=500)
