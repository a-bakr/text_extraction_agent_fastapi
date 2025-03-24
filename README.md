# Text Extraction Agent FastAPI App

A FastAPI web application that uses AI to extract text from images and answers questions about the content.

## Features

- Upload images and extract text using AI models
- Ask questions about the image content
- Modern and responsive UI
- Easy to use interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables by copying the example file and modifying as needed:
```bash
cp .env.example .env
```

Edit the `.env` file to include your API keys and configuration.

## Running the Application

To start the FastAPI server:

```bash
python app.py
```

The application will be available at [http://localhost:8002](http://localhost:8002)

## Usage

1. Open the application in your web browser
2. Upload an image using the file input
3. Write a prompt about what information you want to extract from the image
4. Click "Analyze Image" to process the image
5. View the extracted text and AI-generated response on the results page

## Technologies Used

- FastAPI
- Jinja2 Templates
- LangChain
- OpenAI and Google AI models for image text extraction
- Bootstrap for responsive UI

## Deployment to Vercel

This application is ready to be deployed to Vercel. Follow these steps:

1. Install the Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy the application:
```bash
vercel
```

4. For production deployment:
```bash
vercel --prod
```

### Environment Variables

Make sure to configure the following environment variables in your Vercel project settings:

- `OPENAI_API_KEY` - Your OpenAI API key
- `GOOGLE_API_KEY` - Your Google API key (if using Google AI models)

### Limitations

When deployed to Vercel, the application runs in a serverless environment, which has the following limitations:

- The `/tmp` directory should be used for temporary file storage instead of local app directories
- Maximum execution time is 10-60 seconds depending on your plan
- Maximum payload size is 4.5MB
