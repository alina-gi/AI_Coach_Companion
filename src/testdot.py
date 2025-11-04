from response_engine import ResponseEngine

print("\n--- 🧠 Testing Response Engine Core Logic ---")

# Initialize in LOCAL mode
engine = ResponseEngine(mode="local")

# 1️⃣ Test mood detection
print("\n[Mood Detection Tests]")
print("Positive:", engine.detect_mood("I’m so happy today!"))
print("Negative:", engine.detect_mood("This is really frustrating."))
print("Neutral:", engine.detect_mood("It’s just another normal day."))

# 2️⃣ Test local response generation with different tones
print("\n[Response Generation Tests]")
for tone in ["Blunt", "Empathetic", "Balanced"]:
    print(f"\nTone: {tone}")
    response = engine.generate_local_response("I feel tired but want to keep going.", tone)
    print("Response:", response)

# 3️⃣ Test OpenAI connection (optional)
print("\n[API Connection Test]")
print("OpenAI test:", engine.test_openai_connection("Hello from DotPi test!"))

print("\n✅ If no errors appeared above — your ResponseEngine is functioning smoothly.")
