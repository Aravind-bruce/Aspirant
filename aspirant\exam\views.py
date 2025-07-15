import os
import subprocess
import tempfile
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Disable CSRF for AJAX requests
def compiler(request):
    print("Request Method:", request.method)  # ✅ Debug print

    if request.method == "POST":
        language = request.POST.get("language", "")
        code = request.POST.get("code", "")
        input_data = request.POST.get("input", "")

        if not language or not code:
            return JsonResponse({"output": "❌ Missing code or language."})

        output = ""
        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = ""
            try:
                if language == "python":
                    code_file = os.path.join(temp_dir, "program.py")
                    command = ["python3", code_file]
                elif language == "c":
                    code_file = os.path.join(temp_dir, "program.c")
                    binary_file = os.path.join(temp_dir, "program")
                    compile_command = ["gcc", code_file, "-o", binary_file]
                    command = [binary_file]
                elif language == "cpp":
                    code_file = os.path.join(temp_dir, "program.cpp")
                    binary_file = os.path.join(temp_dir, "program")
                    compile_command = ["g++", code_file, "-o", binary_file]
                    command = [binary_file]
                elif language == "java":
                    code_file = os.path.join(temp_dir, "Main.java")
                    compile_command = ["javac", code_file]
                    command = ["java", "-cp", temp_dir, "Main"]
                elif language == "php":
                    code_file = os.path.join(temp_dir, "program.php")
                    command = ["php", code_file]
                elif language == "javascript":
                    code_file = os.path.join(temp_dir, "program.js")
                    command = ["node", code_file]
                else:
                    return JsonResponse({"output": "❌ Unsupported language"})

                with open(code_file, "w") as f:
                    f.write(code)

                if language in ["c", "cpp", "java"]:
                    compile_result = subprocess.run(compile_command, capture_output=True, text=True)
                    if compile_result.returncode != 0:
                        return JsonResponse({"output": compile_result.stderr})

                execution_result = subprocess.run(command, input=input_data, capture_output=True, text=True, timeout=5)
                output = execution_result.stdout if execution_result.returncode == 0 else execution_result.stderr

            except Exception as e:
                output = str(e)

        return JsonResponse({"output": output})

    return JsonResponse({"output": "❌ Invalid request method."})  # ✅ Ensure valid method
