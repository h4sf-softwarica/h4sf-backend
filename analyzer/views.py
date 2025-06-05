import os
import subprocess
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

@csrf_exempt
@require_POST
def generate_analysis(request):
    video_file = request.FILES.get('video')
    if not video_file:
        return JsonResponse({'error': 'No video uploaded.'}, status=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        for chunk in video_file.chunks():
            temp_video.write(chunk)
        temp_video_path = temp_video.name

    try:
        result = subprocess.run(
            ['python3', 'main.py', '--mode', 'video', '--video', temp_video_path, '--confidence', '0.5'],
            cwd=settings.VIDEO_ANALYSIS_SCRIPT_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        # print("Return Code:", result.returncode)
        # print("STDOUT:\n", result.stdout)
        # print("STDERR:\n", result.stderr)

        result_file = os.path.join(settings.VIDEO_ANALYSIS_SCRIPT_DIR, 'test_results','video_safety_analysis.txt')
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8', errors='ignore') as f:
                result_text = f.read()
        else:
            result_text = 'Analysis result file not found.'

    except Exception as e:
        result_text = f'Error processing video: {str(e)}'
    finally:
        os.remove(temp_video_path)

    return JsonResponse({'result': result_text})
