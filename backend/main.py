#AIzaSyBI5Yb6mGXg_1nmhErVnKaL2frY5DEyEo4

# import os
# import json
# import pandas as pd
# import io
# import plotly.express as px
# import plotly.graph_objects as go
# import matplotlib.pyplot as plt
# import seaborn as sns
# import base64
# from pathlib import Path
# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import uvicorn
# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.metrics import accuracy_score, confusion_matrix
# import uuid

# # --- CORRECT Gemini Import ---
# import google.generativeai as genai

# # --- API KEY SETUP ---
# API_KEY = "AIzaSyBI5Yb6mGXg_1nmhErVnKaL2frY5DEyEo4"  # Replace with your actual Google API key

# if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
#     print("=" * 70)
#     print("ERROR: Google API Key is not set!")
#     print("Please replace 'YOUR_API_KEY_HERE' with your actual API key")
#     print("Get your key from: https://aistudio.google.com/app/apikey")
#     print("=" * 70)
#     raise ValueError("Google API Key is required to run this application")

# # Configure Gemini
# genai.configure(api_key=API_KEY)

# # --- Configuration ---
# MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
# ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
# TEMP_DIR = Path("temp_uploads")
# TEMP_DIR.mkdir(exist_ok=True)

# # --- In-memory store for session data ---
# shared_data_store = {}
# session_conversations = {}  # Store conversation history per session

# # --- FastAPI App Initialization ---
# app = FastAPI(title="Autonomous Data Scientist API")

# # --- CORS Middleware ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["Content-Disposition"]
# )

# # --- Pydantic Models ---
# class ChatRequest(BaseModel):
#     message: str
#     session_id: str

# # --- Initialize Gemini Model ---
# try:
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     print("✅ Successfully initialized Gemini 1.5 Flash")
# except Exception as e:
#     print(f"⚠️  Failed to initialize gemini-1.5-flash: {e}")
#     try:
#         model = genai.GenerativeModel('gemini-pro')
#         print("✅ Using Gemini Pro as fallback")
#     except Exception as e2:
#         print(f"❌ Failed to initialize any Gemini model: {e2}")
#         raise

# # --- Agent Functions ---

# def analyze_dataset_schema(dataset_path: str) -> str:
#     """Analyzes the dataset and returns schema information."""
#     print(f"\n>>> Analyzing dataset: {dataset_path}")
#     try:
#         if dataset_path.endswith('.csv'):
#             df = pd.read_csv(dataset_path)
#         else:
#             df = pd.read_excel(dataset_path)
        
#         # Identify potential target columns
#         categorical_info = [
#             f"'{col}'" for col in df.columns 
#             if df[col].dtype in ['int64', 'object'] and df[col].nunique() < 15
#         ]
        
#         # Store data
#         shared_data_store['dataframe'] = df
#         shared_data_store['dataset_path'] = dataset_path
        
#         return (
#             f"✅ Analysis complete! Dataset has {df.shape[0]} rows and {df.shape[1]} columns. "
#             f"Potential target columns: {', '.join(categorical_info) if categorical_info else 'None identified'}."
#         )
#     except Exception as e:
#         return f"❌ Error analyzing dataset: {str(e)}"

# def generate_final_output(output_type: str, target_column: str) -> str:
#     """Generates notebook or dashboard."""
#     print(f"\n>>> Generating {output_type} for target: {target_column}")
    
#     shared_data_store['target_column'] = target_column
    
#     if 'dataframe' not in shared_data_store:
#         return "❌ Error: No dataset found. Please upload a file first."
    
#     output_type_lower = output_type.lower().strip()
    
#     if output_type_lower == 'notebook':
#         file_path = create_general_analysis_notebook()
#         if file_path:
#             shared_data_store['file_to_download'] = file_path
#             return f"✅ Successfully generated Jupyter Notebook! Ready for download."
#         return "❌ Failed to generate notebook."
            
#     elif output_type_lower == 'dashboard':
#         file_path = create_interactive_dashboard()
#         if file_path:
#             shared_data_store['file_to_download'] = file_path
#             return f"✅ Successfully generated interactive dashboard! Ready for download."
#         return "❌ Failed to generate dashboard."
#     else:
#         return f"❌ Invalid output type. Please choose 'notebook' or 'dashboard'."

# # --- Helper Functions (same as before) ---

# def create_general_analysis_notebook():
#     """Helper function to create a complete Jupyter notebook."""
#     try:
#         dataset_path = shared_data_store['dataset_path']
#         target_column = shared_data_store['target_column']
#         df = shared_data_store['dataframe']
        
#         numerical_features = [
#             col for col in df.columns 
#             if col != target_column 
#             and df[col].dtype in ['int64', 'float64'] 
#             and 'id' not in col.lower()
#         ]
#         features_list_str = str(numerical_features)
#         read_function = "pd.read_csv" if str(dataset_path).endswith('.csv') else "pd.read_excel"
#         dataset_path_str = str(Path(dataset_path).resolve()).replace('\\', '/')

#         imports_code = """import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import json
# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.metrics import accuracy_score, confusion_matrix
# print("Libraries imported successfully.")"""

#         load_and_clean_code = f"""# Step 1: Load and Clean Data
# print("Step 1: Loading and Cleaning Data...")
# df = {read_function}('{dataset_path_str}')

# for col in df.select_dtypes(include=['float64', 'int64']).columns:
#     df[col] = df[col].fillna(df[col].median())

# for col in df.select_dtypes(include=['object']).columns:
#     if len(df[col].mode()) > 0:
#         df[col] = df[col].fillna(df[col].mode()[0])

# for col in df.select_dtypes(include=['object']).columns:
#     if df[col].nunique() == 2:
#         df[col], _ = pd.factorize(df[col])

# print("Data loaded and cleaned.")
# df.head()"""

#         feature_engineering_code = """# Step 2: Feature Engineering
# print("\\nStep 2: Engineering New Features...")

# if 'SibSp' in df.columns and 'Parch' in df.columns:
#     df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
#     df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
#     print("Created 'FamilySize' and 'IsAlone' features.")

# if 'Name' in df.columns:
#     df['Title'] = df['Name'].str.extract(r' ([A-Za-z]+)\\.', expand=False)
#     df['Title'] = df['Title'].replace(['Lady', 'Countess','Capt', 'Col','Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
#     df['Title'] = df['Title'].replace(['Mlle', 'Ms'], 'Miss')
#     df['Title'] = df['Title'].replace('Mme', 'Mrs')
#     title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
#     df['Title'] = df['Title'].map(title_mapping).fillna(0)
#     print("Created 'Title' feature.")

# print("Feature engineering complete.")"""

#         model_evaluation_code = f"""# Step 3: Compare Base Models
# print("\\nStep 3: Comparing Base Models...")

# features_list = {features_list_str}
# if 'FamilySize' in df.columns:
#     features_list.extend(['FamilySize', 'IsAlone'])
# if 'Title' in df.columns:
#     features_list.append('Title')

# target = '{target_column}'
# X = df[[f for f in features_list if f in df.columns]]
# y = df[target]

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# print("Training RandomForest...")
# rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
# rf_model.fit(X_train, y_train)
# rf_preds = rf_model.predict(X_test)
# rf_accuracy = accuracy_score(y_test, rf_preds)
# print(f"RandomForest Base Accuracy: {{rf_accuracy:.4f}}")

# print("Training LogisticRegression...")
# lr_model = LogisticRegression(random_state=42, max_iter=1000)
# lr_model.fit(X_train, y_train)
# lr_preds = lr_model.predict(X_test)
# lr_accuracy = accuracy_score(y_test, lr_preds)
# print(f"LogisticRegression Base Accuracy: {{lr_accuracy:.4f}}")"""

#         hyperparameter_tuning_code = """# Step 4: Tune the Best Model
# print("\\nStep 4: Tuning RandomForest Hyperparameters...")

# param_grid = {
#     'n_estimators': [50, 100, 200],
#     'max_depth': [None, 10, 20],
#     'min_samples_leaf': [1, 2, 4]
# }

# model = RandomForestClassifier(random_state=42)
# grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, verbose=1)
# grid_search.fit(X, y)

# best_params = grid_search.best_params_
# print(f"Best parameters: {best_params}")
# print(f"Best CV accuracy: {grid_search.best_score_:.4f}")"""

#         visualization_code = f"""# Step 5: Final Visualization
# print("\\nStep 5: Generating Final Visualization...")

# final_model = RandomForestClassifier(random_state=42, **best_params)
# final_model.fit(X_train, y_train)
# final_preds = final_model.predict(X_test)
# final_accuracy = accuracy_score(y_test, final_preds)

# print(f"\\n{{'='*50}}")
# print("KEY INSIGHTS")
# print(f"{{'='*50}}")
# print(f"Final accuracy: {{{{final_accuracy:.4f}}}}")
# print(f"Predicting '{target_column}' with {{{{final_accuracy*100:.2f}}}}% accuracy")
# print(f"{{'='*50}}")

# cm = confusion_matrix(y_test, final_preds)
# plt.figure(figsize=(8, 6))
# sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
# plt.xlabel('Predicted')
# plt.ylabel('Actual')
# plt.title('Confusion Matrix')
# plt.show()

# print("\\nAnalysis complete!")"""

#         notebook_filename = f"{os.path.basename(dataset_path).split('.')[0]}_notebook_for_{target_column}.ipynb"
#         notebook_content = {
#             "cells": [
#                 {"cell_type": "markdown", "metadata": {}, "source": [f"# Analysis for {os.path.basename(dataset_path)}\n## Predicting '{target_column}'"]},
#                 {"cell_type": "code", "source": imports_code, "execution_count": None, "outputs": [], "metadata": {}},
#                 {"cell_type": "code", "source": load_and_clean_code, "execution_count": None, "outputs": [], "metadata": {}},
#                 {"cell_type": "code", "source": feature_engineering_code, "execution_count": None, "outputs": [], "metadata": {}},
#                 {"cell_type": "code", "source": model_evaluation_code, "execution_count": None, "outputs": [], "metadata": {}},
#                 {"cell_type": "code", "source": hyperparameter_tuning_code, "execution_count": None, "outputs": [], "metadata": {}},
#                 {"cell_type": "code", "source": visualization_code, "execution_count": None, "outputs": [], "metadata": {}},
#             ],
#             "metadata": {"language_info": {"name": "python", "version": "3.10"}},
#             "nbformat": 4,
#             "nbformat_minor": 4
#         }
        
#         with open(notebook_filename, 'w') as f:
#             json.dump(notebook_content, f, indent=4)
        
#         print(f"✅ Notebook created: {notebook_filename}")
#         return notebook_filename
        
#     except Exception as e:
#         print(f"❌ Error creating notebook: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

# def create_interactive_dashboard():
#     """Generates HTML dashboard."""
#     try:
#         df = shared_data_store['dataframe']
#         target_column = shared_data_store['target_column']
#         dataset_path = shared_data_store['dataset_path']
        
#         kpi_total_rows = df.shape[0]
#         numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
#         insights = []
#         insights.append(f"The dataset contains <strong>{kpi_total_rows:,}</strong> rows and <strong>{df.shape[1]}</strong> columns.")
#         insights.append(f"The target variable, <strong>'{target_column}'</strong>, has <strong>{df[target_column].nunique()}</strong> unique classes.")
        
#         if target_column in numeric_df.columns and len(numeric_df.columns) > 1:
#             correlations = numeric_df.corr(numeric_only=True)[target_column].abs().sort_values(ascending=False)
#             top_corr_feature = correlations.index[1] if len(correlations) > 1 else "N/A"
#             insights.append(f"The feature most correlated with '{target_column}' is <strong>'{top_corr_feature}'</strong>.")

#         dist_fig = px.histogram(df, x=target_column, title=f'Distribution of Target: {target_column}', 
#                                 color=target_column, color_discrete_sequence=px.colors.qualitative.Prism)
#         dist_fig.update_layout(showlegend=False, title_x=0.5)

#         heatmap_html = ""
#         if len(numeric_df.columns) > 1:
#             plt.figure(figsize=(10, 8))
#             corr = numeric_df.corr(numeric_only=True)
#             sns.heatmap(corr, annot=True, cmap='viridis', fmt='.2f')
#             plt.title('Correlation Heatmap of Numeric Features', pad=20)
            
#             buf = io.BytesIO()
#             plt.savefig(buf, format='png', bbox_inches='tight')
#             buf.seek(0)
#             img_b64 = base64.b64encode(buf.read()).decode('utf-8')
#             plt.close()
#             heatmap_html = f'<img src="data:image/png;base64,{img_b64}" alt="Correlation Heatmap" class="w-full h-full object-contain">'
#         else:
#             heatmap_html = '<div class="text-center p-8"><h3 class="text-lg font-semibold text-gray-600">Not enough numeric data for heatmap.</h3></div>'
        
#         adaptive_fig = None
#         if len(numeric_df.columns) > 0:
#             key_numeric_1 = numeric_df.columns[0]
#             chart_type = 'violin' if len(df) > 150 else 'box'
            
#             if chart_type == 'violin':
#                 adaptive_fig = px.violin(df, x=target_column, y=key_numeric_1, color=target_column, 
#                                    title=f'{key_numeric_1} Distribution by {target_column} (Violin Plot)',
#                                    box=True, points="all", color_discrete_sequence=px.colors.qualitative.Pastel)
#             else:
#                 adaptive_fig = px.box(df, x=target_column, y=key_numeric_1, color=target_column, 
#                                title=f'{key_numeric_1} Distribution by {target_column} (Box Plot)',
#                                color_discrete_sequence=px.colors.qualitative.Pastel)
#             adaptive_fig.update_layout(showlegend=False, title_x=0.5)
        
#         dashboard_filename = f"{os.path.basename(dataset_path).split('.')[0]}_dashboard_for_{target_column}.html"
        
#         with open(dashboard_filename, 'w', encoding='utf-8') as f:
#             f.write('<!DOCTYPE html><html><head>')
#             f.write('<script src="https://cdn.tailwindcss.com"></script>')
#             f.write('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
#             f.write('<title>AI Data Scientist Dashboard</title></head>')
#             f.write('<body class="bg-slate-100 p-6 md:p-10 font-sans"><div class="max-w-7xl mx-auto">')
#             f.write('<h1 class="text-5xl font-bold text-slate-800 mb-2">Data Science Insights</h1>')
#             f.write(f'<h2 class="text-xl text-slate-600 mb-10">Analysis of <span class="font-semibold text-indigo-600">{os.path.basename(dataset_path)}</span> Targeting <span class="font-semibold text-indigo-600">{target_column}</span></h2>')
#             f.write('<div class="bg-white p-6 rounded-xl shadow-lg mb-8 border-l-4 border-indigo-500">')
#             f.write('<h3 class="text-2xl font-bold text-gray-800 mb-3">Key Insights</h3>')
#             f.write('<ul class="list-disc list-inside text-gray-700 space-y-2">')
#             for insight in insights:
#                 f.write(f'<li>{insight}</li>')
#             f.write('</ul></div>')
#             f.write('<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">')
#             if dist_fig:
#                 f.write(f'<div class="bg-white p-4 rounded-xl shadow-lg">{dist_fig.to_html(full_html=False, include_plotlyjs=False)}</div>')
#             f.write(f'<div class="bg-white p-4 rounded-xl shadow-lg flex items-center justify-center">{heatmap_html}</div>')
#             if adaptive_fig:
#                 f.write(f'<div class="lg:col-span-2 bg-white p-4 rounded-xl shadow-lg">{adaptive_fig.to_html(full_html=False, include_plotlyjs=False)}</div>')
#             f.write('</div></div></body></html>')
            
#         print(f"✅ Dashboard created: {dashboard_filename}")
#         return dashboard_filename
        
#     except Exception as e:
#         print(f"❌ Error creating dashboard: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

# # --- Conversational Agent Logic ---

# def get_agent_response(session_id: str, user_message: str) -> str:
#     """Handles conversation flow using Gemini."""
    
#     # Initialize conversation history for new session
#     if session_id not in session_conversations:
#         session_conversations[session_id] = {
#             'history': [],
#             'state': 'initial',  # initial, analyzed, target_set, output_chosen
#             'target_column': None
#         }
    
#     session = session_conversations[session_id]
    
#     # Build conversation context
#     conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in session['history']])
    
#     # Determine what to do based on state
#     if session['state'] == 'initial':
#         # First interaction - analyze the dataset
#         dataset_path = shared_data_store.get('dataset_path')
#         if dataset_path:
#             analysis_result = analyze_dataset_schema(dataset_path)
#             session['state'] = 'analyzed'
#             session['history'].append({'role': 'assistant', 'content': analysis_result})
            
#             # Ask for target column
#             follow_up = "\n\nWhich column would you like to predict (target variable)? Please tell me the column name."
#             full_response = analysis_result + follow_up
#             session['history'].append({'role': 'assistant', 'content': follow_up})
#             return full_response
#         return "Please upload a dataset first."
    
#     elif session['state'] == 'analyzed':
#         # User should be specifying target column
#         session['history'].append({'role': 'user', 'content': user_message})
        
#         # Extract target column from user message
#         df = shared_data_store.get('dataframe')
#         if df is not None:
#             # Find if any column name is mentioned in the message
#             user_message_lower = user_message.lower()
#             matched_column = None
            
#             for col in df.columns:
#                 if col.lower() in user_message_lower:
#                     matched_column = col
#                     break
            
#             if matched_column:
#                 session['target_column'] = matched_column
#                 session['state'] = 'target_set'
#                 response = f"Great! I'll help you predict '{matched_column}'. Would you like me to generate a 'notebook' or a 'dashboard'? Please choose one."
#                 session['history'].append({'role': 'assistant', 'content': response})
#                 return response
#             else:
#                 response = f"I couldn't find that column. Available columns are: {', '.join(df.columns)}. Which one would you like to predict?"
#                 session['history'].append({'role': 'assistant', 'content': response})
#                 return response
        
#     elif session['state'] == 'target_set':
#         # User should be choosing output type
#         session['history'].append({'role': 'user', 'content': user_message})
        
#         user_message_lower = user_message.lower()
#         if 'notebook' in user_message_lower:
#             output_type = 'notebook'
#         elif 'dashboard' in user_message_lower:
#             output_type = 'dashboard'
#         else:
#             response = "Please choose either 'notebook' or 'dashboard' for your output."
#             session['history'].append({'role': 'assistant', 'content': response})
#             return response
        
#         # Generate the output
#         result = generate_final_output(output_type, session['target_column'])
#         session['state'] = 'completed'
#         session['history'].append({'role': 'assistant', 'content': result})
#         return result
    
#     elif session['state'] == 'completed':
#         return "Your analysis is complete! You can download the file using the download button above. Would you like to start a new analysis?"
    
#     # Fallback
#     return "I'm not sure what you mean. Could you please clarify?"

# # --- API ENDPOINTS ---

# @app.post("/api/upload")
# async def upload_file(
#     session_id: str = Form(default_factory=lambda: str(uuid.uuid4())), 
#     file: UploadFile = File(...)
# ):
#     """Receives uploaded file and starts analysis."""
#     try:
#         file_ext = Path(file.filename).suffix.lower()
#         if file_ext not in ALLOWED_EXTENSIONS:
#             return JSONResponse(status_code=400, content={"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"})
        
#         contents = await file.read()
#         if len(contents) > MAX_FILE_SIZE:
#             return JSONResponse(status_code=400, content={"error": f"File too large. Max: {MAX_FILE_SIZE/(1024*1024):.0f}MB"})
        
#         dataset_path = TEMP_DIR / f"{session_id}_{file.filename}"
#         with open(dataset_path, "wb") as buffer:
#             buffer.write(contents)
        
#         shared_data_store[f'{session_id}_file'] = str(dataset_path)
#         shared_data_store['dataset_path'] = str(dataset_path)
        
#         # Get initial response
#         response = get_agent_response(session_id, "File uploaded")
        
#         return {"session_id": session_id, "agent_response": response}
        
#     except Exception as e:
#         print(f"Upload error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return JSONResponse(status_code=500, content={"error": f"Upload failed: {str(e)}"})


# @app.post("/api/chat")
# async def chat(request: ChatRequest):
#     """Handles conversation."""
#     try:
#         response = get_agent_response(request.session_id, request.message)
        
#         # Check if file is ready for download
#         if "Successfully generated" in response and shared_data_store.get('file_to_download'):
#             file_path = shared_data_store.pop('file_to_download')
            
#             if os.path.exists(file_path):
#                 return FileResponse(path=file_path, media_type='application/octet-stream', filename=os.path.basename(file_path))
        
#         return {"agent_response": response}
        
#     except Exception as e:
#         print(f"Chat error: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return JSONResponse(status_code=500, content={"error": f"Chat failed: {str(e)}"})


# @app.delete("/api/session/{session_id}")
# async def cleanup_session(session_id: str):
#     """Cleans up session data."""
#     try:
#         if f'{session_id}_file' in shared_data_store:
#             file_path = Path(shared_data_store[f'{session_id}_file'])
#             if file_path.exists():
#                 file_path.unlink()
#                 print(f"Deleted file: {file_path}")
        
#         if session_id in session_conversations:
#             del session_conversations[session_id]
#             print(f"Cleared session: {session_id}")
        
#         keys_to_remove = [k for k in shared_data_store.keys() if session_id in str(k)]
#         for key in keys_to_remove:
#             del shared_data_store[key]
        
#         return {"status": "Session cleaned up successfully"}
        
#     except Exception as e:
#         print(f"Cleanup error: {str(e)}")
#         return JSONResponse(status_code=500, content={"error": str(e)})


# @app.get("/")
# async def root():
#     """Health check."""
#     return {
#         "status": "running",
#         "message": "Autonomous Data Scientist API",
#         "endpoints": {
#             "upload": "/api/upload",
#             "chat": "/api/chat",
#             "cleanup": "/api/session/{session_id}"
#         }
#     }


# if __name__ == "__main__":
#     print("=" * 70)
#     print("Starting Autonomous Data Scientist API")
#     print("=" * 70)
#     print(f"API: http://localhost:8000")
#     print(f"Docs: http://localhost:8000/docs")
#     print("=" * 70)
    
#     uvicorn.run(app, host="0.0.0.0", port=8000)

import os
import json
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import uvicorn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score, precision_score, recall_score
from xgboost import XGBClassifier
import uuid
from datetime import datetime
import asyncio
from typing import Optional
import google.generativeai as genai

# --- API KEY SETUP ---
API_KEY = "AIzaSyBI5Yb6mGXg_1nmhErVnKaL2frY5DEyEo4"

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    print("=" * 70)
    print("ERROR: Google API Key is not set!")
    print("Please replace with your actual API key")
    print("=" * 70)
    raise ValueError("Google API Key is required")

genai.configure(api_key=API_KEY)

# --- Configuration ---
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)

shared_data_store = {}
session_conversations = {}
progress_store = {}  # Store progress updates for each session

app = FastAPI(title="Autonomous Data Scientist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

class AnalysisRequest(BaseModel):
    session_id: str

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Successfully initialized Gemini 1.5 Flash")
except Exception as e:
    print(f"⚠️  Failed to initialize gemini-1.5-flash: {e}")
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("✅ Using Gemini 1.5 Pro as fallback")
    except Exception as e2:
        print(f"❌ Failed to initialize any Gemini model: {e2}")
        raise

def update_progress(session_id: str, step: str, percentage: int, message: str):
    """Update progress for a session"""
    progress_store[session_id] = {
        'step': step,
        'percentage': percentage,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    print(f"📊 Progress [{session_id[:8]}]: {percentage}% - {message}")

def get_smart_suggestions(df, target_column=None):
    suggestions = []
    col_names_lower = [col.lower() for col in df.columns]
    
    if any('survived' in col for col in col_names_lower):
        suggestions.append("💡 I notice a 'survived' column - perfect for survival prediction!")
    if any('price' in col or 'cost' in col or 'amount' in col for col in col_names_lower):
        suggestions.append("💰 I see price/cost data - great for regression analysis!")
    if any('date' in col or 'time' in col for col in col_names_lower):
        suggestions.append("📅 Time-based columns detected - we can do temporal analysis!")
    if any('age' in col for col in col_names_lower):
        suggestions.append("🔧 I can create age groups and bins for better insights!")
    
    missing_pct = (df.isnull().sum() / len(df) * 100).max()
    if missing_pct > 20:
        suggestions.append(f"⚠️ Some columns have {missing_pct:.1f}% missing data - I'll handle this!")
    
    return suggestions

def analyze_dataset_schema(dataset_path: str, session_id: str) -> dict:
    print(f"\n>>> Analyzing dataset: {dataset_path}")
    try:
        if dataset_path.endswith('.csv'):
            df = pd.read_csv(dataset_path)
        else:
            df = pd.read_excel(dataset_path)
        
        n_rows, n_cols = df.shape
        
        categorical_cols = [
            col for col in df.columns 
            if df[col].dtype in ['int64', 'object'] and df[col].nunique() < 15 and df[col].nunique() > 1
        ]
        
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        missing_data = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()
        suggestions = get_smart_suggestions(df)
        
        shared_data_store[f'{session_id}_dataframe'] = df
        shared_data_store[f'{session_id}_dataset_path'] = dataset_path
        
        preview_data = df.head(5).to_dict('records')
        
        return {
            "success": True,
            "stats": {
                "rows": n_rows,
                "columns": n_cols,
                "numerical_features": len(numerical_cols),
                "categorical_features": len(categorical_cols),
                "missing_values": int(missing_data),
                "duplicate_rows": int(duplicate_rows)
            },
            "potential_targets": categorical_cols,
            "columns": df.columns.tolist(),
            "suggestions": suggestions,
            "preview": preview_data,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    except Exception as e:
        print(f"Error in analyze_dataset_schema: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def compare_models(df, target_column, features, session_id=None):
    """Compare multiple ML models and return performance metrics"""
    try:
        import warnings
        warnings.filterwarnings('ignore')
        
        if session_id:
            update_progress(session_id, 'comparing', 20, '🤖 Comparing multiple models...')
        
        X = df[features]
        y = df[target_column]
        X = X.fillna(X.median())
        
        # Check minimum data requirements
        if len(X) < 10:
            raise ValueError(f"Dataset too small ({len(X)} samples). Need at least 10 samples for model comparison.")
        
        # Encode target if it's categorical (string labels)
        from sklearn.preprocessing import LabelEncoder
        label_encoder = None
        if y.dtype == 'object' or y.dtype.name == 'category':
            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(y)
            print(f"Encoded target labels: {label_encoder.classes_}")
        
        # Check if we can use stratify (need at least 2 samples per class)
        from collections import Counter
        class_counts = Counter(y)
        min_class_count = min(class_counts.values())
        
        # Use stratify only if all classes have at least 2 samples
        if min_class_count >= 2:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            print(f"Using stratified split (min class count: {min_class_count})")
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            print(f"Using regular split (min class count: {min_class_count} - too small for stratification)")
        
        # Define models to compare (optimized for speed and performance)
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10, n_jobs=-1),
            'XGBoost': XGBClassifier(n_estimators=100, random_state=42, max_depth=6, learning_rate=0.1, eval_metric='logloss', verbosity=0),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5),
            'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=10),
            'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
        }
        
        results = []
        best_model = None
        best_accuracy = 0
        
        for idx, (name, model) in enumerate(models.items()):
            try:
                if session_id:
                    progress = 20 + (idx + 1) * 8  # Progress from 20% to 68%
                    update_progress(session_id, 'training', progress, f'🔧 Training {name}...')
                
                print(f"Training {name}...")
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                
                # Cross-validation score (use min of 3-fold or n_samples/2)
                n_splits = min(3, len(X_train) // 2, min_class_count)
                if n_splits >= 2:
                    cv_scores = cross_val_score(model, X_train, y_train, cv=n_splits, scoring='accuracy')
                    cv_mean = cv_scores.mean()
                else:
                    cv_mean = accuracy  # Use test accuracy if CV not possible
                
                results.append({
                    'name': name,
                    'accuracy': float(round(accuracy * 100, 2)),
                    'precision': float(round(precision * 100, 2)),
                    'recall': float(round(recall * 100, 2)),
                    'f1_score': float(round(f1 * 100, 2)),
                    'cv_score': float(round(cv_mean * 100, 2))
                })
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model = {'name': name, 'accuracy': accuracy}
                
                print(f"  ✓ {name}: {accuracy*100:.2f}% accuracy")
                
            except Exception as e:
                print(f"  ✗ {name} failed: {e}")
                results.append({
                    'name': name,
                    'accuracy': 0.0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'f1_score': 0.0,
                    'cv_score': 0.0,
                    'error': str(e)
                })
        
        # Sort by accuracy
        results.sort(key=lambda x: x['accuracy'], reverse=True)
        
        # Get feature importance from best model (retrain it quickly)
        top_features = []
        if best_model:
            try:
                best_model_obj = models[best_model['name']]
                best_model_obj.fit(X_train, y_train)
                if hasattr(best_model_obj, 'feature_importances_'):
                    feature_importance = dict(zip(features, best_model_obj.feature_importances_))
                    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
                    top_features = [{"name": name, "importance": float(round(imp * 100, 2))} for name, imp in top_features]
            except Exception as e:
                print(f"Could not extract feature importance: {e}")
        
        if session_id:
            update_progress(session_id, 'analyzed', 70, '✅ Model comparison complete!')
        
        return {
            "models": results,
            "best_model": best_model['name'] if best_model else None,
            "best_accuracy": float(round(best_accuracy * 100, 2)),
            "n_classes": int(df[target_column].nunique()),
            "top_features": top_features,
            "sample_size": int(len(df))
        }
        
    except Exception as e:
        print(f"Error in model comparison: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_model_preview(df, target_column, features):
    """Quick preview with single model for faster response"""
    try:
        X = df[features]
        y = df[target_column]
        X = X.fillna(X.median())
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        rf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        feature_importance = dict(zip(features, rf.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "accuracy": round(accuracy * 100, 2),
            "n_classes": int(df[target_column].nunique()),
            "top_features": [{"name": name, "importance": round(imp * 100, 2)} for name, imp in top_features],
            "sample_size": len(df)
        }
    except Exception as e:
        print(f"Error calculating preview: {e}")
        return None

def get_agent_response(session_id: str, user_message: str) -> dict:
    print(f"\n🤖 get_agent_response called")
    print(f"   Session ID: {session_id}")
    print(f"   Message: {user_message}")
    
    if session_id not in session_conversations:
        print(f"   ⚠️  Session not found, creating new one")
        session_conversations[session_id] = {
            'history': [],
            'state': 'initial',
            'target_column': None,
            'output_type': None
        }
    
    session = session_conversations[session_id]
    print(f"   Current state: {session['state']}")
    
    if session['state'] == 'initial':
        print(f"   🔍 Looking for dataset_path with key: {session_id}_dataset_path")
        print(f"   📚 Keys in shared_data_store: {list(shared_data_store.keys())}")
        dataset_path = shared_data_store.get(f'{session_id}_dataset_path')
        print(f"   📂 Dataset path found: {dataset_path}")
        
        if dataset_path:
            analysis_result = analyze_dataset_schema(dataset_path, session_id)
            
            if analysis_result['success']:
                session['state'] = 'analyzed'
                session['analysis'] = analysis_result
                
                response_text = f"✅ **Analysis Complete!**\n\n"
                response_text += f"📊 Your dataset has **{analysis_result['stats']['rows']:,}** rows and **{analysis_result['stats']['columns']}** columns.\n\n"
                
                if analysis_result['suggestions']:
                    response_text += "**Smart Insights:**\n"
                    for suggestion in analysis_result['suggestions']:
                        response_text += f"- {suggestion}\n"
                    response_text += "\n"
                
                if analysis_result['potential_targets']:
                    response_text += f"**Recommended target columns:** {', '.join(analysis_result['potential_targets'][:5])}\n\n"
                
                response_text += "Which column would you like to predict? (Please type the column name)"
                session['history'].append({'role': 'assistant', 'content': response_text})
                
                return {
                    "response": response_text,
                    "state": "analyzed",
                    "analysis": analysis_result
                }
            else:
                return {
                    "response": f"❌ Error analyzing dataset: {analysis_result['error']}",
                    "state": "error"
                }
        return {"response": "Please upload a dataset first.", "state": "initial"}
    
    elif session['state'] == 'analyzed':
        session['history'].append({'role': 'user', 'content': user_message})
        df = shared_data_store.get(f'{session_id}_dataframe')
        
        if df is not None:
            user_message_lower = user_message.lower().strip()
            matched_column = None
            
            for col in df.columns:
                if col.lower() == user_message_lower or col.lower() in user_message_lower:
                    matched_column = col
                    break
            
            if matched_column:
                session['target_column'] = matched_column
                session['state'] = 'target_set'
                
                numerical_features = [
                    col for col in df.columns 
                    if col != matched_column 
                    and df[col].dtype in ['int64', 'float64']
                    and 'id' not in col.lower()
                ][:10]
                
                preview = calculate_model_preview(df, matched_column, numerical_features)
                session['preview'] = preview
                
                response = f"Perfect! I'll help you predict **'{matched_column}'**.\n\n"
                
                if preview:
                    response += f"📈 **Quick Preview:**\n"
                    response += f"- Estimated Accuracy: **{preview['accuracy']}%**\n"
                    response += f"- Number of Classes: **{preview['n_classes']}**\n"
                    response += f"- Sample Size: **{preview['sample_size']:,}** rows\n\n"
                    response += "**Top Important Features:**\n"
                    for feat in preview['top_features'][:3]:
                        response += f"- {feat['name']} ({feat['importance']}%)\n"
                    response += "\n"
                
                response += "What would you like me to generate?\n"
                response += "Type **'notebook'** for Jupyter Notebook or **'dashboard'** for Interactive HTML Dashboard"
                
                session['history'].append({'role': 'assistant', 'content': response})
                
                return {
                    "response": response,
                    "state": "target_set",
                    "preview": preview,
                    "choices": ["notebook", "dashboard"]
                }
            else:
                available_cols = ", ".join(df.columns.tolist()[:10])
                if len(df.columns) > 10:
                    available_cols += f", ... and {len(df.columns) - 10} more"
                
                response = f"❌ I couldn't find that column.\n\n**Available columns:** {available_cols}\n\nWhich one would you like to predict?"
                session['history'].append({'role': 'assistant', 'content': response})
                
                return {"response": response, "state": "analyzed"}
    
    elif session['state'] == 'target_set':
        session['history'].append({'role': 'user', 'content': user_message})
        user_message_lower = user_message.lower().strip()
        
        if 'notebook' in user_message_lower:
            session['output_type'] = 'notebook'
            session['state'] = 'generating'
            return {
                "response": "🚀 Generating your Jupyter Notebook... This will take a moment!",
                "state": "generating",
                "output_type": "notebook"
            }
        elif 'dashboard' in user_message_lower:
            session['output_type'] = 'dashboard'
            session['state'] = 'generating'
            return {
                "response": "🚀 Creating your Interactive Dashboard... This will take a moment!",
                "state": "generating",
                "output_type": "dashboard"
            }
        else:
            response = "Please choose either **'notebook'** or **'dashboard'** for your output."
            session['history'].append({'role': 'assistant', 'content': response})
            return {"response": response, "state": "target_set", "choices": ["notebook", "dashboard"]}
    
    elif session['state'] == 'completed':
        return {
            "response": "✅ Your analysis is complete! Download the file above. Would you like to start a new analysis?",
            "state": "completed"
        }
    
    return {"response": "I'm not sure what you mean. Could you please clarify?", "state": session['state']}

def generate_final_output(session_id: str) -> dict:
    session = session_conversations.get(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    
    output_type = session.get('output_type')
    target_column = session.get('target_column')
    
    if not output_type or not target_column:
        return {"success": False, "error": "Missing output type or target column"}
    
    print(f"\n>>> Generating {output_type} for session {session_id}, target: {target_column}")
    
    # Initialize progress
    update_progress(session_id, 'starting', 5, f'🚀 Starting {output_type} generation...')
    
    if output_type == 'notebook':
        file_path = create_general_analysis_notebook(session_id)
    elif output_type == 'dashboard':
        file_path = create_interactive_dashboard(session_id)
    else:
        return {"success": False, "error": "Invalid output type"}
    
    if file_path and os.path.exists(file_path):
        session['state'] = 'completed'
        return {"success": True, "file_path": file_path, "filename": os.path.basename(file_path)}
    
    return {"success": False, "error": f"Failed to generate {output_type}"}

def create_general_analysis_notebook(session_id: str):
    try:
        update_progress(session_id, 'loading', 10, '📂 Loading dataset...')
        
        session = session_conversations[session_id]
        dataset_path = shared_data_store[f'{session_id}_dataset_path']
        target_column = session['target_column']
        df = shared_data_store[f'{session_id}_dataframe']
        
        update_progress(session_id, 'preparing', 25, '🔧 Preparing features...')
        
        numerical_features = [
            col for col in df.columns 
            if col != target_column and df[col].dtype in ['int64', 'float64'] and 'id' not in col.lower()
        ]
        
        features_list_str = str(numerical_features)
        read_function = "pd.read_csv" if str(dataset_path).endswith('.csv') else "pd.read_excel"
        dataset_path_str = str(Path(dataset_path).resolve()).replace('\\', '/')

        update_progress(session_id, 'building', 50, '📝 Building notebook structure...')
        
        notebook_filename = f"{os.path.basename(dataset_path).split('.')[0]}_analysis_{target_column}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
        
        notebook_content = {
            "cells": [
                {"cell_type": "markdown", "metadata": {}, "source": [
                    f"# 📊 Autonomous Data Science Analysis\n\n",
                    f"**Dataset:** {os.path.basename(dataset_path)}\n\n",
                    f"**Target Variable:** '{target_column}'\n\n",
                    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---"
                ]},
                {"cell_type": "code", "execution_count": None, "outputs": [], "metadata": {}, "source": [
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier\n",
                    "from sklearn.tree import DecisionTreeClassifier\n",
                    "from sklearn.neighbors import KNeighborsClassifier\n",
                    "from xgboost import XGBClassifier\n",
                    "from sklearn.model_selection import train_test_split, cross_val_score\n",
                    "from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score\n",
                    "import warnings\n",
                    "warnings.filterwarnings('ignore')\n",
                    "print('✅ Libraries imported!')"
                ]},
                {"cell_type": "code", "execution_count": None, "outputs": [], "metadata": {}, "source": [
                    f"df = {read_function}('{dataset_path_str}')\n",
                    "for col in df.select_dtypes(include=['float64', 'int64']).columns:\n",
                    "    df[col] = df[col].fillna(df[col].median())\n",
                    "print(f'Dataset shape: {df.shape}')\n",
                    "df.head()"
                ]},
                {"cell_type": "markdown", "metadata": {}, "source": ["## 🤖 Model Comparison\n\nComparing 5 different machine learning models to find the best performer."]},
                {"cell_type": "code", "execution_count": None, "outputs": [], "metadata": {}, "source": [
                    f"features = {features_list_str}\n",
                    f"target = '{target_column}'\n",
                    "X = df[[f for f in features if f in df.columns]]\n",
                    "y = df[target]\n",
                    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n",
                    "print(f'Training set: {len(X_train)} samples')\n",
                    "print(f'Test set: {len(X_test)} samples')"
                ]},
                {"cell_type": "code", "execution_count": None, "outputs": [], "metadata": {}, "source": [
                    "# Define models to compare\n",
                    "models = {\n",
                    "    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),\n",
                    "    'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss', verbosity=0),\n",
                    "    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),\n",
                    "    'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=10),\n",
                    "    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5)\n",
                    "}\n",
                    "\n",
                    "# Train and evaluate each model\n",
                    "results = []\n",
                    "for name, model in models.items():\n",
                    "    print(f'Training {name}...')\n",
                    "    model.fit(X_train, y_train)\n",
                    "    y_pred = model.predict(X_test)\n",
                    "    \n",
                    "    acc = accuracy_score(y_test, y_pred)\n",
                    "    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)\n",
                    "    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)\n",
                    "    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)\n",
                    "    \n",
                    "    results.append({\n",
                    "        'Model': name,\n",
                    "        'Accuracy': round(acc, 4),\n",
                    "        'Precision': round(prec, 4),\n",
                    "        'Recall': round(rec, 4),\n",
                    "        'F1-Score': round(f1, 4)\n",
                    "    })\n",
                    "\n",
                    "# Display results\n",
                    "results_df = pd.DataFrame(results).sort_values('Accuracy', ascending=False)\n",
                    "print('\\n' + '='*70)\n",
                    "print('📊 MODEL COMPARISON RESULTS')\n",
                    "print('='*70)\n",
                    "print(results_df.to_string(index=False))\n",
                    "print('='*70)\n",
                    "\n",
                    "# Identify best model\n",
                    "best_model_name = results_df.iloc[0]['Model']\n",
                    "best_accuracy = results_df.iloc[0]['Accuracy']\n",
                    "print(f'\\n🏆 Best Model: {best_model_name} with {best_accuracy:.2%} accuracy')"
                ]},
                {"cell_type": "code", "execution_count": None, "outputs": [], "metadata": {}, "source": [
                    "# Visualize model comparison\n",
                    "fig, axes = plt.subplots(1, 2, figsize=(15, 5))\n",
                    "\n",
                    "# Accuracy comparison\n",
                    "axes[0].barh(results_df['Model'], results_df['Accuracy'], color='skyblue')\n",
                    "axes[0].set_xlabel('Accuracy')\n",
                    "axes[0].set_title('Model Accuracy Comparison')\n",
                    "axes[0].set_xlim(0, 1)\n",
                    "for i, v in enumerate(results_df['Accuracy']):\n",
                    "    axes[0].text(v + 0.01, i, f'{v:.2%}', va='center')\n",
                    "\n",
                    "# All metrics comparison for best model\n",
                    "best_row = results_df.iloc[0]\n",
                    "metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']\n",
                    "values = [best_row[m] for m in metrics]\n",
                    "axes[1].bar(metrics, values, color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0'])\n",
                    "axes[1].set_ylabel('Score')\n",
                    "axes[1].set_title(f'Best Model ({best_model_name}) - All Metrics')\n",
                    "axes[1].set_ylim(0, 1)\n",
                    "for i, v in enumerate(values):\n",
                    "    axes[1].text(i, v + 0.02, f'{v:.2%}', ha='center')\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]},
                {"cell_type": "markdown", "metadata": {}, "source": ["## 📈 Confusion Matrix for Best Model"]},
                {"cell_type": "code", "execution_count": None, "outputs": [], "metadata": {}, "source": [
                    "# Train best model and show confusion matrix\n",
                    "best_model = models[best_model_name]\n",
                    "best_model.fit(X_train, y_train)\n",
                    "y_pred = best_model.predict(X_test)\n",
                    "\n",
                    "cm = confusion_matrix(y_test, y_pred)\n",
                    "plt.figure(figsize=(8, 6))\n",
                    "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True)\n",
                    "plt.xlabel('Predicted')\n",
                    "plt.ylabel('Actual')\n",
                    "plt.title(f'Confusion Matrix - {best_model_name}')\n",
                    "plt.show()\n",
                    "\n",
                    "print(f'\\n✅ Analysis Complete! Best model: {best_model_name} ({best_accuracy:.2%} accuracy)')"
                ]}
            ],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        update_progress(session_id, 'generating', 75, '✨ Generating code cells...')
        
        output_path = TEMP_DIR / notebook_filename
        with open(output_path, 'w') as f:
            json.dump(notebook_content, f, indent=2)
        
        update_progress(session_id, 'complete', 100, '✅ Notebook ready!')
        
        print(f"✅ Notebook created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error creating notebook: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_automated_insights(df, target_column, features, model, accuracy, y_test, y_pred):
    """Generate AI-powered automated insights from the dataset and model"""
    try:
        insights = {
            'statistical': [],
            'correlations': [],
            'model_insights': [],
            'recommendations': [],
            'narrative': ''
        }
        
        # 1. Statistical Insights
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 0:
            insights['statistical'].append(f"⚠️ Dataset has {missing_pct:.1f}% missing values")
        else:
            insights['statistical'].append("✅ No missing values detected - excellent data quality!")
        
        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            insights['statistical'].append(f"⚠️ Found {dup_count} duplicate rows ({dup_count/len(df)*100:.1f}%)")
        
        # Class imbalance
        class_dist = df[target_column].value_counts()
        imbalance_ratio = class_dist.max() / class_dist.min()
        if imbalance_ratio > 3:
            insights['statistical'].append(f"⚠️ Significant class imbalance detected (ratio: {imbalance_ratio:.1f}:1)")
        else:
            insights['statistical'].append(f"✅ Classes are well-balanced (ratio: {imbalance_ratio:.1f}:1)")
        
        # 2. Correlation Insights
        numeric_df = pd.DataFrame()
        for col in features:
            if col in df.columns:
                if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                    try:
                        from sklearn.preprocessing import LabelEncoder
                        le = LabelEncoder()
                        numeric_df[col] = le.fit_transform(df[col].astype(str))
                    except:
                        numeric_df[col] = 0
                else:
                    numeric_df[col] = df[col]
                    
        corr_matrix = numeric_df.corr() if not numeric_df.empty else pd.DataFrame()
        
        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    strong_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))
        
        if strong_corr:
            top_corr = sorted(strong_corr, key=lambda x: abs(x[2]), reverse=True)[:3]
            for feat1, feat2, corr_val in top_corr:
                insights['correlations'].append(f"🔗 Strong correlation between <strong>{feat1}</strong> and <strong>{feat2}</strong> ({corr_val:.2f})")
        else:
            insights['correlations'].append("✅ No multicollinearity issues - features are independent")
        
        # 3. Model Insights
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        if features == ['dummy_feature']:
            insights['model_insights'].append("ℹ️ Modeling was performed on a fallback feature because the dataset has no other numeric columns.")
        else:
            top_3_features = feature_importance.head(3)
            insights['model_insights'].append(f"🎯 Top predictor: <strong>{top_3_features.iloc[0]['feature']}</strong> ({top_3_features.iloc[0]['importance']:.1%} importance)")
        
        # Model performance analysis
        from sklearn.metrics import precision_score, recall_score, f1_score
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        if accuracy > 0.9:
            insights['model_insights'].append(f"🏆 Excellent model performance! Accuracy: {accuracy:.1%}")
        elif accuracy > 0.8:
            insights['model_insights'].append(f"✅ Good model performance. Accuracy: {accuracy:.1%}")
        else:
            insights['model_insights'].append(f"⚠️ Model accuracy is {accuracy:.1%} - consider feature engineering")
        
        if precision > recall:
            insights['model_insights'].append(f"📊 Model is more precise ({precision:.1%}) than sensitive ({recall:.1%})")
        else:
            insights['model_insights'].append(f"📊 Model is more sensitive ({recall:.1%}) than precise ({precision:.1%})")
        
        # 4. Recommendations
        if missing_pct > 5:
            insights['recommendations'].append("💡 Consider advanced imputation techniques for missing values")
        
        if imbalance_ratio > 3:
            insights['recommendations'].append("💡 Try SMOTE or class weighting to handle imbalance")
        
        if accuracy < 0.85:
            insights['recommendations'].append("💡 Consider hyperparameter tuning or ensemble methods")
            insights['recommendations'].append("💡 Try feature engineering: polynomial features, interactions")
        
        if len(strong_corr) > 2:
            insights['recommendations'].append("💡 Remove highly correlated features to reduce multicollinearity")
        
        # 5. Generate AI Narrative using Gemini
        try:
            prompt = f"""Generate a professional, concise data science report (3-4 paragraphs) based on this analysis:

Dataset: {len(df)} rows, {len(df.columns)} columns
Target: {target_column} with {df[target_column].nunique()} classes
Model: Random Forest with {accuracy:.1%} accuracy
Top Features: {', '.join(top_3_features['feature'].head(3).tolist())}
Key Stats: Precision={precision:.1%}, Recall={recall:.1%}, F1={f1:.1%}

Write in a professional tone suitable for a business presentation. Include:
1. Executive summary of findings
2. Key insights about the data
3. Model performance interpretation
4. Actionable recommendations

Keep it concise and impactful."""

            try:
                # Try gemini-1.5-flash (without -latest suffix)
                model_gemini = genai.GenerativeModel('gemini-1.5-flash')
                response = model_gemini.generate_content(prompt)
                insights['narrative'] = response.text
            except Exception as gemini_error:
                print(f"Gemini 1.5 Flash failed: {gemini_error}, trying gemini-1.5-pro...")
                try:
                    # Fallback to gemini-1.5-pro (without -latest suffix)
                    model_gemini = genai.GenerativeModel('gemini-1.5-pro')
                    response = model_gemini.generate_content(prompt)
                    insights['narrative'] = response.text
                except Exception as e2:
                    print(f"Both Gemini models failed: {e2}")
                    raise
        except Exception as e:
            print(f"Error generating narrative: {e}")
            insights['narrative'] = f"""
            <h3>Executive Summary</h3>
            <p>Analysis of {len(df):,} records reveals a {df[target_column].nunique()}-class classification problem. 
            Our Random Forest model achieved {accuracy:.1%} accuracy, with <strong>{top_3_features.iloc[0]['feature']}</strong> 
            being the strongest predictor.</p>
            
            <h3>Key Findings</h3>
            <p>The model demonstrates {'excellent' if accuracy > 0.9 else 'good' if accuracy > 0.8 else 'moderate'} 
            performance with balanced precision ({precision:.1%}) and recall ({recall:.1%}). 
            {'The dataset shows good quality with minimal missing values.' if missing_pct < 5 else 'Data quality could be improved by addressing missing values.'}</p>
            
            <h3>Recommendations</h3>
            <p>{'Consider deploying this model for production use.' if accuracy > 0.9 else 'Further optimization through hyperparameter tuning is recommended.'} 
            Focus on the top 3 features for maximum impact: {', '.join(top_3_features['feature'].head(3).tolist())}.</p>
            """
        
        return insights
        
    except Exception as e:
        print(f"Error generating insights: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statistical': ["Analysis in progress..."],
            'correlations': [],
            'model_insights': [],
            'recommendations': [],
            'narrative': "Insights generation encountered an error."
        }

def calculate_data_quality_score(df, target_column):
    """Calculate data quality score (0-100)"""
    try:
        score = 100
        issues = []
        
        # 1. Missing values (-20 points max)
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 0:
            penalty = min(20, missing_pct * 2)
            score -= penalty
            issues.append(f"Missing values: {missing_pct:.1f}%")
        
        # 2. Duplicate rows (-10 points max)
        dup_pct = (df.duplicated().sum() / len(df)) * 100
        if dup_pct > 0:
            penalty = min(10, dup_pct * 2)
            score -= penalty
            issues.append(f"Duplicates: {dup_pct:.1f}%")
        
        # 3. Class imbalance (-15 points max)
        if target_column in df.columns:
            class_dist = df[target_column].value_counts()
            imbalance_ratio = class_dist.max() / class_dist.min() if class_dist.min() > 0 else 10
            if imbalance_ratio > 2:
                penalty = min(15, (imbalance_ratio - 2) * 3)
                score -= penalty
                issues.append(f"Class imbalance: {imbalance_ratio:.1f}:1")
        
        # 4. Outliers in numeric columns (-10 points max)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        outlier_count = 0
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            outlier_count += outliers
        
        outlier_pct = (outlier_count / (len(df) * len(numeric_cols))) * 100 if len(numeric_cols) > 0 else 0
        if outlier_pct > 5:
            penalty = min(10, outlier_pct)
            score -= penalty
            issues.append(f"Outliers: {outlier_pct:.1f}%")
        
        # 5. Data type consistency (-5 points)
        if df.select_dtypes(include=['object']).shape[1] > df.shape[1] * 0.7:
            score -= 5
            issues.append("Too many text columns")
        
        score = max(0, min(100, score))
        
        # Determine grade
        if score >= 90:
            grade = "A"
            color = "#10b981"  # green
            status = "Excellent"
        elif score >= 80:
            grade = "B"
            color = "#3b82f6"  # blue
            status = "Good"
        elif score >= 70:
            grade = "C"
            color = "#f59e0b"  # yellow
            status = "Fair"
        elif score >= 60:
            grade = "D"
            color = "#ef4444"  # red
            status = "Poor"
        else:
            grade = "F"
            color = "#dc2626"  # dark red
            status = "Critical"
        
        return {
            'score': round(score, 1),
            'grade': grade,
            'color': color,
            'status': status,
            'issues': issues
        }
        
    except Exception as e:
        print(f"Error calculating quality score: {e}")
        return {
            'score': 75,
            'grade': 'C',
            'color': '#f59e0b',
            'status': 'Unknown',
            'issues': []
        }

def create_interactive_dashboard(session_id: str):
    try:
        update_progress(session_id, 'loading', 10, '📂 Loading dataset...')
        
        session = session_conversations[session_id]
        df = shared_data_store[f'{session_id}_dataframe']
        target_column = session['target_column']
        dataset_path = shared_data_store[f'{session_id}_dataset_path']
        
        update_progress(session_id, 'visualizing', 30, '📊 Creating visualizations...')
        
        # Copy dataframe and encode categorical features to numerical for modeling
        df_encoded = df.copy()
        for col in df_encoded.columns:
            if col != target_column and df_encoded[col].dtype == 'object':
                try:
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                except Exception as e:
                    print(f"Error encoding column {col}: {e}")
                    
        all_numerical = [
            col for col in df_encoded.columns 
            if col != target_column 
            and df_encoded[col].dtype in ['int64', 'float64', 'int32']
            and 'id' not in col.lower()
        ]
        numerical_features = all_numerical[:10]  # Limit to 10 for modeling
        
        if len(numerical_features) == 0:
            df_encoded['dummy_feature'] = 0
            numerical_features = ['dummy_feature']
            
        print(f"Total numerical/encoded features available: {len(all_numerical)}")
        print(f"Using {len(numerical_features)} features for modeling")
        
        # Prepare data for modeling
        from sklearn.preprocessing import LabelEncoder
        from sklearn.metrics import roc_curve, auc, precision_recall_curve
        import numpy as np
        
        X = df_encoded[numerical_features].fillna(df_encoded[numerical_features].median())
        y = df[target_column]
        
        # Encode target if categorical
        label_encoder = None
        if y.dtype == 'object' or y.dtype.name == 'category':
            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)
        else:
            y_encoded = y
        
        # Train model for advanced metrics
        # Check if we can use stratify
        from collections import Counter
        class_counts = Counter(y_encoded)
        min_class_count = min(class_counts.values())
        
        if min_class_count >= 2:
            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
        
        print(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
        print(f"Number of classes: {len(np.unique(y_encoded))}")
        
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        rf_model.fit(X_train, y_train)
        y_pred = rf_model.predict(X_test)
        y_pred_proba = rf_model.predict_proba(X_test)
        
        print(f"Predictions shape: {y_pred.shape}, Probabilities shape: {y_pred_proba.shape}")
        
        # 1. Distribution Chart - Use bar chart for better visibility with small datasets
        value_counts = df[target_column].value_counts().reset_index()
        value_counts.columns = [target_column, 'count']
        
        print(f"Target distribution value_counts:\n{value_counts}")
        
        # Create bar chart using go.Bar for more control
        # IMPORTANT: Convert to Python lists to avoid binary encoding issues
        dist_fig = go.Figure()
        
        colors = px.colors.qualitative.Set3[:len(value_counts)]
        
        # Convert pandas Series to Python lists explicitly
        x_values = value_counts[target_column].tolist()
        y_values = value_counts['count'].tolist()
        text_values = [str(int(v)) for v in y_values]  # Convert to string integers
        
        dist_fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            text=text_values,
            textposition='outside',
            marker=dict(
                color=colors,
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        ))
        
        dist_fig.update_layout(
            title=dict(
                text=f'Distribution of {target_column}',
                x=0.5,
                xanchor='center'
            ),
            showlegend=False,
            height=450,
            template='plotly_white',
            margin=dict(l=50, r=50, t=80, b=50),
            xaxis_title=target_column,
            yaxis_title='Count',
            yaxis=dict(range=[0, max(y_values) * 1.2]),
            bargap=0.2
        )
        
        update_progress(session_id, 'heatmap', 40, '🔥 Generating correlation heatmap...')
        
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        heatmap_html = ""
        
        if len(numeric_df.columns) > 1:
            plt.figure(figsize=(10, 8))
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', center=0)
            plt.title('Feature Correlation Heatmap', pad=20, fontsize=16, fontweight='bold')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            heatmap_html = f'<img src="data:image/png;base64,{img_b64}" class="w-full h-auto rounded-lg shadow-lg">'
        
        update_progress(session_id, 'feature_importance', 50, '⭐ Creating feature importance chart...')
        
        # 2. Feature Importance Chart (Interactive)
        feature_importance = pd.DataFrame({
            'feature': numerical_features,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=True)
        
        importance_fig = px.bar(feature_importance, x='importance', y='feature', 
                               orientation='h',
                               title='Feature Importance (Random Forest)',
                               color='importance',
                               color_continuous_scale='Viridis')
        importance_fig.update_layout(showlegend=False, title_x=0.5, height=400)
        
        update_progress(session_id, '3d_plot', 55, '🎨 Creating 3D visualization...')
        
        # 3. 3D Scatter Plot (if we have at least 3 features)
        scatter_3d_html = ""
        surface_3d_html = ""
        
        print(f"Number of numerical features for 3D: {len(numerical_features)}")
        print(f"Features: {numerical_features[:5] if len(numerical_features) > 0 else 'None'}")
        
        if len(numerical_features) >= 3:
            print("Creating 3D scatter plot...")
            
            # Sample data if too large (for performance)
            df_sample = df_encoded
            if len(df_encoded) > 1000:
                sample_size = min(1000, len(df_encoded))
                df_sample = df_encoded.sample(n=sample_size, random_state=42)
                print(f"Sampling {sample_size} points from {len(df_encoded)} for 3D visualization")
            
            # 3D Scatter Plot
            scatter_3d = px.scatter_3d(df_sample, 
                                      x=numerical_features[0], 
                                      y=numerical_features[1], 
                                      z=numerical_features[2],
                                      color=target_column,
                                      title=f'3D Feature Space - Interactive Scatter',
                                      color_discrete_sequence=px.colors.qualitative.Bold,
                                      opacity=0.7,
                                      size_max=10)
            scatter_3d.update_layout(
                title_x=0.5,
                height=700,
                template='plotly_white',
                scene=dict(
                    xaxis_title=numerical_features[0],
                    yaxis_title=numerical_features[1],
                    zaxis_title=numerical_features[2],
                    bgcolor='rgba(240,240,240,0.9)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            # Use 'cdn' for 3D plots to ensure proper rendering
            scatter_3d_html = scatter_3d.to_html(full_html=False, include_plotlyjs='cdn', div_id="scatter_3d_chart", config={'displayModeBar': True, 'responsive': True})
            print(f"3D Scatter created: {len(scatter_3d_html)} characters")
            
            # 3D Surface Plot (Feature Interaction)
            try:
                print("Creating 3D surface plot...")
                # Create a grid for surface plot
                x_range = np.linspace(df_encoded[numerical_features[0]].min(), df_encoded[numerical_features[0]].max(), 30)
                y_range = np.linspace(df_encoded[numerical_features[1]].min(), df_encoded[numerical_features[1]].max(), 30)
                x_grid, y_grid = np.meshgrid(x_range, y_range)
                
                # Use the trained model to predict on the grid
                grid_features = np.zeros((x_grid.size, len(numerical_features)))
                grid_features[:, 0] = x_grid.ravel()
                grid_features[:, 1] = y_grid.ravel()
                # Fill other features with median values
                for i in range(2, len(numerical_features)):
                    grid_features[:, i] = df_encoded[numerical_features[i]].median()
                
                z_grid = rf_model.predict_proba(grid_features)[:, 0].reshape(x_grid.shape)
                
                surface_fig = go.Figure(data=[go.Surface(
                    x=x_range,
                    y=y_range,
                    z=z_grid,
                    colorscale='Viridis',
                    name='Decision Surface'
                )])
                
                surface_fig.update_layout(
                    title=f'3D Decision Surface - {numerical_features[0]} vs {numerical_features[1]}',
                    title_x=0.5,
                    height=700,
                    template='plotly_white',
                    scene=dict(
                        xaxis_title=numerical_features[0],
                        yaxis_title=numerical_features[1],
                        zaxis_title='Prediction Probability',
                        bgcolor='rgba(240,240,240,0.9)',
                        camera=dict(
                            eye=dict(x=1.5, y=1.5, z=1.5)
                        )
                    ),
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                # Use 'cdn' for 3D plots to ensure proper rendering
                surface_3d_html = surface_fig.to_html(full_html=False, include_plotlyjs='cdn', div_id="surface_3d_chart", config={'displayModeBar': True, 'responsive': True})
                print(f"3D Surface created: {len(surface_3d_html)} characters")
            except Exception as e:
                print(f"Could not create 3D surface plot: {e}")
                import traceback
                traceback.print_exc()
        
        update_progress(session_id, 'roc_curve', 60, '📈 Generating ROC curves...')
        
        # 4. ROC Curve - Simplified and Working
        roc_fig = go.Figure()
        n_classes = len(np.unique(y_encoded))
        
        try:
            print(f"Creating ROC curve for {n_classes} classes")
            
            # Always add diagonal reference line first
            roc_fig.add_trace(go.Scatter(
                x=[0, 0.5, 1],
                y=[0, 0.5, 1],
                mode='lines',
                name='Random Classifier',
                line=dict(color='gray', width=2, dash='dash'),
                visible=True
            ))
            
            if n_classes == 2:
                # Binary classification
                fpr, tpr, _ = roc_curve(y_test, y_pred_proba[:, 1])
                roc_auc = auc(fpr, tpr)
                print(f"Binary ROC - AUC: {roc_auc:.3f}")
                
                roc_fig.add_trace(go.Scatter(
                    x=list(fpr),
                    y=list(tpr),
                    mode='lines+markers',
                    name=f'Model (AUC={roc_auc:.2f})',
                    line=dict(color='red', width=4),
                    marker=dict(size=8, color='red'),
                    visible=True
                ))
            else:
                # Multiclass
                from sklearn.preprocessing import label_binarize
                model_classes = list(rf_model.classes_)
                y_test_bin = label_binarize(y_test, classes=model_classes)
                if len(model_classes) == 2 and len(y_test_bin.shape) == 1:
                    y_test_bin = np.column_stack((1 - y_test_bin, y_test_bin))
                
                colors = ['red', 'blue', 'green', 'orange', 'purple']
                plotted_classes = 0
                for i in range(len(model_classes)):
                    if plotted_classes >= 5:
                        break
                    class_idx = model_classes[i]
                    class_name = label_encoder.classes_[class_idx] if label_encoder else f'Class {class_idx}'
                    
                    if np.sum(y_test == class_idx) > 0:
                        try:
                            fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_proba[:, i])
                            roc_auc = auc(fpr, tpr)
                            if not np.isnan(roc_auc):
                                print(f"Adding {class_name} - AUC: {roc_auc:.3f}")
                                roc_fig.add_trace(go.Scatter(
                                    x=list(fpr),
                                    y=list(tpr),
                                    mode='lines+markers',
                                    name=f'{class_name} (AUC={roc_auc:.2f})',
                                    line=dict(color=colors[plotted_classes % len(colors)], width=4),
                                    marker=dict(size=8),
                                    visible=True
                                ))
                                plotted_classes += 1
                        except Exception as e:
                            print(f"Error with class {class_name}: {e}")
            
            roc_fig.update_layout(
                title='ROC Curve',
                xaxis_title='False Positive Rate',
                yaxis_title='True Positive Rate',
                height=500,
                showlegend=True,
                xaxis=dict(range=[0, 1], showgrid=True),
                yaxis=dict(range=[0, 1], showgrid=True)
            )
            
            print(f"ROC figure has {len(roc_fig.data)} traces")
        except Exception as e:
            print(f"ROC Error: {e}")
            import traceback
            traceback.print_exc()
        
        update_progress(session_id, 'precision_recall', 65, '🎯 Creating precision-recall curve...')
        
        # 5. Precision-Recall Curve - Simplified
        pr_fig = go.Figure()
        
        try:
            print(f"Creating PR curve for {n_classes} classes")
            
            if n_classes == 2:
                precision, recall, _ = precision_recall_curve(y_test, y_pred_proba[:, 1])
                print(f"Binary PR - {len(precision)} points")
                
                pr_fig.add_trace(go.Scatter(
                    x=list(recall),
                    y=list(precision),
                    mode='lines+markers',
                    name='Model',
                    line=dict(color='green', width=4),
                    marker=dict(size=8, color='green'),
                    visible=True
                ))
            else:
                # Multiclass
                from sklearn.preprocessing import label_binarize
                model_classes = list(rf_model.classes_)
                y_test_bin = label_binarize(y_test, classes=model_classes)
                if len(model_classes) == 2 and len(y_test_bin.shape) == 1:
                    y_test_bin = np.column_stack((1 - y_test_bin, y_test_bin))
                
                colors = ['red', 'blue', 'green', 'orange', 'purple']
                plotted_classes = 0
                for i in range(len(model_classes)):
                    if plotted_classes >= 5:
                        break
                    class_idx = model_classes[i]
                    class_name = label_encoder.classes_[class_idx] if label_encoder else f'Class {class_idx}'
                    
                    if np.sum(y_test == class_idx) > 0:
                        try:
                            precision, recall, _ = precision_recall_curve(y_test_bin[:, i], y_pred_proba[:, i])
                            print(f"Adding {class_name} - {len(precision)} points")
                            
                            pr_fig.add_trace(go.Scatter(
                                x=list(recall),
                                y=list(precision),
                                mode='lines+markers',
                                name=class_name,
                                line=dict(color=colors[plotted_classes % len(colors)], width=4),
                                marker=dict(size=8),
                                visible=True
                            ))
                            plotted_classes += 1
                        except Exception as e:
                            print(f"Error with class {class_name}: {e}")
            
            pr_fig.update_layout(
                title='Precision-Recall Curve',
                xaxis_title='Recall',
                yaxis_title='Precision',
                height=500,
                showlegend=True,
                xaxis=dict(range=[0, 1], showgrid=True),
                yaxis=dict(range=[0, 1], showgrid=True)
            )
            
            print(f"PR figure has {len(pr_fig.data)} traces")
        except Exception as e:
            print(f"PR Error: {e}")
            import traceback
            traceback.print_exc()
        
        update_progress(session_id, 'confusion', 70, '🔢 Building confusion matrix...')
        
        # 6. Confusion Matrix - Using both Plotly AND HTML table as backup
        cm_fig = None
        cm_table_html = ""
        
        try:
            cm = confusion_matrix(y_test, y_pred)
            class_names = label_encoder.classes_ if label_encoder else [str(i) for i in range(n_classes)]
            
            print(f"Confusion Matrix shape: {cm.shape}")
            print(f"Confusion Matrix:\n{cm}")
            
            # Create Plotly heatmap - use only classes present in confusion matrix
            actual_classes = class_names[:cm.shape[0]]
            max_val = cm.max()
            
            if len(actual_classes) > 20:
                # For high cardinality, don't show text annotations in heatmap as it freezes the browser
                cm_fig = go.Figure(data=go.Heatmap(
                    z=cm.tolist(),
                    x=list(actual_classes),
                    y=list(actual_classes),
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title="Count")
                ))
                cm_fig.update_layout(
                    title='Confusion Matrix (High Cardinality)',
                    xaxis_title='Predicted',
                    yaxis_title='Actual',
                    height=700,
                    width=700,
                    xaxis=dict(side='bottom', showticklabels=False),
                    yaxis=dict(autorange='reversed', showticklabels=False)
                )
                
                # Render a summary note instead of a massive HTML table
                from collections import Counter
                test_counts = Counter(y_test)
                top_class_indices = [idx for idx, count in test_counts.most_common(10)]
                top_class_names = [class_names[idx] for idx in top_class_indices if idx < len(class_names)]
                
                cm_table_html = f'<div class="text-center p-6 bg-slate-800 rounded-lg text-slate-300 border border-slate-700 max-w-2xl mx-auto my-6">'
                cm_table_html += f'<p class="mb-2 font-semibold">⚠️ Confusion matrix table is hidden because the dataset has too many target classes ({len(actual_classes)} classes).</p>'
                cm_table_html += f'<p class="text-sm text-slate-400">Top 10 classes in test set: {", ".join(top_class_names)}</p>'
                cm_table_html += f'</div>'
            else:
                cm_fig = go.Figure(data=go.Heatmap(
                    z=cm.tolist(),
                    x=list(actual_classes),
                    y=list(actual_classes),
                    colorscale='Blues',
                    text=cm.tolist(),
                    texttemplate='%{text}',
                    textfont={"size": 14 if len(actual_classes) > 8 else 20, "color": "white"},
                    showscale=True,
                    colorbar=dict(title="Count")
                ))
                cm_fig.update_layout(
                    title='Confusion Matrix',
                    xaxis_title='Predicted',
                    yaxis_title='Actual',
                    height=600,
                    width=600,
                    xaxis=dict(side='bottom', tickmode='array', tickvals=list(range(len(actual_classes))), ticktext=list(actual_classes)),
                    yaxis=dict(autorange='reversed', tickmode='array', tickvals=list(range(len(actual_classes))), ticktext=list(actual_classes))
                )
                
                cm_table_html = '<table style="border-collapse: collapse; margin: 20px auto; font-size: 16px;">'
                cm_table_html += '<tr><th style="padding: 10px; border: 1px solid #ddd;"></th>'
                for name in actual_classes:
                    cm_table_html += f'<th style="padding: 10px; border: 1px solid #ddd; background: #f0f0f0;"><b>Pred: {name}</b></th>'
                cm_table_html += '</tr>'
                
                for i, actual_name in enumerate(actual_classes):
                    cm_table_html += f'<tr><th style="padding: 10px; border: 1px solid #ddd; background: #f0f0f0;"><b>Actual: {actual_name}</b></th>'
                    for j in range(len(actual_classes)):
                        val = cm[i][j] if i < cm.shape[0] and j < cm.shape[1] else 0
                        intensity = int((val / max_val) * 200) if max_val > 0 else 0
                        bg_color = f'rgb({255-intensity}, {255-intensity}, 255)'
                        cm_table_html += f'<td style="padding: 20px; border: 1px solid #ddd; background: {bg_color}; text-align: center; font-size: 20px; font-weight: bold;">{val}</td>'
                    cm_table_html += '</tr>'
                cm_table_html += '</table>'
            
            print(f"Confusion matrix created with shape {cm.shape}")
            print(f"HTML table created: {len(cm_table_html)} chars")
        except Exception as e:
            print(f"Error creating confusion matrix: {e}")
            import traceback
            traceback.print_exc()
            cm_fig = go.Figure()
            cm_fig.add_annotation(
                text=f"Confusion Matrix Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            cm_table_html = f"<p style='color: red;'>Error: {str(e)}</p>"
        
        # 7. Box Plot
        adaptive_fig_html = ""
        if len(numeric_df.columns) > 0:
            key_numeric = numeric_df.columns[0]
            adaptive_fig = px.box(df, x=target_column, y=key_numeric, color=target_column,
                                 title=f'{key_numeric} Distribution by {target_column}',
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            adaptive_fig.update_layout(showlegend=False, title_x=0.5, height=400)
            adaptive_fig_html = adaptive_fig.to_html(full_html=False, include_plotlyjs=False)
        
        # Calculate accuracy for stats display
        from sklearn.metrics import accuracy_score
        best_accuracy = accuracy_score(y_test, y_pred)
        
        # Calculate data quality score
        quality_score = calculate_data_quality_score(df, target_column)
        
        # Generate AI-powered insights
        update_progress(session_id, 'insights', 72, '🧠 Generating AI insights...')
        ai_insights = generate_automated_insights(df, target_column, numerical_features, rf_model, best_accuracy, y_test, y_pred)
        
        insights = []
        insights.append(f"Dataset contains <strong>{df.shape[0]:,}</strong> rows and <strong>{df.shape[1]}</strong> columns")
        insights.append(f"Target '<strong>{target_column}</strong>' has <strong>{df[target_column].nunique()}</strong> unique values")
        insights.append(f"Model achieved <strong>{best_accuracy:.1%}</strong> accuracy on test set")
        
        insights_html = "".join([f"<div class='insight-item'><span class='text-purple-400 mr-2 font-bold'>▸</span>{i}</div>" for i in insights])
        
        update_progress(session_id, 'building', 75, '🎨 Building HTML dashboard...')
        
        dashboard_filename = f"{os.path.basename(dataset_path).split('.')[0]}_dashboard_{target_column}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = TEMP_DIR / dashboard_filename
        
        # Convert all Plotly figures to HTML strings
        print("Converting figures to HTML...")
        dist_fig_html = dist_fig.to_html(full_html=False, include_plotlyjs=False, div_id="dist_chart", config={'responsive': True, 'displayModeBar': True})
        importance_fig_html = importance_fig.to_html(full_html=False, include_plotlyjs=False, div_id="importance_chart", config={'responsive': True, 'displayModeBar': True})
        roc_fig_html = roc_fig.to_html(full_html=False, include_plotlyjs=False, div_id="roc_chart", config={'responsive': True, 'displayModeBar': True})
        pr_fig_html = pr_fig.to_html(full_html=False, include_plotlyjs=False, div_id="pr_chart", config={'responsive': True, 'displayModeBar': True})
        
        # Try different approach for confusion matrix - include plotlyjs to ensure it renders
        cm_fig_html = cm_fig.to_html(full_html=False, include_plotlyjs=False, div_id="cm_chart", config={'displayModeBar': True})
        
        print(f"Confusion matrix HTML length: {len(cm_fig_html)}")
        print(f"CM HTML preview: {cm_fig_html[:200]}...")
        print(f"3D scatter HTML length: {len(scatter_3d_html) if scatter_3d_html else 0}")
        print(f"3D surface HTML length: {len(surface_3d_html) if surface_3d_html else 0}")
        
        # Build HTML content
        html_parts = []
        
        # Header with modern design
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Scientist Dashboard - {os.path.basename(dataset_path)}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ 
            font-family: 'Inter', sans-serif; 
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            min-height: 100vh;
        }}
        .chart-card {{ 
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}
        .chart-card:hover {{ 
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            border-color: rgba(99, 102, 241, 0.5);
        }}
        .chart-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6, #d946ef);
        }}
        .metric-card {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            transition: all 0.3s ease;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(79, 70, 229, 0.4);
            border-color: rgba(139, 92, 246, 0.6);
        }}
        .insight-item {{
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-left: 4px solid #6366f1;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-radius: 0.5rem;
            color: #e2e8f0;
            font-size: 0.95rem;
            line-height: 1.6;
            transition: all 0.3s ease;
        }}
        .insight-item:hover {{
            background: linear-gradient(135deg, #334155 0%, #475569 100%);
            border-left-color: #8b5cf6;
            transform: translateX(8px);
        }}
        .section-title {{
            color: #f1f5f9;
            font-size: 1.75rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .stat-value {{
            color: #ffffff;
            font-size: 2rem;
            font-weight: 900;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .stat-label {{
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        .animate-fade-in {{
            animation: fadeInUp 0.6s ease-out forwards;
        }}
        .glass-effect {{
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(148, 163, 184, 0.2);
        }}
        .chart-title {{
            color: #f1f5f9;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        .badge {{
            display: inline-block;
            padding: 0.375rem 0.875rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <!-- Hero Header -->
        <div class="relative bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-3xl shadow-2xl p-8 md:p-12 mb-8 text-white overflow-hidden">
            <div class="absolute top-0 right-0 w-96 h-96 bg-white opacity-5 rounded-full -mr-48 -mt-48"></div>
            <div class="absolute bottom-0 left-0 w-64 h-64 bg-white opacity-5 rounded-full -ml-32 -mb-32"></div>
            <div class="relative z-10">
                <div class="flex items-center mb-6">
                    <div class="w-20 h-20 bg-white rounded-2xl flex items-center justify-center mr-5 shadow-2xl">
                        <span class="text-5xl">&#129302;</span>
                    </div>
                    <div>
                        <h1 class="text-4xl md:text-6xl font-black tracking-tight">AI Data Scientist</h1>
                        <p class="text-lg md:text-xl opacity-95 mt-2 font-medium">Autonomous Machine Learning Dashboard</p>
                    </div>
                </div>
                <div class="flex flex-wrap gap-3 mt-8">
                    <div class="glass-effect px-5 py-3 rounded-xl">
                        <span class="text-sm opacity-80 font-medium">Dataset</span>
                        <span class="font-bold ml-2 text-lg">{os.path.basename(dataset_path)}</span>
                    </div>
                    <div class="glass-effect px-4 py-2 rounded-lg">
                        <span class="text-sm opacity-75">Target:</span>
                        <span class="font-semibold ml-2">{target_column}</span>
                    </div>
                    <div class="glass-effect px-4 py-2 rounded-lg">
                        <span class="text-sm opacity-75">Generated:</span>
                        <span class="font-semibold ml-2">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Stats Grid -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div class="metric-card rounded-xl p-6 text-center">
                <div class="stat-value">{len(df)}</div>
                <div class="stat-label">Samples</div>
            </div>
            <div class="metric-card rounded-xl p-6 text-center">
                <div class="stat-value">{len(df.columns)}</div>
                <div class="stat-label">Features</div>
            </div>
            <div class="metric-card rounded-xl p-6 text-center">
                <div class="stat-value">{df[target_column].nunique()}</div>
                <div class="stat-label">Classes</div>
            </div>
            <div class="metric-card rounded-xl p-6 text-center">
                <div class="stat-value">{round(best_accuracy * 100, 1)}%</div>
                <div class="stat-label">Best Accuracy</div>
            </div>
            <div class="rounded-xl p-6 text-center" style="background: linear-gradient(135deg, {quality_score['color']} 0%, {quality_score['color']}dd 100%); border: 2px solid {quality_score['color']};">
                <div class="relative inline-block">
                    <svg class="transform -rotate-90" width="100" height="100">
                        <circle cx="50" cy="50" r="40" stroke="rgba(255,255,255,0.2)" stroke-width="8" fill="none"/>
                        <circle cx="50" cy="50" r="40" stroke="white" stroke-width="8" fill="none"
                                stroke-dasharray="{quality_score['score'] * 2.51} 251"
                                stroke-linecap="round"/>
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center">
                        <div class="text-white">
                            <div class="text-3xl font-black">{quality_score['score']}</div>
                            <div class="text-xs font-bold">{quality_score['grade']}</div>
                        </div>
                    </div>
                </div>
                <div class="stat-label mt-2" style="color: white;">Data Quality</div>
                <div class="text-xs text-white opacity-90 mt-1">{quality_score['status']}</div>
            </div>
        </div>

        <!-- Key Insights Card -->
        <div class="chart-card rounded-2xl shadow-2xl p-8 mb-8 animate-fade-in">
            <div class="section-title">
                <div class="w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-3xl">&#128161;</span>
                </div>
                <span>Key Insights</span>
            </div>
            <div class="space-y-3">{insights_html}</div>
        </div>

        <!-- AI-Generated Insights Section -->
        <div class="chart-card rounded-2xl shadow-2xl p-8 mb-8 animate-fade-in" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: 2px solid rgba(139, 92, 246, 0.5);">
            <div class="section-title" style="color: white;">
                <div class="w-14 h-14 bg-white rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-3xl">&#129302;</span>
                </div>
                <span>AI-Powered Analysis Report</span>
            </div>
            
            <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 mb-6">
                <div class="text-white prose prose-invert max-w-none">
                    {ai_insights['narrative']}
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-5">
                    <h4 class="text-white font-bold text-lg mb-4 flex items-center">
                        <span class="text-2xl mr-2">📊</span> Statistical Findings
                    </h4>
                    <div class="space-y-2">
                        {''.join([f'<div class="text-slate-100 text-sm py-2 border-b border-white border-opacity-20">{item}</div>' for item in ai_insights['statistical']])}
                    </div>
                </div>
                
                <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-5">
                    <h4 class="text-white font-bold text-lg mb-4 flex items-center">
                        <span class="text-2xl mr-2">🔗</span> Correlation Analysis
                    </h4>
                    <div class="space-y-2">
                        {''.join([f'<div class="text-slate-100 text-sm py-2 border-b border-white border-opacity-20">{item}</div>' for item in ai_insights['correlations']]) if ai_insights['correlations'] else '<div class="text-slate-200 text-sm">No significant correlations found</div>'}
                    </div>
                </div>
                
                <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-5">
                    <h4 class="text-white font-bold text-lg mb-4 flex items-center">
                        <span class="text-2xl mr-2">🎯</span> Model Performance
                    </h4>
                    <div class="space-y-2">
                        {''.join([f'<div class="text-slate-100 text-sm py-2 border-b border-white border-opacity-20">{item}</div>' for item in ai_insights['model_insights']])}
                    </div>
                </div>
                
                <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-5">
                    <h4 class="text-white font-bold text-lg mb-4 flex items-center">
                        <span class="text-2xl mr-2">💡</span> Recommendations
                    </h4>
                    <div class="space-y-2">
                        {''.join([f'<div class="text-slate-100 text-sm py-2 border-b border-white border-opacity-20">{item}</div>' for item in ai_insights['recommendations']]) if ai_insights['recommendations'] else '<div class="text-slate-200 text-sm">✅ Model is performing optimally!</div>'}
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Visualizations Grid -->
        """)
        html_parts.append("""
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="chart-card p-6 rounded-2xl shadow-2xl animate-fade-in">
                <h3 class="chart-title">
                    <span class="text-2xl mr-2">&#128202;</span>
                    Target Distribution
                </h3>
                <div style="width: 100%; min-height: 400px;">
        """)
        html_parts.append(dist_fig_html)
        html_parts.append("""
                </div>
            </div>
            <div class="chart-card p-6 rounded-2xl shadow-2xl animate-fade-in">
                <h3 class="chart-title">
                    <span class="text-2xl mr-2">&#128293;</span>
                    Correlation Heatmap
                </h3>
                <div style="width: 100%; min-height: 400px;">
        """)
        html_parts.append(heatmap_html)
        html_parts.append("""
                </div>
            </div>
        </div>
        
        <div class="chart-card p-8 rounded-2xl shadow-2xl mb-8 animate-fade-in">
            <div class="section-title">
                <div class="w-14 h-14 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-3xl">&#127919;</span>
                </div>
                <span>Feature Importance Analysis</span>
            </div>
        """)
        html_parts.append(importance_fig_html)
        html_parts.append("""
        </div>
""")
        
        # 3D Visualizations
        if scatter_3d_html:
            print(f"Adding 3D scatter to HTML (length: {len(scatter_3d_html)})")
            html_parts.append("""
        <div class="chart-card rounded-2xl p-8 mb-8 shadow-2xl">
            <div class="section-title mb-6">
                <div class="w-14 h-14 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-3xl">&#127760;</span>
                </div>
                <span>3D Interactive Visualizations</span>
            </div>
            <div class="grid grid-cols-1 gap-6">
                <div class="glass-effect p-6 rounded-xl">
                    <h3 class="chart-title">3D Feature Space Scatter</h3>
                    <p class="text-slate-300 text-sm mb-4">Rotate, zoom, and pan to explore the feature space</p>
                    <div style="width: 100%; min-height: 700px;">
""")
            html_parts.append(scatter_3d_html)
            html_parts.append("</div></div>")
            print("3D scatter added to HTML")
            
            if surface_3d_html:
                print(f"Adding 3D surface to HTML (length: {len(surface_3d_html)})")
                html_parts.append("""
                <div class="glass-effect p-6 rounded-xl">
                    <h3 class="chart-title">3D Decision Surface</h3>
                    <p class="text-slate-300 text-sm mb-4">Model prediction probability landscape</p>
                    <div style="width: 100%; min-height: 700px;">
""")
                html_parts.append(surface_3d_html)
                html_parts.append("</div></div>")
                print("3D surface added to HTML")
            
            html_parts.append("</div></div>")
        
        # Model Performance Section
        html_parts.append("""
        <div class="chart-card rounded-2xl p-8 mb-8 shadow-2xl animate-fade-in">
            <div class="section-title mb-8">
                <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-3xl">&#128200;</span>
                </div>
                <span>Model Performance Metrics</span>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="glass-effect p-6 rounded-xl">
                    <h3 class="chart-title">
                        <span class="text-xl mr-2">&#128202;</span>
                        ROC Curve
                    </h3>
        """)
        html_parts.append(roc_fig_html)
        html_parts.append("""
                </div>
                <div class="glass-effect p-6 rounded-xl">
                    <h3 class="chart-title">
                        <span class="text-xl mr-2">&#127919;</span>
                        Precision-Recall Curve
                    </h3>
        """)
        html_parts.append(pr_fig_html)
        html_parts.append("""
                </div>
            </div>
        </div>

        """)
        html_parts.append("""
        <div class="chart-card p-8 rounded-2xl shadow-2xl mb-8 animate-fade-in">
            <div class="section-title mb-6">
                <div class="w-14 h-14 bg-gradient-to-br from-orange-400 to-red-500 rounded-xl flex items-center justify-center shadow-lg">
                    <span class="text-3xl">&#128290;</span>
                </div>
                <span>Confusion Matrix Analysis</span>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="glass-effect p-5 rounded-xl">
                    <h4 class="text-slate-200 text-sm font-semibold mb-4 text-center">Interactive Heatmap</h4>
        """)
        print(f"Adding confusion matrix Plotly ({len(cm_fig_html)} chars)")
        html_parts.append(cm_fig_html)
        html_parts.append("""
                </div>
                <div class="glass-effect p-5 rounded-xl">
                    <h4 class="text-slate-200 text-sm font-semibold mb-4 text-center">Detailed Table View</h4>
        """)
        html_parts.append(cm_table_html)
        html_parts.append("""
                </div>
            </div>
        </div>
""")
        print("Confusion matrix (Plotly + Table) added to HTML")
        
        # Box Plot
        if adaptive_fig_html:
            html_parts.append("""
        <div class="chart-card p-6 rounded-xl shadow-2xl mb-6">
            <h3 class="chart-title">Distribution Analysis</h3>
        """)
            html_parts.append(adaptive_fig_html)
            html_parts.append("""
        </div>
        """)
        
        # Footer
        html_parts.append("""
        <div class="mt-16 mb-8">
            <div class="chart-card rounded-2xl p-8 text-center">
                <div class="flex justify-center mb-6">
                    <div class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl">
                        <span class="text-4xl">&#128640;</span>
                    </div>
                </div>
                <h3 class="text-2xl font-bold text-slate-100 mb-3">Generated by Autonomous Data Scientist</h3>
                <p class="text-slate-300 text-sm mb-6">Powered by AI | FastAPI | Plotly | scikit-learn | XGBoost</p>
                <div class="flex flex-wrap justify-center gap-4 text-sm">
                    <span class="badge">&#9889; Real-time Analysis</span>
                    <span class="badge">&#129302; ML-Powered</span>
                    <span class="badge">&#128202; Interactive Charts</span>
                    <span class="badge">&#127760; 3D Visualizations</span>
                    <span class="badge">&#128200; Advanced Metrics</span>
                </div>
                <div class="mt-8 pt-6 border-t border-slate-600">
                    <p class="text-slate-400 text-xs">
                        This dashboard provides comprehensive machine learning insights including model performance, 
                        feature importance, confusion matrices, ROC curves, and interactive 3D visualizations.
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Add fade-in animation on scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {{ threshold: 0.1 }});
        
        document.querySelectorAll('.animate-fade-in').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            observer.observe(el);
        });
        
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
        
        // Ensure all Plotly charts are properly sized after page load
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                // Get all plotly divs
                const plotlyDivs = document.querySelectorAll('.plotly-graph-div');
                plotlyDivs.forEach(div => {{
                    if (div.id && window.Plotly) {{
                        try {{
                            window.Plotly.Plots.resize(div);
                        }} catch(e) {{
                            console.log('Could not resize plot:', div.id, e);
                        }}
                    }}
                }});
            }}, 500);
        }});
    </script>
</body>
</html>
""")
        
        # Combine all parts
        html_content = "".join(html_parts)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        update_progress(session_id, 'complete', 100, '✅ Dashboard ready!')
        
        print(f"✅ Dashboard created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.get("/api/sample-datasets")
async def get_sample_datasets():
    """Get list of available sample datasets"""
    samples = [
        {
            "id": "iris",
            "name": "Iris Flowers",
            "description": "Classic dataset with 3 flower species (150 samples, 5 features)",
            "target": "species",
            "size": "4.5 KB",
            "icon": "🌸"
        },
        {
            "id": "titanic",
            "name": "Titanic Survival",
            "description": "Passenger survival prediction (30 samples, 10 features)",
            "target": "Survived",
            "size": "2.8 KB",
            "icon": "🚢"
        },
        {
            "id": "wine_quality",
            "name": "Wine Quality",
            "description": "Wine quality classification (30 samples, 12 features)",
            "target": "quality",
            "size": "3.2 KB",
            "icon": "🍷"
        }
    ]
    return {"samples": samples}

@app.post("/api/load-sample/{sample_id}")
async def load_sample_dataset(sample_id: str):
    """Load a sample dataset"""
    try:
        sample_path = Path(__file__).parent / "sample_datasets" / f"{sample_id}.csv"
        
        if not sample_path.exists():
            return JSONResponse(status_code=404, content={"error": "Sample dataset not found"})
        
        # Read the sample file
        with open(sample_path, "rb") as f:
            contents = f.read()
        
        # Create session
        session_id = str(uuid.uuid4())
        dataset_path = TEMP_DIR / f"{session_id}_{sample_id}.csv"
        
        # Save to temp
        with open(dataset_path, "wb") as buffer:
            buffer.write(contents)
        
        # Store dataset path
        shared_data_store[f'{session_id}_dataset_path'] = str(dataset_path)
        session_conversations[session_id] = {'history': [], 'state': 'initial', 'target_column': None, 'output_type': None}
        
        # Get agent response
        response = get_agent_response(session_id, "File uploaded")
        
        return {
            "session_id": session_id,
            "message": response.get('response', ''),
            "state": response.get('state', ''),
            "analysis": response.get('analysis'),
            "sample_name": sample_id
        }
        
    except Exception as e:
        print(f"Sample load error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Failed to load sample: {str(e)}"})

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        print(f"\n{'='*60}")
        print(f"📤 UPLOAD REQUEST RECEIVED")
        print(f"{'='*60}")
        
        file_ext = Path(file.filename).suffix.lower()
        print(f"📄 File: {file.filename}")
        print(f"📋 Extension: {file_ext}")
        
        if file_ext not in ALLOWED_EXTENSIONS:
            return JSONResponse(status_code=400, content={"error": f"Invalid file type"})
        
        contents = await file.read()
        print(f"📦 File size: {len(contents)} bytes")
        
        if len(contents) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "File too large"})
        
        session_id = str(uuid.uuid4())
        dataset_path = TEMP_DIR / f"{session_id}_{file.filename}"
        
        print(f"🆔 Session ID: {session_id}")
        print(f"💾 Saving to: {dataset_path}")
        
        with open(dataset_path, "wb") as buffer:
            buffer.write(contents)
        
        print(f"✅ File saved successfully")
        
        # Store dataset path BEFORE creating session and calling get_agent_response
        shared_data_store[f'{session_id}_dataset_path'] = str(dataset_path)
        print(f"📝 Stored in shared_data_store with key: {session_id}_dataset_path")
        print(f"🔍 Checking if key exists: {f'{session_id}_dataset_path' in shared_data_store}")
        
        session_conversations[session_id] = {'history': [], 'state': 'initial', 'target_column': None, 'output_type': None}
        print(f"🎯 Session initialized with state: initial")
        
        print(f"🤖 Calling get_agent_response...")
        response = get_agent_response(session_id, "File uploaded")
        print(f"📨 Agent response: {response}")
        print(f"{'='*60}\n")
        
        return {
            "session_id": session_id,
            "message": response.get('response', ''),
            "state": response.get('state', ''),
            "analysis": response.get('analysis')
        }
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Upload failed: {str(e)}"})

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        response = get_agent_response(request.session_id, request.message)
        return response
    except Exception as e:
        print(f"Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Chat failed: {str(e)}"})

@app.post("/api/compare-models")
async def compare_models_endpoint(request: AnalysisRequest):
    """Compare multiple ML models for the given session"""
    try:
        session_id = request.session_id
        session = session_conversations.get(session_id)
        
        if not session:
            return JSONResponse(status_code=404, content={"error": "Session not found"})
        
        target_column = session.get('target_column')
        if not target_column:
            return JSONResponse(status_code=400, content={"error": "No target column set"})
        
        df = shared_data_store.get(f'{session_id}_dataframe')
        if df is None:
            return JSONResponse(status_code=404, content={"error": "Dataset not found"})
        
        # Copy dataframe and encode categorical features to numerical for modeling
        df_encoded = df.copy()
        for col in df_encoded.columns:
            if col != target_column and df_encoded[col].dtype == 'object':
                try:
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                except:
                    pass

        # Get numerical/encoded features
        numerical_features = [
            col for col in df_encoded.columns 
            if col != target_column 
            and df_encoded[col].dtype in ['int64', 'float64', 'int32']
            and 'id' not in col.lower()
        ][:15]  # Use up to 15 features
        
        if len(numerical_features) == 0:
            df_encoded['dummy_feature'] = 0
            numerical_features = ['dummy_feature']
        
        # Run model comparison
        comparison_result = compare_models(df_encoded, target_column, numerical_features, session_id)
        
        if comparison_result:
            # Store in session for later use
            session['model_comparison'] = comparison_result
            return {"success": True, "comparison": comparison_result}
        else:
            return JSONResponse(status_code=500, content={"error": "Model comparison failed"})
            
    except Exception as e:
        print(f"Model comparison error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Comparison failed: {str(e)}"})

@app.get("/api/progress/{session_id}")
async def progress_stream(session_id: str):
    """Stream progress updates via SSE"""
    async def event_generator():
        try:
            # Initialize progress
            if session_id not in progress_store:
                progress_store[session_id] = {
                    'step': 'initializing',
                    'percentage': 0,
                    'message': 'Starting...',
                    'timestamp': datetime.now().isoformat()
                }
            
            last_progress = None
            max_iterations = 300  # 30 seconds max (100ms * 300)
            iteration = 0
            
            while iteration < max_iterations:
                current_progress = progress_store.get(session_id)
                
                if current_progress and current_progress != last_progress:
                    yield {
                        "event": "progress",
                        "data": json.dumps(current_progress)
                    }
                    last_progress = current_progress
                    
                    # If complete, send final message and close
                    if current_progress.get('percentage') >= 100:
                        yield {
                            "event": "complete",
                            "data": json.dumps({"message": "Generation complete!"})
                        }
                        break
                
                await asyncio.sleep(0.1)  # Check every 100ms
                iteration += 1
            
            # Cleanup
            if session_id in progress_store:
                del progress_store[session_id]
                
        except asyncio.CancelledError:
            print(f"SSE connection closed for session {session_id}")
    
    return EventSourceResponse(event_generator())

@app.post("/api/generate")
async def generate_output(request: AnalysisRequest):
    try:
        result = generate_final_output(request.session_id)
        if result['success']:
            return FileResponse(path=result['file_path'], media_type='application/octet-stream', filename=result['filename'])
        else:
            return JSONResponse(status_code=500, content={"error": result['error']})
    except Exception as e:
        print(f"Generate error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Generation failed: {str(e)}"})

@app.post("/api/export-pdf")
async def export_dashboard_pdf(request: AnalysisRequest):
    """Export dashboard as PDF (simplified version)"""
    try:
        session_id = request.session_id
        session = session_conversations.get(session_id)
        
        if not session:
            return JSONResponse(status_code=404, content={"error": "Session not found"})
        
        # For now, return a message that PDF export is available
        # In production, you would use libraries like pdfkit, weasyprint, or playwright
        
        # Simple approach: Return the HTML file with a note
        result = generate_final_output(session_id)
        if result['success'] and result['output_type'] == 'dashboard':
            # Add a note about PDF export
            return {
                "success": True,
                "message": "Dashboard generated! Use browser's Print to PDF feature (Ctrl+P) for PDF export.",
                "file_path": result['file_path'],
                "tip": "Open the dashboard HTML file and use your browser's 'Print to PDF' option for best results."
            }
        else:
            return JSONResponse(status_code=500, content={"error": "Dashboard not generated yet"})
            
    except Exception as e:
        print(f"PDF export error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"PDF export failed: {str(e)}"})

@app.delete("/api/session/{session_id}")
async def cleanup_session(session_id: str):
    try:
        if f'{session_id}_dataset_path' in shared_data_store:
            file_path = Path(shared_data_store[f'{session_id}_dataset_path'])
            if file_path.exists():
                file_path.unlink()
        
        if session_id in session_conversations:
            del session_conversations[session_id]
        
        keys_to_remove = [k for k in shared_data_store.keys() if session_id in str(k)]
        for key in keys_to_remove:
            del shared_data_store[key]
        
        return {"status": "Session cleaned up successfully"}
    except Exception as e:
        print(f"Cleanup error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Autonomous Data Scientist API",
        "version": "2.0",
        "endpoints": {
            "upload": "POST /api/upload",
            "chat": "POST /api/chat",
            "generate": "POST /api/generate",
            "cleanup": "DELETE /api/session/{session_id}"
        }
    }

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Autonomous Data Scientist API v2.0")
    print("=" * 70)
    print(f"📡 API Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run(app, host="0.0.0.0", port=8000)