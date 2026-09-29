import os
import json
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from fnol_agent.agent import ClaimsProcessingAgent

app = FastAPI(title="Autonomous Claims Processing Agent API", version="1.0.0")
agent = ClaimsProcessingAgent()

SAMPLES_DIR = Path("samples")

class TextProcessingRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Insurance Claims Processing Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen font-sans">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Header -->
        <header class="mb-8 border-b border-slate-800 pb-6 flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-extrabold text-white flex items-center gap-3">
                    <i class="fa-solid fa-shield-halved text-blue-500"></i>
                    FNOL Claims Processing Agent
                </h1>
                <p class="text-slate-400 mt-1 text-sm">Autonomous extraction, missing field validation & workflow routing engine</p>
            </div>
            <span class="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-full text-xs font-semibold">
                v1.0.0 Production
            </span>
        </header>

        <!-- Grid Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Left Column: Input Form & Samples -->
            <div class="lg:col-span-5 space-y-6">
                <!-- Sample Quick Select -->
                <div class="bg-slate-800/60 rounded-xl border border-slate-700/60 p-5 shadow-lg">
                    <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-folder-open text-blue-400"></i> Load Preset Sample FNOL
                    </h2>
                    <div class="grid grid-cols-1 gap-2">
                        <button onclick="loadPreset('sample_1_fasttrack.pdf')" class="text-left px-3 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition border border-slate-600/40 flex justify-between items-center">
                            <span><b>Sample 1:</b> Minor Auto Collision (< $25k)</span>
                            <span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded">Fast-track</span>
                        </button>
                        <button onclick="loadPreset('sample_2_manual_review.pdf')" class="text-left px-3 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition border border-slate-600/40 flex justify-between items-center">
                            <span><b>Sample 2:</b> Missing Policy & Contact</span>
                            <span class="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded">Manual Review</span>
                        </button>
                        <button onclick="loadPreset('sample_3_investigation.pdf')" class="text-left px-3 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition border border-slate-600/40 flex justify-between items-center">
                            <span><b>Sample 3:</b> Suspicious / Staged Claim</span>
                            <span class="text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded">Investigation</span>
                        </button>
                        <button onclick="loadPreset('sample_4_injury_specialist.pdf')" class="text-left px-3 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition border border-slate-600/40 flex justify-between items-center">
                            <span><b>Sample 4:</b> Bodily Injury Slip & Fall</span>
                            <span class="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded">Specialist</span>
                        </button>
                        <button onclick="loadPreset('sample_5_high_value.pdf')" class="text-left px-3 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-xs rounded-lg transition border border-slate-600/40 flex justify-between items-center">
                            <span><b>Sample 5:</b> High-Value Property ($185k)</span>
                            <span class="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">Standard Review</span>
                        </button>
                    </div>
                </div>

                <!-- Upload Document -->
                <div class="bg-slate-800/60 rounded-xl border border-slate-700/60 p-5 shadow-lg">
                    <h2 class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-cloud-arrow-up text-blue-400"></i> Upload FNOL File (.pdf / .txt)
                    </h2>
                    <form id="uploadForm" onsubmit="handleUpload(event)" class="space-y-4">
                        <div class="border-2 border-dashed border-slate-600 hover:border-blue-500 rounded-lg p-6 text-center bg-slate-900/40 transition cursor-pointer" onclick="document.getElementById('fileInput').click()">
                            <i class="fa-solid fa-file-pdf text-3xl text-slate-400 mb-2"></i>
                            <p class="text-xs text-slate-300">Click to select or drag & drop FNOL document</p>
                            <p class="text-[10px] text-slate-500 mt-1">Supports PDF and TXT formats</p>
                            <input type="file" id="fileInput" name="file" accept=".pdf,.txt" class="hidden" onchange="updateFileName(this)">
                        </div>
                        <div id="selectedFileName" class="text-xs text-blue-400 hidden font-mono"></div>
                        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2.5 rounded-lg transition shadow-md flex items-center justify-center gap-2">
                            <i class="fa-solid fa-bolt"></i> Process Claim Document
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Column: Results & Interactive Viewer -->
            <div class="lg:col-span-7 space-y-6">
                <!-- Status Banner -->
                <div id="resultBanner" class="bg-slate-800/60 rounded-xl border border-slate-700/60 p-6 shadow-lg hidden">
                    <div class="flex items-start justify-between">
                        <div>
                            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Recommended Workflow Route</span>
                            <h3 id="recommendedRouteText" class="text-2xl font-black mt-1">---</h3>
                        </div>
                        <span id="routeBadge" class="px-4 py-1.5 rounded-full text-xs font-bold tracking-wide shadow-inner">
                            ---
                        </span>
                    </div>

                    <div class="mt-4 pt-4 border-t border-slate-700/60">
                        <h4 class="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Decision Reasoning</h4>
                        <p id="reasoningText" class="text-sm text-slate-300 leading-relaxed font-light">---</p>
                    </div>

                    <div id="missingFieldsContainer" class="mt-4 pt-4 border-t border-slate-700/60 hidden">
                        <h4 class="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                            <i class="fa-solid fa-triangle-exclamation"></i> Missing Mandatory Fields
                        </h4>
                        <div id="missingFieldsBadges" class="flex flex-wrap gap-2"></div>
                    </div>
                </div>

                <!-- Structured Extracted Fields Viewer -->
                <div id="extractedFieldsCard" class="bg-slate-800/60 rounded-xl border border-slate-700/60 p-6 shadow-lg hidden">
                    <div class="flex items-center justify-between mb-4 border-b border-slate-700/60 pb-3">
                        <h3 class="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                            <i class="fa-solid fa-list-check text-blue-400"></i> Extracted Claim Fields
                        </h3>
                        <button onclick="copyJSON()" class="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded transition flex items-center gap-1.5">
                            <i class="fa-solid fa-copy"></i> Copy Raw JSON
                        </button>
                    </div>

                    <div id="jsonViewer" class="bg-slate-950 p-4 rounded-lg font-mono text-xs text-emerald-400 overflow-x-auto max-h-[450px]">
                        Select or upload a document to process...
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentResult = null;

        function updateFileName(input) {
            const fileNameDiv = document.getElementById('selectedFileName');
            if (input.files.length > 0) {
                fileNameDiv.textContent = "Selected: " + input.files[0].name;
                fileNameDiv.classList.remove('hidden');
            }
        }

        async function handleUpload(e) {
            e.preventDefault();
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                const response = await fetch('/api/process-file', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                displayResult(data);
            } catch (err) {
                alert("Error processing document: " + err.message);
            }
        }

        async function loadPreset(filename) {
            try {
                const response = await fetch('/api/process-preset/' + filename);
                const data = await response.json();
                displayResult(data);
            } catch (err) {
                alert("Error loading preset: " + err.message);
            }
        }

        function displayResult(data) {
            currentResult = data;
            document.getElementById('resultBanner').classList.remove('hidden');
            document.getElementById('extractedFieldsCard').classList.remove('hidden');

            document.getElementById('recommendedRouteText').textContent = data.recommendedRoute;
            document.getElementById('reasoningText').textContent = data.reasoning;

            const badge = document.getElementById('routeBadge');
            badge.textContent = data.recommendedRoute;

            if (data.recommendedRoute === 'Fast-track') {
                badge.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
                document.getElementById('recommendedRouteText').className = "text-2xl font-black mt-1 text-emerald-400";
            } else if (data.recommendedRoute === 'Manual Review') {
                badge.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30";
                document.getElementById('recommendedRouteText').className = "text-2xl font-black mt-1 text-amber-400";
            } else if (data.recommendedRoute === 'Investigation Flag') {
                badge.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30";
                document.getElementById('recommendedRouteText').className = "text-2xl font-black mt-1 text-rose-400";
            } else if (data.recommendedRoute === 'Specialist Queue') {
                badge.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30";
                document.getElementById('recommendedRouteText').className = "text-2xl font-black mt-1 text-purple-400";
            } else {
                badge.className = "px-4 py-1.5 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30";
                document.getElementById('recommendedRouteText').className = "text-2xl font-black mt-1 text-blue-400";
            }

            const missingDiv = document.getElementById('missingFieldsContainer');
            const badgesDiv = document.getElementById('missingFieldsBadges');
            badgesDiv.innerHTML = '';

            if (data.missingFields && data.missingFields.length > 0) {
                missingDiv.classList.remove('hidden');
                data.missingFields.forEach(field => {
                    const span = document.createElement('span');
                    span.className = "px-2.5 py-1 bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[11px] font-mono rounded-md";
                    span.textContent = field;
                    badgesDiv.appendChild(span);
                });
            } else {
                missingDiv.classList.add('hidden');
            }

            document.getElementById('jsonViewer').textContent = JSON.stringify(data, null, 2);
        }

        function copyJSON() {
            if (!currentResult) return;
            navigator.clipboard.writeText(JSON.stringify(currentResult, null, 2));
            alert("Raw JSON response copied to clipboard!");
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/process-file")
async def process_file(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    temp_path = SAMPLES_DIR / f"temp_{file.filename}"
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        result = agent.process_file(str(temp_path))
        return JSONResponse(content=result.to_dict())
    finally:
        if temp_path.exists():
            temp_path.unlink()

@app.get("/api/process-preset/{filename}")
def process_preset(filename: str):
    preset_path = SAMPLES_DIR / filename
    if not preset_path.exists():
        raise HTTPException(status_code=404, detail="Preset file not found.")

    result = agent.process_file(str(preset_path))
    return JSONResponse(content=result.to_dict())

@app.post("/api/process-text")
def process_text(req: TextProcessingRequest):
    result = agent.process_text(req.text)
    return JSONResponse(content=result.to_dict())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
