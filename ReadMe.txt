# AI Quiz Generator
Author: Alan Jiang  
Year: Freshman  
Major: Computer Science  

Project Overview
AI Quiz Generator is a web application that converts text or PDF documents into interactive multiple-choice quizzes using a local AI model. The goal of this project is to make studying faster and more efficient by automatically generating practice questions from notes or readings.

Project Video
Watch the full walkthrough here:  
https://your-video-link-here

GitHub Repository
https://github.com/Someone041/Cs50-Final-project

Features
- Upload PDFs or paste text to generate quizzes  
- Automatically creates multiple-choice questions  
- Includes correct answers and explanations  
- Interactive quiz interface  
- Tracks progress with XP, levels, and streaks  

Technologies Used
- Backend: Flask (Python)  
- Frontend: HTML  
- AI Model: Local model via Ollama  

Challenges & Solutions
One of the biggest challenges was getting the AI model to consistently return properly formatted JSON. Sometimes the output was incomplete or incorrectly structured, which caused errors in the app.

To solve this, I improved the prompt design, reduced randomness in the model output, and added validation with retry logic to ensure the data was usable.

I also encountered issues with Python virtual environments and frontend crashes due to missing elements. Debugging these problems helped me better understand how the frontend and backend interact in a full-stack application.

What I Learned
- How to build and connect a full-stack web application  
- How to work with local AI models instead of external APIs  
- How to handle unreliable or inconsistent AI outputs  
- The importance of debugging across multiple parts of a system  

Reflection
This project helped me turn an idea into a functional tool that can improve studying. I enjoyed building something practical that transforms notes into interactive learning material, and it showed me how AI can be applied in everyday use cases.
