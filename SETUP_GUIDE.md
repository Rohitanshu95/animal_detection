# Quick Setup Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
# Make sure you're in the project root
cd f:\Temp\animal_detection

# Activate virtual environment
.venv\Scripts\Activate

# Install new packages
uv pip install langgraph langchain langchain-google-genai langchain-community python-dateutil
```

### 2. Verify Environment Variables
Check that your `.env` file has:
```
GOOGLE_API_KEY=your_api_key_here
MONGODB_URL=your_mongodb_url_here
```

### 3. Start Backend
```bash
# Terminal 1
cd backend
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Google Generative AI configured
✅ Using new google-genai package
```

### 4. Start Frontend
```bash
# Terminal 2
cd frontend
streamlit run app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 5. Test the Features

#### Test Excel Upload:
1. Navigate to "Upload" in the sidebar
2. Upload an Excel file
3. Click "Parse Excel"
4. Review the parsed data
5. Click "Enrich with AI"
6. Select incidents and upload

#### Test AI Assistant:
1. Navigate to "Assistant" in the sidebar
2. Try example questions from sidebar:
   - "What are the most common types of wildlife being smuggled?"
   - "Show me incidents from the last 30 days"
3. Type your own questions
4. Toggle "Show tool usage" to see how the agent works

## ⚠️ Troubleshooting

### If Backend Fails:
- Check MongoDB is running
- Verify GOOGLE_API_KEY is set
- Check no other process is using port 8000

### If Frontend Fails:
- Verify backend is running on port 8000
- Check streamlit is installed
- Clear browser cache if pages don't load

### If Excel Upload Fails:
- Ensure Excel file has the expected format
- Check backend logs for parsing errors
- Verify enrichment agent has API access

### If Assistant Doesn't Respond:
- Check backend endpoint `/assistant/chat` is accessible
- Verify LangChain packages are installed
- Check GOOGLE_API_KEY is valid
- Look for errors in backend terminal

## 📊 Sample Excel Format

```
n°1 / 1st April - 30th June 2013

Date         Division      Page    Description
08.01.2013   Mumbai       5       Ivory tusks seized at port
January 2013 Delhi        12      Pangolin scales found in cargo
```

The system will:
- Extract the quarterly header
- Parse each incident row
- Clean dates and validate data
- Enrich with AI (animals, quantities, etc.)

## 🎯 Quick Commands

### Install all dependencies at once:
```bash
uv pip install -r requirements.txt
```

### Check if everything is installed:
```bash
uv pip list | grep -E "langgraph|langchain|streamlit|fastapi"
```

### Restart both services:
```bash
# Stop both terminals (Ctrl+C)
# Then restart as shown in steps 3-4
```

## ✅ Success Indicators

Backend is working if you see:
- ✅ Google Generative AI configured
- ✅ Using new google-genai package
- INFO: Application startup complete

Frontend is working if:
- Sidebar shows all navigation options
- "Upload" and "Assistant" are clickable
- No error messages on page load

Both features working if:
- Excel upload shows parsing results
- Assistant responds to questions
- Tool usage is visible (when enabled)

## 🔍 Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can navigate to Upload page
- [ ] Can upload Excel file
- [ ] Excel parsing works
- [ ] AI enrichment works
- [ ] Can upload to database
- [ ] Can navigate to Assistant page
- [ ] Assistant responds to questions
- [ ] Tool calls are shown (when enabled)
- [ ] Can view tool execution details

## 📞 Need Help?

Common issues:
1. **ModuleNotFoundError:** Run `uv pip install -r requirements.txt`
2. **API Key errors:** Check `.env` file has correct `GOOGLE_API_KEY`
3. **Port already in use:** Kill process on port 8000/8501 or use different ports
4. **Database connection:** Verify MongoDB is running and URL is correct

Happy tracking! 🦁
