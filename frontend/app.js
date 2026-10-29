// ClanVox Frontend Real-Time Client

let socket = null;
let audioContext = null;
let mediaStream = null;
let audioProcessor = null;
let isRecording = false;
let audioQueue = [];
let isPlayingAudio = false;
let sessionId = 'sess_' + Math.random().toString(36).substring(2, 9);
let currentAssistantMessageElement = null;

// DOM Elements
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');
const turnState = document.getElementById('turnState');
const micBtn = document.getElementById('micBtn');
const interruptBtn = document.getElementById('interruptBtn');
const visualizerHint = document.getElementById('visualizerHint');
const matrixLangBadge = document.getElementById('matrixLangBadge');
const codeSwitchBadge = document.getElementById('codeSwitchBadge');
const latencyBadge = document.getElementById('latencyBadge');
const transcriptBox = document.getElementById('transcriptBox');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const clearChatBtn = document.getElementById('clearChatBtn');
const languageSelect = document.getElementById('languageSelect');
const canvas = document.getElementById('waveformCanvas');
const canvasCtx = canvas.getContext('2d');

// Initialize WebSocket Connection
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host || 'localhost:8000';
  const wsUrl = `${protocol}//${host}/v1/realtime?session_id=${sessionId}`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    statusBadge.classList.add('connected');
    statusText.textContent = 'Connected';
    // Send initial language configuration
    if (languageSelect.value !== 'auto') {
      sendConfigUpdate({ language: languageSelect.value });
    }
  };

  socket.onclose = () => {
    statusBadge.classList.remove('connected');
    statusText.textContent = 'Disconnected';
    setTimeout(connectWebSocket, 2000);
  };

  socket.onerror = (err) => {
    console.error('WebSocket Error:', err);
  };

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleServerEvent(msg);
    } catch (e) {
      console.error('Failed to parse message', e);
    }
  };
}

function handleServerEvent(msg) {
  switch (msg.type) {
    case 'state':
      updateStatePill(msg.value);
      if (msg.value === 'speaking') {
        interruptBtn.disabled = false;
      } else if (msg.value === 'idle' || msg.value === 'listening') {
        interruptBtn.disabled = true;
      }
      break;

    case 'stt.partial':
      visualizerHint.textContent = msg.text || 'Listening...';
      break;

    case 'stt.final':
      visualizerHint.textContent = '';
      appendMessage('user', msg.text, msg.lang || 'en');
      matrixLangBadge.textContent = (msg.lang || 'en').toUpperCase();
      currentAssistantMessageElement = null; // Prepare for new assistant turn
      break;

    case 'llm.delta':
      appendAssistantDelta(msg.text);
      break;

    case 'tts.audio':
      if (msg.data) {
        queueAudioPlayback(msg.data);
      }
      break;

    case 'tool.call':
      appendSystemNotice(`⚡ Calling Tool: ${msg.name}...`);
      break;

    case 'error':
      appendSystemNotice(`⚠️ Error: ${msg.message}`);
      break;
  }
}

function updateStatePill(state) {
  turnState.className = `state-pill ${state}`;
  turnState.textContent = state.toUpperCase();
}

function appendMessage(sender, text, lang) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;

  const metaDiv = document.createElement('div');
  metaDiv.className = 'msg-meta';

  const nameSpan = document.createElement('span');
  nameSpan.className = 'sender-name';
  nameSpan.textContent = sender === 'user' ? 'You' : 'ClanVox';

  const langSpan = document.createElement('span');
  langSpan.className = 'msg-lang';
  langSpan.textContent = lang || 'en';

  metaDiv.appendChild(nameSpan);
  metaDiv.appendChild(langSpan);

  const contentDiv = document.createElement('div');
  contentDiv.className = 'msg-content';
  contentDiv.textContent = text;

  msgDiv.appendChild(metaDiv);
  msgDiv.appendChild(contentDiv);

  transcriptBox.appendChild(msgDiv);
  transcriptBox.scrollTop = transcriptBox.scrollHeight;
  return contentDiv;
}

function appendAssistantDelta(token) {
  if (!currentAssistantMessageElement) {
    currentAssistantMessageElement = appendMessage('assistant', '', languageSelect.value || 'en');
  }
  currentAssistantMessageElement.textContent += token;
  transcriptBox.scrollTop = transcriptBox.scrollHeight;
}

function appendSystemNotice(text) {
  const notice = document.createElement('div');
  notice.style.fontSize = '12px';
  notice.style.color = '#94a3b8';
  notice.style.textAlign = 'center';
  notice.style.margin = '4px 0';
  notice.textContent = text;
  transcriptBox.appendChild(notice);
  transcriptBox.scrollTop = transcriptBox.scrollHeight;
}

// Audio Recording & Streaming
async function toggleRecording() {
  if (isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    }
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 16000,
        channelCount: 1
      }
    });

    const source = audioContext.createMediaStreamSource(mediaStream);
    audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);

    audioProcessor.onaudioprocess = (e) => {
      if (!isRecording) return;
      const inputData = e.inputBuffer.getChannelData(0);

      // Convert Float32 to 16-bit PCM
      const pcm16 = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]));
        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      // Convert buffer to base64 and send
      const base64Audio = arrayBufferToBase64(pcm16.buffer);
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'audio.chunk',
          data: base64Audio
        }));
      }

      drawWaveform(inputData);
    };

    source.connect(audioProcessor);
    audioProcessor.connect(audioContext.destination);

    isRecording = true;
    micBtn.classList.add('active');
    visualizerHint.textContent = 'Listening... Speak now';
  } catch (err) {
    console.error('Microphone access denied:', err);
    alert('Microphone access is required for real-time voice chat.');
  }
}

function stopRecording() {
  isRecording = false;
  micBtn.classList.remove('active');
  visualizerHint.textContent = 'Tap microphone to speak';

  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop());
  }
  if (audioProcessor) {
    audioProcessor.disconnect();
  }
  clearCanvas();
}

// Convert ArrayBuffer to Base64
function arrayBufferToBase64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

// Base64 to Int16Array
function base64ToInt16Array(base64) {
  const binary = window.atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Int16Array(bytes.buffer);
}

// Queue & Play incoming TTS Audio
function queueAudioPlayback(base64Data) {
  const pcm16 = base64ToInt16Array(base64Data);
  audioQueue.push(pcm16);
  if (!isPlayingAudio) {
    playNextAudio();
  }
}

async function playNextAudio() {
  if (audioQueue.length === 0) {
    isPlayingAudio = false;
    return;
  }
  isPlayingAudio = true;
  const pcm16 = audioQueue.shift();

  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
  }

  const audioBuffer = audioContext.createBuffer(1, pcm16.length, 16000);
  const channelData = audioBuffer.getChannelData(0);
  for (let i = 0; i < pcm16.length; i++) {
    channelData[i] = pcm16[i] / 32768.0;
  }

  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);

  source.onended = () => {
    playNextAudio();
  };

  source.start();
}

// Barge-in / Interrupt
function triggerBargeIn() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'interrupt' }));
  }
  // Flush local audio queue immediately
  audioQueue = [];
  isPlayingAudio = false;
}

// Visualizer Waveform Animation
function drawWaveform(dataArray) {
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
  canvasCtx.lineWidth = 2;
  canvasCtx.strokeStyle = '#06b6d4';
  canvasCtx.beginPath();

  const sliceWidth = canvas.width * 1.0 / dataArray.length;
  let x = 0;

  for (let i = 0; i < dataArray.length; i += 8) {
    const v = dataArray[i] * 50.0;
    const y = (canvas.height / 2) + v;
    if (i === 0) {
      canvasCtx.moveTo(x, y);
    } else {
      canvasCtx.lineTo(x, y);
    }
    x += sliceWidth * 8;
  }

  canvasCtx.stroke();
}

function clearCanvas() {
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
}

function sendConfigUpdate(config) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: 'config.update',
      ...config
    }));
  }
}

// Event Listeners
micBtn.addEventListener('click', toggleRecording);
interruptBtn.addEventListener('click', triggerBargeIn);

languageSelect.addEventListener('change', (e) => {
  const lang = e.target.value;
  if (lang !== 'auto') {
    sendConfigUpdate({ language: lang });
    matrixLangBadge.textContent = lang.toUpperCase();
  }
});

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = '';
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type: 'text.message',
      text: text,
      language: languageSelect.value === 'auto' ? null : languageSelect.value
    }));
  }
});

clearChatBtn.addEventListener('click', () => {
  transcriptBox.innerHTML = '';
});

// Connect on page load
window.addEventListener('DOMContentLoaded', () => {
  connectWebSocket();
});

