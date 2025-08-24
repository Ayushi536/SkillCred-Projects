# smoke_test.py — quick import check for google-genai (no billing heavy call)
from google import genai
import google.genai as genai

client = genai.Client(api_key="AIzaSyBdntEUrSONZ3bLyPh7XLSXTp8MgM9ojmM")

print("google-genai import OK")
# client = genai.Client()
print("genai.Client created OK (client will use GEMINI_API_KEY from env if set)")
