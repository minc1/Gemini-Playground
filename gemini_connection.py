import asyncio
import os
import json
import base64
import pyaudio
from websockets import connect
from concurrent.futures import CancelledError
from voice_activity_detector import VoiceActivityDetector

class GeminiConnection:
    def __init__(self, config=None, cleanup_event=None, on_connect=None, video_capture=None):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        self.model = "gemini-2.0-flash-exp"
        self.config = config or {
            "system_prompt": "BE IRREVERNTLY FUNNY. You are a personal assistant with over 180 IQ. You answer directly and immediately without answering the user's question with another question.",
            "voice": "Kore",
            "video_mode": "none"
        }
        
        self.uri = (
            "wss://generativelanguage.googleapis.com/ws/"
            "google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
            f"?key={self.api_key}"
        )
        
        self.ws = None
        self.vad = VoiceActivityDetector()
        self.equalizer = None
        self.video_capture = video_capture
        self.audio_stream = None

        # Audio settings
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.INPUT_RATE = 16000
        self.OUTPUT_RATE = 24000
        self.CHUNK = 512

        self.audio_queue = asyncio.Queue()
        self.is_playing = False
        self.running = True
        self.cleanup_event = cleanup_event
        self.on_connect = on_connect
        self.allow_interruptions = config.get("allow_interruptions", False)

    def set_equalizer(self, equalizer):
        """Set the equalizer for visual feedback"""
        self.equalizer = equalizer

    async def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                print(f"Error closing websocket: {e}")
        
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")

    async def start(self):
        try:
            self.ws = await connect(self.uri)
            
            generation_config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": self.config.get("voice", "Kore")
                        }
                    }
                },
                "temperature": self.config.get("temperature", 0.7),
                "top_p": self.config.get("top_p", 0.95),
                "top_k": self.config.get("top_k", 40)
            }
            
            setup_message = {
                "setup": {
                    "model": f"models/{self.model}",
                    "generation_config": generation_config,
                    "system_instruction": {
                        "parts": [
                            {
                                "text": self.config.get("system_prompt", "")
                            }
                        ]
                    }
                }
            }
                
            setup_message = {
                "setup": {
                    "model": f"models/{self.model}",
                    "generation_config": generation_config,
                    "system_instruction": {
                        "parts": [
                            {
                                "text": self.config.get("system_prompt", "")
                            }
                        ]
                    }
                }
            }
            
            await self.ws.send(json.dumps(setup_message))
            first_msg = await self.ws.recv()
            
            if not first_msg:
                raise ConnectionError("Failed to receive initial message from Gemini")
                
            print("Connected to Gemini. Speak into your microphone.")
            
            if self.on_connect:
                asyncio.get_event_loop().call_soon_threadsafe(self.on_connect)
            
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.capture_audio())
                
                if self.video_capture and self.config.get("video_mode") != "none":
                    tg.create_task(self.capture_video())
                    
                tg.create_task(self.receive_server_messages())
                tg.create_task(self.play_responses())
                tg.create_task(self.watch_cleanup())

        except Exception as e:
            print(f"Error in Gemini connection: {e}")
            raise
        finally:
            await self.cleanup()

    async def capture_video(self):
        """Capture and send video frames to Gemini"""
        while self.running:
            try:
                if not self.video_capture:
                    break
                    
                frame = self.video_capture.get_frame()
                if frame:
                    msg = {
                        "realtime_input": {
                            "media_chunks": [frame]
                        }
                    }
                    if self.ws:
                        await self.ws.send(json.dumps(msg))
                await asyncio.sleep(1.0)  # Capture every second
            except Exception as e:
                print(f"Error capturing video: {e}")
                await asyncio.sleep(1.0)

    async def capture_audio(self):
        """Capture audio from microphone and send to Gemini"""
        audio = pyaudio.PyAudio()
        try:
            self.audio_stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.INPUT_RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            while self.running:
                try:
                    data = await asyncio.to_thread(
                        self.audio_stream.read, 
                        self.CHUNK, 
                        exception_on_overflow=False
                    )
                    
                    if self.equalizer:
                        self.equalizer.update_levels(data)
                    
                    should_process = (not self.is_playing) or (
                        self.is_playing and self.allow_interruptions
                    )

                    if should_process and self.ws:
                        if not self.vad.is_speech(data):
                            if not hasattr(self, '_printed_no_speech'):
                                print("No speech detected")
                                self._printed_no_speech = True
                            data = b'\x00' * len(data)
                        else:
                            self._printed_no_speech = False
                        
                        msg = {
                            "realtime_input": {
                                "media_chunks": [
                                    {
                                        "data": base64.b64encode(data).decode(),
                                        "mime_type": "audio/pcm"
                                    }
                                ]
                            }
                        }
                        await self.ws.send(json.dumps(msg))
                    else:
                        if not hasattr(self, '_printed_skip_message'):
                            print("Skipping input while Gemini is speaking")
                            self._printed_skip_message = True
                        elif not self.is_playing:
                            self._printed_skip_message = False

                except OSError as e:
                    print(f"Audio capture error: {e}")
                    await asyncio.sleep(0.1)
                    continue

        except CancelledError:
            print("Audio capture cancelled")
        except Exception as e:
            print(f"Unexpected error in capture_audio: {e}")
        finally:
            if self.audio_stream:
                try:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                except:
                    pass
            try:
                audio.terminate()
            except:
                pass

    async def receive_server_messages(self):
        """Receive and process messages from Gemini"""
        if not self.ws:
            return
            
        async for msg in self.ws:
            try:
                response = json.loads(msg)
                
                try:
                    parts = response["serverContent"].get("modelTurn", {}).get("parts", [])
                    for p in parts:
                        if "inlineData" in p:
                            audio_data_b64 = p["inlineData"]["data"]
                            audio_bytes = base64.b64decode(audio_data_b64)
                            await self.audio_queue.put(audio_bytes)
                        elif "text" in p:
                            print("Gemini text response:", p["text"])
                except KeyError:
                    pass

                try:
                    if response["serverContent"].get("turnComplete"):
                        while not self.audio_queue.empty():
                            await self.audio_queue.get()
                except KeyError:
                    pass
                    
            except json.JSONDecodeError as e:
                print(f"Error decoding server message: {e}")
            except Exception as e:
                print(f"Error processing server message: {e}")

    async def play_responses(self):
        """Play audio responses from Gemini"""
        audio = pyaudio.PyAudio()
        stream = None
        try:
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.OUTPUT_RATE,
                output=True
            )

            while self.running:
                try:
                    audio_chunk = await self.audio_queue.get()
                    self.is_playing = True
                    await asyncio.to_thread(stream.write, audio_chunk)
                    self.is_playing = False
                except Exception as e:
                    print(f"Error playing audio: {e}")
                    await asyncio.sleep(0.1)
                    
        except CancelledError:
            print("Playback cancelled")
        except Exception as e:
            print(f"Unexpected error in play_responses: {e}")
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
            try:
                audio.terminate()
            except:
                pass

    async def watch_cleanup(self):
        """Watch for cleanup event"""
        while self.running:
            if self.cleanup_event and self.cleanup_event.is_set():
                self.running = False
                break
            await asyncio.sleep(0.1)
